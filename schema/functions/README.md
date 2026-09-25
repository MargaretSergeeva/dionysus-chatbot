# Retrieval functions

Postgres functions deployed to Supabase (source of truth here; applied via
`mcp__Supabase__apply_migration`, not run manually against prod). Routing
logic for when the bot/Dify workflow should call which one: **DC2-A-96**.

| Function | Kind | Ticket | Use for |
|---|---|---|---|
| `match_rheingau_chunks` | pure semantic (RAG) | DC2-119 | Open-ended / descriptive questions |
| `filter_rheingau_pages` | pure structured filter | DC2-131, DC2-132 | List/filter questions over amenity flags, category & city — needs a complete, exact result set |
| `match_rheingau_chunks_filtered` | hybrid (filter + semantic) | DC2-131, DC2-132 | Combined questions ("a nice pet-friendly hotel in Rüdesheim") |

All three are called from Dify as RPC/HTTP tools against the Supabase
PostgREST endpoint (`/rest/v1/rpc/<function_name>`), not embedded as
application code — there is no separate retrieval backend in this repo.

`filter_rheingau_pages` and `match_rheingau_chunks_filtered` follow the same
nullable-boolean rule as the `rheingau_pages` amenity columns themselves
(see DC2-A-125): a boolean parameter left as its default `NULL` is not
filtered on at all; passing `true` or `false` only ever matches rows with a
*confirmed* value, never a row where the underlying flag is `NULL`
(unknown). Never pass `false` to mean "I don't care" — that would wrongly
exclude every unconfirmed row.

`p_city` follows the same NULL-means-unfiltered rule and expects the
*canonical* value in `rheingau_pages.city` (see `../data/plz_city_map.sql`,
DC2-132) — e.g. `"Eltville-Erbach"`, not free text and not the raw
`cities` column, which mixes real towns with the "Rheingau" region tag.
