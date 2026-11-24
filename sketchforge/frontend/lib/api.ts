import type { Mode, Params, ProcessResult, Presets, Schema } from "./types";

export const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/$/, "");

async function fail(res: Response): Promise<never> {
  let msg = `Request failed (${res.status})`;
  try {
    const body = await res.json();
    const d = body.detail;
    if (typeof d === "string") msg = d;
    else if (Array.isArray(d) && d.length) msg = d.map((e: any) => `${(e.loc || []).slice(-1)[0]}: ${e.msg}`).join("; ");
  } catch {
    /* keep default message */
  }
  throw new Error(msg);
}

export async function getSchema(): Promise<Schema> {
  const r = await fetch(`${API_URL}/api/schema`);
  if (!r.ok) await fail(r);
  return r.json();
}

export async function getPresets(): Promise<Presets> {
  const r = await fetch(`${API_URL}/api/presets`);
  if (!r.ok) await fail(r);
  return r.json();
}

function form(file: File, mode: Mode, params: Params, extra: Record<string, string>) {
  const f = new FormData();
  f.append("file", file);
  f.append("mode", mode);
  f.append("params", JSON.stringify(params));
  Object.entries(extra).forEach(([k, v]) => f.append(k, v));
  return f;
}

export async function renderPreview(file: File, mode: Mode, params: Params, signal?: AbortSignal): Promise<ProcessResult> {
  const r = await fetch(`${API_URL}/api/process`, {
    method: "POST",
    body: form(file, mode, params, { quality: "preview" }),
    signal,
  });
  if (!r.ok) await fail(r);
  return r.json();
}

export async function download(file: File, mode: Mode, params: Params, format: string): Promise<void> {
  const r = await fetch(`${API_URL}/api/export`, { method: "POST", body: form(file, mode, params, { format }) });
  if (!r.ok) await fail(r);
  const blob = await r.blob();
  const cd = r.headers.get("Content-Disposition") || "";
  const name = /filename="([^"]+)"/.exec(cd)?.[1] || `sketchforge.${format.startsWith("svg") ? "svg" : format}`;
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}
