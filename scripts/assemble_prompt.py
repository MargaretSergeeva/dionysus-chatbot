#!/usr/bin/env python3
"""Dionysus prompt assembler — data-gated, platform-aware (DC2-A-95, DC2-A-84, DC2-91, DC2-122).

One set of prompt modules, three builds:
  full             — every supported module; our own stack (Dify, Plan B)
  gastbot          — modules targeted at Gastbot; linted against the Gastbot baseline
                     (conflicts always fail; duplicates fail unless the module allows them)
  gastbot_compact  — short policy version for Gastbot (DC2-A-136: short, high-level prompt);
                     same baseline lint; each module lists the modules it replaces in `covers`

Commands
  check                          validate modules + lint both builds
  build  [--target full|gastbot|gastbot_compact|all]   write prompts/dist/<target>/system_prompt.md + manifest.json
  verify                         fail if the committed prompts/dist differs from a fresh build
  report                         write prompts/dist/status_report.md

Module file = prompts/{core,blocks,adapters/*,compact}/NN_slug.md with YAML front matter:
  ---
  id: core-04-language
  label: '04'            # heading label: '04' (core) or 'BLOCK 03' (block); null = no heading
  title: LANGUAGE
  position: 40           # global order in the assembled prompt
  status: supported      # supported | partially | blocked | unknown | draft
  targets: [full]        # builds that include the module
  source: DC2-A-60 CORE 04
  deps: []               # YouTrack issues the module's data depends on
  allow_overlap: []      # Gastbot baseline builtins this module repeats on purpose
  overlap_reason: ''     # required when allow_overlap is set
  covers: []             # compact modules only: codes of the modules they replace (C05, B03, A02a)
  ---
Target-specific text inside a module:
  <!-- only:gastbot --> ... <!-- /only -->
  <!-- only:full --> ... <!-- /only -->
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PROMPTS = ROOT / "prompts"
MODULE_DIRS = ("core", "blocks", "adapters/gastbot", "adapters/dify", "compact")
TARGETS = ("full", "gastbot", "gastbot_compact")
STATUSES = {"supported", "partially", "blocked", "unknown", "draft"}
ONLY_RE = re.compile(r"<!--\s*only:(\w+)\s*-->(.*?)<!--\s*/only\s*-->", re.S)
REF_RE = re.compile(r"(Block )?§(\d{2})")


class AssemblyError(Exception):
    """Invalid module set or a build that breaks a gate rule."""


@dataclass
class Module:
    path: Path
    id: str
    label: str | None
    title: str | None
    position: int
    status: str
    targets: list[str]
    source: str
    body: str
    deps: list[str] = field(default_factory=list)
    allow_overlap: list[str] = field(default_factory=list)
    overlap_reason: str = ""
    covers: list[str] = field(default_factory=list)

    def render(self, target: str) -> str:
        def keep(match: re.Match) -> str:
            return match.group(2).strip("\n") if match.group(1) == target else ""

        text = re.sub(r"\n{3,}", "\n\n", ONLY_RE.sub(keep, self.body)).strip()
        if self.label is None:
            return text
        return f"#### {self.label}. {self.title}\n\n{text}"


def load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_module(path: Path) -> Module:
    raw = path.read_text(encoding="utf-8")
    if not raw.startswith("---\n"):
        raise AssemblyError(f"{path}: missing front matter")
    _, front, body = raw.split("---\n", 2)
    meta = yaml.safe_load(front)
    module = Module(
        path=path,
        id=meta["id"],
        label=meta["label"],
        title=meta["title"],
        position=int(meta["position"]),
        status=meta["status"],
        targets=list(meta["targets"]),
        source=meta["source"],
        body=body.strip("\n"),
        deps=list(meta.get("deps") or []),
        allow_overlap=list(meta.get("allow_overlap") or []),
        overlap_reason=meta.get("overlap_reason") or "",
        covers=list(meta.get("covers") or []),
    )
    if module.status not in STATUSES:
        raise AssemblyError(f"{path}: status '{module.status}' not in {sorted(STATUSES)}")
    unknown_targets = set(module.targets) - set(TARGETS)
    if unknown_targets:
        raise AssemblyError(f"{path}: unknown targets {sorted(unknown_targets)}")
    if module.allow_overlap and not module.overlap_reason:
        raise AssemblyError(f"{path}: allow_overlap set without overlap_reason")
    markers = re.findall(r"<!--\s*only:(\w+)", module.body)
    if len(markers) != len(re.findall(r"<!--\s*/only\s*-->", module.body)):
        raise AssemblyError(f"{path}: unbalanced only-markers")
    for marker in markers:
        if marker not in TARGETS:
            raise AssemblyError(f"{path}: unknown target marker 'only:{marker}'")
    return module


def load_modules() -> list[Module]:
    modules = [parse_module(path=p) for d in MODULE_DIRS for p in sorted((PROMPTS / d).glob("*.md"))]
    if not modules:
        raise AssemblyError(f"no modules under {PROMPTS}")
    ids = [m.id for m in modules]
    duplicates = sorted({i for i in ids if ids.count(i) > 1})
    if duplicates:
        raise AssemblyError(f"duplicate module ids: {duplicates}")
    positions = [m.position for m in modules]
    clashes = sorted({p for p in positions if positions.count(p) > 1})
    if clashes:
        raise AssemblyError(f"duplicate positions: {clashes}")
    return sorted(modules, key=lambda m: m.position)


def select(modules: list[Module], target: str, gate: dict) -> list[Module]:
    merge = set(gate["merge_statuses"])
    return [m for m in modules if target in m.targets and m.status in merge]


def lint_baseline(modules: list[Module], target: str, baseline: dict) -> list[str]:
    errors = []
    for m in modules:
        text = m.render(target=target)
        for kind in ("builtins", "conflicts"):
            for key, spec in baseline[kind].items():
                hit = next((re.search(p, text, re.I) for p in spec["patterns"] if re.search(p, text, re.I)), None)
                if hit is None:
                    continue
                snippet = text[max(0, hit.start() - 20): hit.end() + 20].replace("\n", " ")
                if kind == "conflicts":
                    errors.append(f"{m.path.name}: CONFLICTS with {target} '{key}' ({spec['description']}) → …{snippet}…")
                elif key not in m.allow_overlap:
                    errors.append(f"{m.path.name}: DUPLICATES {target} builtin '{key}' ({spec['description']}) → …{snippet}…")
    return errors


def lint_platform_variables(modules: list[Module], target: str, variables: list[str]) -> list[str]:
    errors = []
    for m in modules:
        text = m.render(target=target)
        for var in variables:
            if re.search(rf"\b{re.escape(var)}\b", text):
                errors.append(f"{m.path.name}: platform variable '{var}' in the {target} build (wrap it in <!-- only:gastbot -->)")
    return errors


def lint_references(modules: list[Module], target: str) -> list[str]:
    labels = {m.label for m in modules if m.label}
    errors = []
    for m in modules:
        for match in REF_RE.finditer(m.render(target=target)):
            ref = f"BLOCK {match.group(2)}" if match.group(1) else match.group(2)
            if ref not in labels:
                errors.append(f"{m.path.name}: references §{ref} which is not in the {target} build")
    return errors


def run_check(gate: dict, baseline: dict) -> list[Module]:
    modules = load_modules()
    errors = []
    for target in TARGETS:
        included = select(modules=modules, target=target, gate=gate)
        errors += lint_references(modules=included, target=target)
        if gate["targets"][target]["lint_baseline"]:
            errors += lint_baseline(modules=included, target=target, baseline=baseline)
        else:
            errors += lint_platform_variables(modules=included, target=target, variables=baseline["variables"])
    if errors:
        raise AssemblyError("gate check failed:\n" + "\n".join(f"  {e}" for e in errors))
    return modules


def render_build(modules: list[Module], target: str, gate: dict, version: str) -> tuple[str, dict]:
    included = select(modules=modules, target=target, gate=gate)
    prompt = "\n\n---\n\n".join(m.render(target=target) for m in included) + "\n"
    manifest = {
        "target": target,
        "version": version,
        "chars": len(prompt),
        "included": [{"id": m.id, "status": m.status, "source": m.source} for m in included],
        "held_out": [{"id": m.id, "status": m.status, "targets": m.targets, "deps": m.deps}
                     for m in modules if m not in included],
    }
    return prompt, manifest


def build_outputs(gate: dict, baseline: dict, targets: tuple[str, ...]) -> dict[Path, str]:
    modules = run_check(gate=gate, baseline=baseline)
    version = (PROMPTS / "VERSION").read_text(encoding="utf-8").strip()
    outputs = {}
    for target in targets:
        prompt, manifest = render_build(modules=modules, target=target, gate=gate, version=version)
        out_dir = PROMPTS / "dist" / target
        outputs[out_dir / "system_prompt.md"] = prompt
        outputs[out_dir / "manifest.json"] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    outputs[PROMPTS / "dist" / "status_report.md"] = render_report(modules=modules, gate=gate, version=version)
    return outputs


def render_report(modules: list[Module], gate: dict, version: str) -> str:
    included = {t: {m.id for m in select(modules=modules, target=t, gate=gate)} for t in TARGETS}
    lines = [f"# Prompt module status — {version}", "",
             "Generated by `scripts/assemble_prompt.py report`. Do not edit by hand.", "",
             "| Pos | Module | Status | Source | Deps | full | gastbot | gastbot_compact |",
             "|---|---|---|---|---|---|---|---|"]
    for m in modules:
        name = f"{m.label}. {m.title}" if m.label else m.id
        marks = ["✅" if m.id in included[t] else "—" for t in TARGETS]
        lines.append(f"| {m.position} | {name} | {m.status} | {m.source} | {', '.join(m.deps) or '—'} | {' | '.join(marks)} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
    build = sub.add_parser("build")
    build.add_argument("--target", choices=[*TARGETS, "all"], default="all")
    sub.add_parser("verify")
    sub.add_parser("report")
    args = parser.parse_args()

    gate = load_yaml(path=PROMPTS / "gate.yaml")
    baseline = load_yaml(path=PROMPTS / "platform" / "gastbot_baseline.yaml")

    if args.cmd == "check":
        modules = run_check(gate=gate, baseline=baseline)
        for target in TARGETS:
            print(f"{target}: {len(select(modules=modules, target=target, gate=gate))} modules")
        print("gate check passed")
        return 0

    if args.cmd == "report":
        modules = run_check(gate=gate, baseline=baseline)
        version = (PROMPTS / "VERSION").read_text(encoding="utf-8").strip()
        path = PROMPTS / "dist" / "status_report.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render_report(modules=modules, gate=gate, version=version), encoding="utf-8")
        print(f"→ {path.relative_to(ROOT)}")
        return 0

    targets = TARGETS if args.cmd == "verify" or args.target == "all" else (args.target,)
    outputs = build_outputs(gate=gate, baseline=baseline, targets=targets)

    if args.cmd == "verify":
        stale = [p for p, content in outputs.items()
                 if not p.exists() or p.read_text(encoding="utf-8") != content]
        if stale:
            raise AssemblyError("prompts/dist is stale — run `python scripts/assemble_prompt.py build`:\n"
                                + "\n".join(f"  {p.relative_to(ROOT)}" for p in stale))
        print("prompts/dist is up to date")
        return 0

    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"→ {path.relative_to(ROOT)} ({len(content)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
