// Resource Sender: type an email, a resource name and a link, and it sends
// the standard "here is the resource" email through GoHighLevel.
// Secrets (set in Cloudflare, never in this file):
//   GHL_TOKEN        GoHighLevel Private Integration token
//   GHL_LOCATION_ID  your sub-account (location) id
//   APP_PASSWORD     password you type into the page
// Optional: FROM_EMAIL, FROM_NAME

const GHL = "https://services.leadconnectorhq.com";

// ---- Edit the email wording here ------------------------------------------
const buildEmail = (link) => ({
  text: `Here is the resource as promised.\n\n${link}`,
  html: `<p>Here is the resource as promised.</p><p><a href="${esc(link)}">${esc(link)}</a></p>`,
});
// ----------------------------------------------------------------------------

const esc = (s) =>
  String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "content-type": "application/json" } });

async function ghl(env, path, body) {
  const res = await fetch(GHL + path, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.GHL_TOKEN}`,
      Version: "2021-07-28",
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.message || `GoHighLevel error ${res.status}`);
  return data;
}

async function send(request, env) {
  const { password, email, subject, link } = await request.json().catch(() => ({}));
  if (!env.APP_PASSWORD || password !== env.APP_PASSWORD) return json({ error: "Wrong password" }, 401);

  const to = String(email || "").trim().toLowerCase();
  const subj = String(subject || "").trim();
  const url = String(link || "").trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(to)) return json({ error: "Enter a valid email address" }, 400);
  if (!subj) return json({ error: "Enter the resource name (it becomes the subject)" }, 400);
  if (!/^https?:\/\/\S+$/i.test(url)) return json({ error: "Enter the full resource link starting with https://" }, 400);

  try {
    // Finds the contact by email, or creates it if they are new.
    const up = await ghl(env, "/contacts/upsert", { locationId: env.GHL_LOCATION_ID, email: to });
    const contactId = up.contact && up.contact.id;
    if (!contactId) throw new Error("Could not find or create the contact");

    const { text, html } = buildEmail(url);
    const msg = { type: "Email", contactId, subject: subj, message: text, html };
    if (env.FROM_EMAIL) msg.emailFrom = env.FROM_NAME ? `${env.FROM_NAME} <${env.FROM_EMAIL}>` : env.FROM_EMAIL;
    await ghl(env, "/conversations/messages", msg);
    return json({ ok: true, new: !!up.new });
  } catch (e) {
    return json({ error: e.message }, 502);
  }
}

const PAGE = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Resource Sender</title>
<style>
:root{--bg:#f6f4ef;--card:#fff;--ink:#1c1a17;--mute:#6b665e;--line:#e4dfd5;--accent:#b4451f}
@media(prefers-color-scheme:dark){:root{--bg:#141210;--card:#1d1a17;--ink:#f1ede6;--mute:#9a9388;--line:#33302b;--accent:#e2673a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.5 system-ui,sans-serif;padding:24px 16px}
main{max-width:480px;margin:0 auto;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:24px}
h1{font-size:20px;margin:0 0 4px}p.s{color:var(--mute);margin:0 0 20px;font-size:14px}
label{display:block;font-size:13px;font-weight:600;margin:14px 0 6px}
input{width:100%;padding:12px;font:inherit;color:var(--ink);background:var(--bg);border:1px solid var(--line);border-radius:8px}
input:focus{outline:2px solid var(--accent);outline-offset:1px}
button{width:100%;margin-top:20px;padding:13px;font:inherit;font-weight:700;color:#fff;background:var(--accent);border:0;border-radius:8px;cursor:pointer}
button:disabled{opacity:.6;cursor:wait}#m{margin-top:14px;font-size:14px;min-height:20px}.ok{color:#2e8b57}.er{color:#d03b3b}
.pv{margin-top:18px;padding:12px;border:1px dashed var(--line);border-radius:8px;font-size:13px;color:var(--mute)}
</style></head><body><main>
<h1>Send a resource</h1><p class="s">Fill in three fields. The email body is added for you.</p>
<form id="f">
<label for="e">Contact email</label><input id="e" type="email" required autocomplete="off" placeholder="name@example.com">
<label for="s">Resource name (subject)</label><input id="s" required placeholder="The 5 Prompt Playbook">
<label for="l">Resource link</label><input id="l" type="url" required placeholder="https://...">
<label for="p">Password</label><input id="p" type="password" required autocomplete="current-password">
<button id="b">Send email</button><div id="m" role="status"></div>
</form>
<div class="pv"><b>Email they receive</b><br>Subject: <span id="ps">(resource name)</span><br>Here is the resource as promised.<br><span id="pl">(link)</span></div>
</main><script>
const $=i=>document.getElementById(i);
try{$("p").value=localStorage.getItem("rs_pw")||""}catch(e){}
$("s").oninput=()=>$("ps").textContent=$("s").value||"(resource name)";
$("l").oninput=()=>$("pl").textContent=$("l").value||"(link)";
$("f").onsubmit=async ev=>{ev.preventDefault();const b=$("b"),m=$("m");b.disabled=true;m.className="";m.textContent="Sending...";
try{const r=await fetch("/send",{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify({password:$("p").value,email:$("e").value,subject:$("s").value,link:$("l").value})});
const d=await r.json();if(!r.ok)throw new Error(d.error||"Failed");
try{localStorage.setItem("rs_pw",$("p").value)}catch(e){}
m.className="ok";m.textContent="Sent to "+$("e").value.trim()+(d.new?" (new contact created)":"");$("e").value="";$("e").focus()}
catch(e){m.className="er";m.textContent=e.message}b.disabled=false};
</script></body></html>`;

export default {
  async fetch(request, env) {
    const { pathname } = new URL(request.url);
    if (request.method === "POST" && pathname === "/send") return send(request, env);
    return new Response(PAGE, { headers: { "content-type": "text/html; charset=utf-8" } });
  },
};
