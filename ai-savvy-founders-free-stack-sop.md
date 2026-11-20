# SOP: Replace 9 Paid Apps With Free Open-Source Twins

**Brand:** AI Savvy Founders
**Source reel:** "Claude just killed v5" ($305/month stack → $0)
**Time to complete:** ~20 min per app (first one), ~10 min after that
**Goal:** Swap one paid SaaS at a time for its free, self-hosted GitHub twin without breaking your workflow.

---

## The Swap Map

| # | Paid app | Cost/mo | Free twin | What it replaces |
|---|----------|---------|-----------|------------------|
| 1 | Notion | $10 | AppFlowy | Notes, docs, wikis, local AI |
| 2 | Calendly | $10 | Cal.com | Booking links on your own domain |
| 3 | Asana | $13.49 | OpenProject | Tasks, Gantt charts, agile boards |
| 4 | Wispr Flow | $15 | OpenWhispr | Dictation into any app, offline |
| 5 | Loom | $18 | Cap | Screen recording + share links |
| 6 | ElevenLabs | $22 | VoiceStudio | Voice cloning and design, local |
| 7 | Intercom | $29 | Chatwoot | Live chat, email, WhatsApp, IG inbox |
| 8 | Higgsfield | $49 | Open Generative AI | AI images and video, 600+ models |
| 9 | Semrush | $139 | OpenSEO | Rank tracking, backlinks, site audits |
| | **Total** | **$305.49** | **$0** | **$18,329 over 5 years** |

---

## Phase 1: Audit (10 min, do once)

1. Open a spreadsheet. Columns: App, Monthly cost, Renewal date, Used weekly? (Y/N), Free twin.
2. Fill in the 9 rows from the Swap Map. Add any other tools you pay for.
3. Mark each app Y/N for "did I use this in the last 14 days?"
4. Rank by **savings x ease**. Start with the easiest: Cap, Cal.com, OpenWhispr. Save the heavy ones (Semrush, Intercom) for later.
5. Write down each renewal date. **Never cancel before you have migrated.**

## Phase 2: Pick Your Install Path (per app)

Choose one before you start:

- **Local app (easiest):** Download and install. Best for OpenWhispr, Cap, AppFlowy, VoiceStudio.
- **One-line install on a server:** Copy the Docker or install command from the repo README. Best for Chatwoot, OpenProject, Cal.com, OpenSEO.
- **Managed hosting:** Pay a small fee for someone else to host it. Only if you hit a wall.

## Phase 3: Migrate One App (repeat for each)

1. **Find the repo.** Search GitHub for the free twin's name. Check the star count, last commit date (should be recent), and open issues.
2. **Read the README.** Find the install section and system requirements.
3. **Install.** Follow the one-line install or download from the repo's Releases page.
4. **Export from the paid app.** Use its export or CSV/Markdown option. Save to a folder named `backup-[app]-[date]`.
5. **Import into the free twin.** Use its import tool, or copy over manually if the data set is small.
6. **Run both in parallel for 7 days.** Use the free twin for all new work. Keep the paid app as a safety net.
7. **Test the workflow end to end.**
   - Notion → AppFlowy: create a doc, link a page, run local AI.
   - Calendly → Cal.com: book a test slot, check Google/Outlook sync, confirm your domain `yourname.com/book` works.
   - Asana → OpenProject: create a project, add a Gantt chart, assign a task.
   - Wispr Flow → OpenWhispr: dictate into 3 different apps, test offline.
   - Loom → Cap: record, copy the share link, open it in a private window.
   - ElevenLabs → VoiceStudio: clone a voice from a short sample, generate a line.
   - Intercom → Chatwoot: send a test message from chat, email, WhatsApp, Instagram.
   - Higgsfield → Open Generative AI: generate one image and one short video.
   - Semrush → OpenSEO: run a site audit and rank check on your domain.
8. **Update links.** Replace old booking links, embeds, and widgets on your site, email signature, and bio.
9. **Cancel the paid plan** after the 7-day parallel run passes. Cancel before the renewal date.
10. **Log the savings.** Update your spreadsheet with the date cancelled and the new monthly total.

## Phase 4: Safety Checklist

- [ ] Backup of every export stored in two places
- [ ] Self-hosted tools behind HTTPS with strong passwords and 2FA
- [ ] Auto-updates or a monthly update reminder
- [ ] Weekly backup of the self-hosted database
- [ ] Team members trained and given access before you cancel the paid plan
- [ ] Any client-facing tool (booking page, chat) tested from a phone

## Phase 5: Savings Tracker

| Month | Apps cancelled | Monthly spend | Saved this month | Saved YTD |
|-------|----------------|---------------|------------------|-----------|
| 1 | | | | |

Formula: **Monthly cost x 12 = yearly savings. Monthly cost x 60 = 5-year savings.**
Example: Semrush $139 x 12 = **$1,668 a year** from one swap.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Install fails | Check the repo's Issues tab, then the README's requirements (Docker, Node, Python version). |
| Missing feature | Check the repo's roadmap. If it's critical, keep that single paid app and swap the rest. |
| Data won't import | Export as CSV or Markdown, then import in small batches. |
| Team won't switch | Run a 15-minute walkthrough and keep a one-page cheat sheet. |

## Delivery Note (for the "Comment GITHUB" CTA)

When someone comments **GITHUB**, send them:
1. All 9 repo links (paste yours here)
2. The one-line install for each
3. The paid plan it replaces
4. This SOP
