#!/usr/bin/env python3
"""Dionysus prompt assembler — data-gated, platform-aware (DC2-A-95, DC2-A-84, DC2-91, DC2-122).

One set of prompt modules, two builds:
  full             — every supported module; our own stack (Dify, Plan B)
  gastbot          — modules targeted at Gastbot; linted against the Gastbot baseline
                     (conflicts always fail; duplicates fail unless the module allows them)

Commands
  check                          validate modules + lint both builds
  build  [--target full|gastbot|all]   write prompts/dist/<target>/system_prompt.md + manifest.json
  verify                         fail if the committed prompts/dist differs from a fresh build
  report                         write prompts/dist/status_report.md

Module file = prompts/{core,blocks,adapters/*}/NN_slug.md with YAML front matter:
  ---
  id: core-04-language
  label: '04'            # heading label: '04' (core) or 'BLOCK 03' (block); null = no heading
  title: LANGUAGE
  position: 40           # global order in the assembled prompt
  status: supported      # supported | partially | blocked | unknown | draft
  source: DC2-A-60 CORE 04
  deps: []               # YouTrack issues the module's data depends on
  gastbot_covers:        # only if Gastbot already does this (prompts/platform/gastbot_baseline.yaml)
    relation: conflict   # conflict (Gastbot does it differently) | duplicate (Gastbot does the same) — both: never in gastbot
    builtins: []         # baseline keys the text repeats
    reason: ''
A module enters a build when all its `data` reaches the build (data_sources.yaml) and
Gastbot does not cover it.
  data: [wines]          # data sources from prompts/data_sources.yaml, or `data: general`
  data_note: ''          # optional: data gaps worth knowing
  requirements: [FR-04]  # IDs from prompts/requirements.yaml (at least one)
  fields: [wines_enriched.jahrgang]  # Supabase table.field this module uses (metadata only; required when data is a table/view/function)
  ---
No build-specific text inside a module: split it instead (only-markers are rejected).
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
MODULE_DIRS = ("core", "blocks", "adapters/gastbot", "adapters/dify")
TARGETS = ("full", "gastbot")
STATUSES = {"supported", "partially", "blocked", "unknown", "draft"}
REF_RE = re.compile(r"(Block )?§(\d{2}[a-z]?)")  # §10, §10c, Block §06b


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
    source: str
    body: str
    deps: list[str] = field(default_factory=list)
    gastbot_covers: dict = field(default_factory=dict)
    targets: list[str] = field(default_factory=list)          # derived, never written by hand
    excluded: dict[str, str] = field(default_factory=dict)    # build -> reason it is left out
    covers: list[str] = field(default_factory=list)
    data: list[str] = field(default_factory=list)   # [] = general (needs no data)
    data_note: str = ""
    requirements: list[str] = field(default_factory=list)
    fields: list[str] = field(default_factory=list)   # table.field in Supabase (metadata, not prompt text)

    def render(self, target: str) -> str:
        text = self.body.strip()
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
        source=meta["source"],
        body=body.strip("\n"),
        deps=list(meta.get("deps") or []),
        gastbot_covers=parse_gastbot_covers(path=path, value=meta.get("gastbot_covers")),
        covers=list(meta.get("covers") or []),
        data=parse_data(path=path, value=meta.get("data")),
        data_note=meta.get("data_note") or "",
        requirements=list(meta.get("requirements") or []),
        fields=list(meta.get("fields") or []),
    )
    if module.status not in STATUSES:
        raise AssemblyError(f"{path}: status '{module.status}' not in {sorted(STATUSES)}")
    retired = {"targets", "allow_overlap", "overlap_reason"} & set(meta)
    if retired:
        raise AssemblyError(f"{path}: {sorted(retired)} retired (DC2-142) — builds come from `data` and `gastbot_covers`")
    if re.search(r"<!--\s*/?only", module.body):
        raise AssemblyError(f"{path}: only-markers retired (DC2-142) — split the module so each one is fully in or out of a build")
    return module


def parse_gastbot_covers(path: Path, value) -> dict:
    if not value:
        return {}
    if value.get("relation") not in {"conflict", "duplicate"} or not value.get("reason"):
        raise AssemblyError(f"{path}: gastbot_covers needs relation (conflict|duplicate) and reason")
    return {"relation": value["relation"], "builtins": list(value.get("builtins") or []),
            "reason": value["reason"]}


def derive_targets(modules: list[Module], registry: dict) -> None:
    """A module enters a build when all its data reaches the build and Gastbot does not cover it."""
    sources = registry["sources"]
    for m in modules:
        candidates = list(TARGETS)
        for build in candidates:
            missing = [d for d in m.data if build not in sources.get(d, {}).get("builds", [])]
            cov = m.gastbot_covers
            if missing:
                m.excluded[build] = "data not available: " + ", ".join(missing)
            elif build != "full" and cov:
                m.excluded[build] = f"platform-covered ({cov['relation']}): {cov['reason']}"
            else:
                m.targets.append(build)


def parse_data(path: Path, value) -> list[str]:
    if value == "general":
        return []
    if not value or not isinstance(value, list):
        raise AssemblyError(f"{path}: `data` missing — list the data sources from prompts/data_sources.yaml or write `data: general`")
    return list(value)


def lint_requirements(modules: list[Module], catalog: dict) -> list[str]:
    known = catalog["requirements"]
    errors = [f"{m.path.name}: `requirements` missing — list IDs from prompts/requirements.yaml"
              for m in modules if not m.requirements]
    errors += [f"{m.path.name}: requirement '{r}' is not in prompts/requirements.yaml"
               for m in modules for r in m.requirements if r not in known]
    return errors


def lint_data(modules: list[Module], registry: dict) -> list[str]:
    sources = registry["sources"]
    errors = [f"{m.path.name}: data source '{d}' is not in prompts/data_sources.yaml"
              for m in modules for d in m.data if d not in sources]
    tables = {name for name, s in sources.items() if s.get("kind") in ("table", "view")}
    for m in modules:
        if m.data and any(d in tables or sources.get(d, {}).get("kind") == "function" for d in m.data) and not m.fields:
            errors.append(f"{m.path.name}: `fields` missing — list the Supabase fields (table.field) this module uses")
        for f in m.fields:
            table, _, col = f.partition(".")
            if table not in tables:
                errors.append(f"{m.path.name}: field '{f}' — '{table}' is not a table/view in prompts/data_sources.yaml")
            elif col not in sources[table].get("fields", []):
                errors.append(f"{m.path.name}: field '{f}' is not listed for {table} in prompts/data_sources.yaml")
    return errors


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
                elif key not in m.gastbot_covers.get("builtins", []):
                    errors.append(f"{m.path.name}: DUPLICATES {target} builtin '{key}' ({spec['description']}) → …{snippet}… (declare it in gastbot_covers)")
    return errors


def lint_platform_variables(modules: list[Module], target: str, variables: list[str]) -> list[str]:
    errors = []
    for m in modules:
        text = m.render(target=target)
        for var in variables:
            if re.search(rf"\b{re.escape(var)}\b", text):
                errors.append(f"{m.path.name}: platform variable '{var}' in the {target} build (add the data source gastbot_variables)")
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
    registry = load_yaml(path=PROMPTS / "data_sources.yaml")
    errors = lint_data(modules=modules, registry=registry)
    errors += lint_requirements(modules=modules, catalog=load_yaml(path=PROMPTS / "requirements.yaml"))
    if not errors:
        derive_targets(modules=modules, registry=registry)
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
        "held_out": [{"id": m.id, "status": m.status,
                      "reason": m.excluded.get(target) or "status not merged",
                      "deps": m.deps}
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
             "| Pos | Supabase fields | Module | Status | Requirements | Data | Source | Deps | full | gastbot |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for m in modules:
        name = f"{m.label}. {m.title}" if m.label else m.id
        marks = ["✅" if m.id in included[t] else ("⛔ " + m.excluded[t] if t in m.excluded else "—") for t in TARGETS]
        data = ", ".join(f"`{d}`" for d in m.data) or "general"
        by_table: dict[str, list[str]] = {}
        for f in m.fields:
            t, _, col = f.partition(".")
            by_table.setdefault(t, []).append(col)
        fields = "<br>".join(f"`{t}`: {', '.join(cols)}" for t, cols in by_table.items()) or "—"
        lines.append(f"| {m.position} | {fields} | {name} | {m.status} | {', '.join(m.requirements)} | {data} | {m.source} | {', '.join(m.deps) or '—'} | {' | '.join(marks)} |")
    catalog = load_yaml(path=PROMPTS / "requirements.yaml")["requirements"]
    lines += ["", "## Requirement → modules", "",
              "| ID | Requirement | Modules | full | gastbot |", "|---|---|---|---|---|"]
    for rid, req in catalog.items():
        covering = [m for m in modules if rid in m.requirements]
        names = ", ".join(m.label or m.id for m in covering)
        if not covering:
            names = "— (met outside the prompt)" if req.get("prompt") is False else "⚠️ no module yet"
        marks = ["✅" if any(m.id in included[t] for m in covering) else "—" for t in TARGETS]
        lines.append(f"| {rid} | {req['title']} | {names} | {' | '.join(marks)} |")
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
