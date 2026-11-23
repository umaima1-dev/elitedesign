"use client";

import { useEffect, useState } from "react";

export default function Home() {
  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [link, setLink] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState(null);

  useEffect(() => {
    try {
      setPassword(localStorage.getItem("rs_pw") || "");
    } catch {}
  }, []);

  async function onSubmit(e) {
    e.preventDefault();
    setBusy(true);
    setMsg({ type: "", text: "Sending..." });
    try {
      const res = await fetch("/api/send", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ password, email, subject, link }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed to send");
      try {
        localStorage.setItem("rs_pw", password);
      } catch {}
      setMsg({ type: "ok", text: `Sent to ${email.trim()}${data.isNew ? " (new contact created)" : ""}` });
      setEmail("");
    } catch (err) {
      setMsg({ type: "err", text: err.message });
    }
    setBusy(false);
  }

  return (
    <main>
      <h1>Send a resource</h1>
      <p className="sub">Fill in three fields. The email body is added for you.</p>
      <form onSubmit={onSubmit}>
        <label htmlFor="e">Contact email</label>
        <input id="e" type="email" required autoComplete="off" placeholder="name@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
        <label htmlFor="s">Resource name (subject)</label>
        <input id="s" required placeholder="The 5 Prompt Playbook" value={subject} onChange={(e) => setSubject(e.target.value)} />
        <label htmlFor="l">Resource link</label>
        <input id="l" type="url" required placeholder="https://..." value={link} onChange={(e) => setLink(e.target.value)} />
        <label htmlFor="p">Password</label>
        <input id="p" type="password" required autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button disabled={busy}>{busy ? "Sending..." : "Send email"}</button>
        <div className="msg" role="status">
          {msg && <span className={msg.type}>{msg.text}</span>}
        </div>
      </form>
      <div className="preview">
        <b>Email they receive</b>
        <br />
        Subject: {subject || "(resource name)"}
        <br />
        Here is the resource as promised.
        <br />
        {link || "(link)"}
      </div>
    </main>
  );
}
