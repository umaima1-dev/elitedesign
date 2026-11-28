# Repository audit

Status of every upstream repository. **All are `not audited`.** Update a row only after cloning and reading the repo.

## Checklist per repo

- [ ] Last commit date and maintenance activity
- [ ] License allows reuse
- [ ] Contains executable code, or only prompt text
- [ ] API keys and paid dependencies
- [ ] Works on Windows
- [ ] Uses the current Claude Code `SKILL.md` format
- [ ] Integrations respect `shared/workflows/approval-gate.md`

## Tracker

| Repo | Feeds agent(s) | Decision | Audit |
|---|---|---|---|
| social-media-skills/skills | brain-keeper, content-strategist, hook-writer, repurposer, stories-writer | Primary foundation: cherry-pick skills | not audited |
| shika-stuck/viral-analyzer | outlier-scout, analyst | Study scraping and scoring | not audited |
| thejmvai/claude-viral-radar | hook-analyst | Study hook analysis | not audited |
| zayd28061-hub/viral-content-skill | content-strategist, competitor-research | Study strategy output | not audited |
| Ootto-AI/claude-content-skills | scriptwriter, hook-writer | Study script and caption flow | not audited |
| Ootto-AI/claude-virality-skill | hook-analyst | Optional: retention patterns | not audited |
| MuhammadaliNazarov/claude-video-skills | hook-writer, scriptwriter | Study hook frameworks | not audited |
| jdjf39/video-creator-skills | video-editor | Primary for video | not audited |
| social-media-skills/instagram-carousel-skill | carousel-designer | Compare with installed carousel skills | not audited |
| cth9191/carousel-engine | carousel-designer | Study cold-reader review | not audited |
| tenfoldmarc/carousel-suite-skill | carousel-designer | Optional | not audited |
| michaellady/claude-social-media-skills | scheduler, performance-tracker | Primary for Buffer | not audited |
| AleemHaider/manychat-mcp | conversion-builder | Primary MCP | not audited |
| Bynor-S-R-L/bynor-mcp | engagement-assistant, performance-tracker | Optional | not audited |
| jsath/claude-skills | brain-keeper, repurposer | Voice learning | not audited |
| kkoppenhaver/cc-skills | brain-keeper, content-strategist | Editing, fact-check | not audited |
| Melvynx/video-agent-skills | video-editor | Alternative | not audited |
| w-avw/instagram-viral-reels-research-claude-skill | outlier-scout | Study 5x logic | not audited |

## Blueprint

**Reuse (skills already installed in this Claude workspace or adopt as is):** carousel-designer, repurposer, competitor-research.

**Modify (start from upstream, adapt to Business Brain and gate):** brain-keeper, outlier-scout, hook-analyst, content-strategist, hook-writer, scriptwriter, video-editor, scheduler, engagement-assistant, performance-tracker, analyst.

**Build from scratch:** stories-writer, conversion-builder (design logic), trending-audio source.

**MCP to connect:** Apify, Buffer, ManyChat.

**Do not install in parallel (overlap):** Publora, Quegly, Schedulala, Social Neuron, Socialync, the other seven carousel repos, and the other video-editing collections beyond one chosen primary. Pick one per job.
