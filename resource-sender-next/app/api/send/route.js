import { NextResponse } from "next/server";
import { buildEmail } from "../../email-template";

const GHL = "https://services.leadconnectorhq.com";

async function ghl(path, body) {
  const res = await fetch(GHL + path, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.GHL_TOKEN}`,
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

export async function POST(request) {
  const { password, email, subject, link } = await request.json().catch(() => ({}));

  if (!process.env.APP_PASSWORD || password !== process.env.APP_PASSWORD) {
    return NextResponse.json({ error: "Wrong password" }, { status: 401 });
  }
  if (!process.env.GHL_TOKEN || !process.env.GHL_LOCATION_ID) {
    return NextResponse.json({ error: "Server is missing GHL_TOKEN or GHL_LOCATION_ID" }, { status: 500 });
  }

  const to = String(email || "").trim().toLowerCase();
  const subj = String(subject || "").trim();
  const url = String(link || "").trim();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(to)) return NextResponse.json({ error: "Enter a valid email address" }, { status: 400 });
  if (!subj) return NextResponse.json({ error: "Enter the resource name (it becomes the subject)" }, { status: 400 });
  if (!/^https?:\/\/\S+$/i.test(url)) return NextResponse.json({ error: "Enter the full resource link starting with https://" }, { status: 400 });

  try {
    // Finds the contact by email, or creates it if they are new.
    const up = await ghl("/contacts/upsert", { locationId: process.env.GHL_LOCATION_ID, email: to });
    const contactId = up.contact?.id;
    if (!contactId) throw new Error("Could not find or create the contact");

    const { text, html } = buildEmail(url, subj);
    const msg = { type: "Email", contactId, subject: subj, message: text, html };
    if (process.env.FROM_EMAIL) {
      msg.emailFrom = process.env.FROM_NAME ? `${process.env.FROM_NAME} <${process.env.FROM_EMAIL}>` : process.env.FROM_EMAIL;
    }
    await ghl("/conversations/messages", msg);
    return NextResponse.json({ ok: true, isNew: !!up.new });
  } catch (e) {
    return NextResponse.json({ error: e.message }, { status: 502 });
  }
}
