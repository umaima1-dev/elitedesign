// Reusable email template. Edit the settings below; no other code needs to change.
export const EMAIL = {
  brand: "AI Savvy Founders",
  signOff: "Umaima",
  greeting: "Hey there,",
  intro: "Here is the resource as promised. Tap the button below to open it.",
  introPlain: "Here is the resource as promised. Your link is below.",
  button: "Open the resource",
  outro: "Hope it helps. Just reply to this email if you have any questions.",
  accent: "#b4451f", // button + top bar
  ink: "#1c1a17", // text
  paper: "#f6f4ef", // page background
};

const esc = (s) =>
  String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

export function buildEmail(link, resourceName) {
  const e = EMAIL;
  const url = esc(link);
  const title = esc(resourceName);

  const text = [
    e.greeting,
    "",
    e.introPlain,
    "",
    `${resourceName}: ${link}`,
    "",
    e.outro,
    "",
    `${e.signOff}`,
    e.brand,
  ].join("\n");

  const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"></head>
<body style="margin:0;padding:0;background:${e.paper};">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">${title}: your resource is inside.</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:${e.paper};padding:28px 12px;">
<tr><td align="center">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="max-width:560px;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e4dfd5;">
    <tr><td style="background:${e.accent};height:6px;font-size:0;line-height:0;">&nbsp;</td></tr>
    <tr><td style="padding:32px 32px 8px;font-family:Arial,Helvetica,sans-serif;color:${e.ink};">
      <div style="font-size:12px;letter-spacing:1.5px;text-transform:uppercase;color:${e.accent};font-weight:700;">${esc(e.brand)}</div>
      <h1 style="margin:10px 0 0;font-size:24px;line-height:1.25;color:${e.ink};">${title}</h1>
    </td></tr>
    <tr><td style="padding:16px 32px 0;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.6;color:${e.ink};">
      <p style="margin:0 0 14px;">${esc(e.greeting)}</p>
      <p style="margin:0;">${esc(e.intro)}</p>
    </td></tr>
    <tr><td align="left" style="padding:24px 32px;">
      <a href="${url}" style="display:inline-block;background:${e.accent};color:#ffffff;font-family:Arial,Helvetica,sans-serif;font-size:16px;font-weight:700;text-decoration:none;padding:14px 28px;border-radius:8px;">${esc(e.button)}</a>
    </td></tr>
    <tr><td style="padding:0 32px;font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.5;color:#6b665e;">
      Button not working? Copy this link into your browser:<br>
      <a href="${url}" style="color:${e.accent};word-break:break-all;">${url}</a>
    </td></tr>
    <tr><td style="padding:24px 32px 32px;font-family:Arial,Helvetica,sans-serif;font-size:16px;line-height:1.6;color:${e.ink};">
      <p style="margin:0 0 14px;">${esc(e.outro)}</p>
      <p style="margin:0;">${esc(e.signOff)}<br><span style="color:#6b665e;font-size:14px;">${esc(e.brand)}</span></p>
    </td></tr>
  </table>
</td></tr></table>
</body></html>`;

  return { text, html };
}
