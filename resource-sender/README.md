# Resource Sender

One page, three fields (contact email, resource name, resource link). It finds
or creates the contact in GoHighLevel and sends the standard email from your
GoHighLevel account, so it shows up in their conversation history.

## One-time setup (about 10 minutes)

1. **GoHighLevel token:** Settings > Private Integrations > Create new.
   Scopes: `contacts.write`, `contacts.readonly`, `conversations/message.write`.
   Copy the token.
2. **Location ID:** Settings > Business Profile (the sub-account id).
3. **Deploy** (free Cloudflare account):
   ```bash
   cd resource-sender
   npx wrangler deploy
   npx wrangler secret put GHL_TOKEN
   npx wrangler secret put GHL_LOCATION_ID
   npx wrangler secret put APP_PASSWORD
   ```
   Optional sender: `npx wrangler secret put FROM_EMAIL` (and `FROM_NAME`).
4. Open the URL Wrangler prints, enter the password once (the browser remembers it).

Change the email wording in `buildEmail()` at the top of `worker.js`.
