# Approval gate

**Rule: no agent publishes, sends email, or messages a lead without an approval record. This holds whatever the underlying tool allows.**

## How it works

1. Agent finishes an asset and gets a Brain Keeper PASS.
2. Agent runs `python scripts/approve.py request <asset> --action <publish|message> --destination "<where>"`. This writes `approvals/<id>.json` with status `pending` and the SHA-256 of the asset.
3. A human reviews the asset and runs `python scripts/approve.py approve <id> --by "<name>"`.
4. Before any external action, the agent runs `python scripts/approve.py check <asset> --action <action>`. Exit code 0 means approved and unchanged. Anything else means stop.
5. If the asset is edited after approval its hash changes and the approval is void. Request again.

## Which agents are gated

| Agent | Gate |
|---|---|
| scheduler | publish |
| engagement-assistant | outbound-message (draft only, human sends) |
| conversion-builder | outbound-message |

All other agents produce files only.
