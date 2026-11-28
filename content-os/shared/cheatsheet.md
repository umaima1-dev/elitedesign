# Content OS cheat sheet

Type `/content-os` and say what you want in plain words. It picks the right agent. Or call an agent directly with its command.

## How it works in one minute

- **Skills** are instructions Claude follows. **Agents** are skills with one job, one input and one output file.
- Work flows left to right, and results loop back: **Research, Plan, Create, Distribute, Convert, Measure**.
- Every agent reads your brand files in `business-brain/` and writes its result as a file in its department folder.
- Anything that goes out to the world (publishing, messages) waits for your approval.

## Commands

| Command | What it does | Try saying | Output |
|---|---|---|---|
| `/content-os` | Main entry. Routes any request to the right agent | "Plan my week" | depends |
| `/setup-content-os` | Set up or change your brand profile | "Update my offers" | `config.json`, `business-brain/` |
| `/content-os-brain-keeper` | Builds your brand files and checks any content against them | "Check this caption against my brand" | verdict PASS / FIX / BLOCK |
| `/content-os-outlier-scout` | Finds posts that beat a creator's normal results | "Find outlier posts from my watchlist" | `research/outliers/` |
| `/content-os-hook-analyst` | Explains why top posts worked: hook, structure, visuals | "Break down these outliers" | `research/hooks/`, `research/hook-bank.md` |
| `/content-os-competitor-research` | Competitor teardown and gaps you can own | "What are my competitors missing?" | `research/competitors/` |
| `/content-os-content-strategist` | Builds the weekly plan | "Plan next week" | `planning/weekly/` |
| `/content-os-hook-writer` | Ranked hook options for a post | "Give me hooks for post 2" | hooks list |
| `/content-os-scriptwriter` | Short-form video script, shot list, caption | "Script the Monday reel" | `studio/scripts/` |
| `/content-os-carousel-designer` | Carousel copy and slides | "Make a carousel on topic X" | `studio/carousels/` |
| `/content-os-video-editor` | Edits raw footage: cuts, captions, reframing | "Edit this video" (needs FFmpeg) | `studio/videos/` |
| `/content-os-repurposer` | Adapts one piece for other platforms | "Turn this reel into a LinkedIn post" | `distribution/repurposed/` |
| `/content-os-scheduler` | Queues approved posts in your publishing tool | "Schedule this week's posts" | queue log. **Needs approval** |
| `/content-os-stories-writer` | Daily Stories sequence | "Stories for today" | `distribution/stories/` |
| `/content-os-engagement-assistant` | Sorts comments and DMs, flags leads, drafts replies. You send them | "Triage today's comments" | `distribution/engagement/` |
| `/content-os-conversion-builder` | Freebie, keyword, DM flow and welcome email for a post | "Build the funnel for the Tuesday post" | `conversion/funnels/`. **Needs approval** |
| `/content-os-performance-tracker` | Collects post metrics into one table | "Pull this week's numbers" | `analytics/data/performance.csv` |
| `/content-os-analyst` | Finds what works and tells Research and Planning | "What should I do more of?" | `analytics/reports/` |

## A normal week

| Day | Say |
|---|---|
| Sunday | "Find what is working in my niche" then "Analyse my results" |
| Monday | "Plan my week" and approve it |
| Tue to Thu | "Write the scripts", "Make the carousels", "Build the funnels" |
| Daily | "Stories for today", "Triage my comments" |
| Friday | "Schedule the approved posts", "Pull this week's numbers" |

## Approval rule

Nothing is published, emailed or sent until you approve it. Scheduler and Conversion Builder check this before they act. Engagement Assistant only drafts replies.

## Where things are

`config.json` your settings, `business-brain/` your brand, `research/` `planning/` `studio/` `distribution/` `conversion/` `analytics/` the work. Change a setting anytime with `/setup-content-os`.

## If a command does not show up

Desktop app: open the `content-os` folder as a project. Web app: start the session on the repo. You can always just type `/content-os` and ask in plain words, or ask Claude to read `shared/cheatsheet.md`.
