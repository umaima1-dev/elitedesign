# Integrations

Skills tell an agent how to do a task. They do not grant API access, data, scheduling or permissions. Each integration below must be connected and tested before the agent that depends on it is trusted.

| Integration | Used by | What it provides | Status | Verify before use |
|---|---|---|---|---|
| Apify | outlier-scout, hook-analyst, competitor-research | Instagram/LinkedIn scraping into JSON | Available as an MCP connector in this workspace | Actor cost per run, platform terms of service |
| Buffer | scheduler, performance-tracker | Queue and schedule posts, stats | Needs credentials | Current API availability and access rules for your account. Study `michaellady/claude-social-media-skills` |
| ManyChat MCP | conversion-builder, performance-tracker | Subscribers, tags, fields, flow triggers | Needs API key | Pro plan requirement, flow-creation limits. Study `AleemHaider/manychat-mcp` |
| FFmpeg + transcription | video-editor, hook-analyst | Cuts, captions, reframing, transcripts | Local install | Windows paths, whisper model download |
| Inbox (read-only) | engagement-assistant | Comments and DMs for triage | Needs a source | Read-only scope. Replies are sent by a human |
| Trending audio source | (none yet) | Live trending audio feed | **Not solved.** No audited repo provides it | Needs a dedicated data source |

## Alternatives, not replacements

Publora, Quegly, Schedulala, Social Neuron, Bynor and Zernio can publish or report analytics. Buffer stays the publishing destination. Use these only as references, or as a fallback if Buffer access is blocked.

## Setup notes

Keep credentials in environment variables or the connector settings. Never commit keys. `.gitignore` excludes `.env`.
