# Resource Sender (Next.js)

Type a contact email, a resource name and a resource link. The app finds or
creates the contact in GoHighLevel and sends the standard email from your
GoHighLevel account, so it appears in their conversation history.

Email: branded layout with the resource name as the title, "Here is the resource as promised", and a button linking to the resource.
Subject: the resource name you type.

## 1. Get your GoHighLevel details
- **Token:** Settings > Private Integrations > Create new. Scopes:
  `contacts.write`, `contacts.readonly`, `conversations/message.write`.
- **Location ID:** Settings > Business Profile.

## 2. Run locally
```bash
npm install
cp .env.example .env.local   # then fill in the values
npm run dev
```
Open http://localhost:3000

## 3. Deploy on Vercel (free)
1. Push this folder to a GitHub repo (or run `npx vercel` in this folder).
2. In Vercel > Project > Settings > Environment Variables add:
   `GHL_TOKEN`, `GHL_LOCATION_ID`, `APP_PASSWORD` (and optional `FROM_EMAIL`, `FROM_NAME`).
3. Deploy, open the URL, bookmark it. The browser remembers your password.

## Change the email wording
Edit the settings at the top of `app/email-template.js` (greeting, intro, button text, follow line, custom-solutions line, sign-off, colours).
