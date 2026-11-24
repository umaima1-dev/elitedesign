"use client";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { PbnControls, PrintSize, SketchControls } from "@/components/Controls";
import Preview from "@/components/Preview";
import { Section, Segmented, Slider } from "@/components/ui";
import { API_URL, download, getPresets, getSchema, renderPreview } from "@/lib/api";
import type { Focus, Mode, Params, Presets, ProcessResult, Schema } from "@/lib/types";

const defaultsOf = (spec: Schema[Mode]): Params => Object.fromEntries(Object.entries(spec).map(([k, v]) => [k, v.default ?? null]));

type View = "result" | "split" | "original";

export default function Home() {
  const [schema, setSchema] = useState<Schema | null>(null);
  const [presets, setPresets] = useState<Presets | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);

  const [file, setFile] = useState<File | null>(null);
  const [originalUrl, setOriginalUrl] = useState<string | null>(null);
  const [aspect, setAspect] = useState(1);

  const [mode, setMode] = useState<Mode>("sketch");
  const [sketch, setSketch] = useState<Params | null>(null);
  const [pbn, setPbn] = useState<Params | null>(null);

  const [results, setResults] = useState<Partial<Record<Mode, ProcessResult>>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<View>("result");
  const [drawing, setDrawing] = useState(false);
  const [dl, setDl] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInput = useRef<HTMLInputElement>(null);
  const recipeInput = useRef<HTMLInputElement>(null);

  // ---- load schema + presets from the backend (single source of truth for ranges and defaults)
  useEffect(() => {
    Promise.all([getSchema(), getPresets()])
      .then(([s, p]) => {
        setSchema(s);
        setPresets(p);
        setSketch(defaultsOf(s.sketch));
        setPbn(defaultsOf(s.pbn));
      })
      .catch((e) => setApiError(e instanceof Error ? e.message : String(e)));
  }, []);

  const params = mode === "sketch" ? sketch : pbn;
  const setParams = useCallback(
    (patch: Params) => (mode === "sketch" ? setSketch : setPbn)((p) => (p ? { ...p, ...patch } : p)),
    [mode],
  );

  // ---- file handling
  const pick = useCallback((f: File | undefined | null) => {
    if (!f) return;
    if (!f.type.startsWith("image/")) {
      setError("Please choose an image file (JPG, PNG or WebP).");
      return;
    }
    setError(null);
    setResults({});
    setFile(f);
    setOriginalUrl((old) => {
      if (old) URL.revokeObjectURL(old);
      return URL.createObjectURL(f);
    });
  }, []);

  useEffect(() => {
    if (!originalUrl) return;
    const img = new Image();
    img.onload = () => setAspect(img.naturalWidth / img.naturalHeight);
    img.src = originalUrl;
  }, [originalUrl]);

  // ---- live preview (debounced, cancels the previous request)
  useEffect(() => {
    if (!file || !params) return;
    const ctl = new AbortController();
    const t = setTimeout(async () => {
      setBusy(true);
      setError(null);
      try {
        const r = await renderPreview(file, mode, params, ctl.signal);
        setResults((prev) => ({ ...prev, [mode]: r }));
      } catch (e) {
        if ((e as Error).name !== "AbortError") setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (!ctl.signal.aborted) setBusy(false);
      }
    }, 450);
    return () => {
      clearTimeout(t);
      ctl.abort();
    };
  }, [file, mode, params]);

  const result = results[mode] ?? null;

  // PBN result is SVG markup: serve it to <img> through a blob URL
  const [svgUrl, setSvgUrl] = useState<string | null>(null);
  useEffect(() => {
    if (!result?.svg) {
      setSvgUrl(null);
      return;
    }
    const url = URL.createObjectURL(new Blob([result.svg], { type: "image/svg+xml" }));
    setSvgUrl(url);
    return () => URL.revokeObjectURL(url);
  }, [result?.svg]);
  const resultUrl = mode === "sketch" ? result?.image ?? null : svgUrl;

  // ---- actions
  const applyPreset = (name: string) => {
    const preset = presets?.[mode].find((p) => p.name === name);
    if (!preset || !schema) return;
    const keep = mode === "sketch" ? { focus: sketch?.focus ?? null, focus_boost: sketch?.focus_boost } : {};
    const base = defaultsOf(schema[mode]);
    const next = { ...base, ...preset.params, print_width_cm: params?.print_width_cm ?? base.print_width_cm, view: params?.view ?? base.view, ...keep };
    if (mode === "sketch") {
      delete next.view;
      setSketch(next);
    } else {
      setPbn(next);
    }
  };

  const loadRecipe = async (f: File | undefined) => {
    if (!f || !schema) return;
    try {
      const rec = JSON.parse(await f.text());
      const m: Mode = rec.mode === "pbn" ? "pbn" : "sketch";
      const p = rec.params ?? rec;
      const next = { ...defaultsOf(schema[m]), ...Object.fromEntries(Object.entries(p).filter(([k]) => k in schema[m])) };
      setMode(m);
      (m === "sketch" ? setSketch : setPbn)(next);
      setError(null);
    } catch {
      setError("That file is not a SketchForge recipe.");
    }
  };

  const doDownload = async (format: string) => {
    if (!file || !params) return;
    setDl(format);
    setError(null);
    try {
      await download(file, mode, params, format);
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setDl(null);
    }
  };

  const setFocus = (f: Focus | null) => {
    setDrawing(false);
    setSketch((p) =>
      p ? { ...p, focus: f ? { x: round(f.x), y: round(f.y), w: round(f.w), h: round(f.h) } : null } : p,
    );
  };

  const presetNames = useMemo(() => presets?.[mode].map((p) => p.name) ?? [], [presets, mode]);

  // ---- render
  if (apiError) {
    return (
      <main className="center">
        <div className="card">
          <h1>SketchForge</h1>
          <p className="error">Can’t reach the engine at <code>{API_URL}</code>.</p>
          <p>Start the backend, then reload this page:</p>
          <pre>cd backend{"\n"}uvicorn app.main:app --port 8000</pre>
          <small>{apiError}</small>
        </div>
      </main>
    );
  }
  if (!schema || !params) {
    return <main className="center"><p>Loading…</p></main>;
  }

  return (
    <div className="shell">
      <header>
        <h1>SketchForge</h1>
        <p>Photo → pencil sketch, traceable outline, or SVG paint-by-numbers. Same photo + same settings = same result, every time.</p>
      </header>

      <div className="layout">
        <aside className="panel">
          <Section title="1 · Photo">
            <div
              className={`drop ${dragOver ? "over" : ""}`}
              onClick={() => fileInput.current?.click()}
              onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); pick(e.dataTransfer.files?.[0]); }}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && fileInput.current?.click()}
            >
              {file ? <><strong>{file.name}</strong><span>Click or drop to replace</span></> : <><strong>Drop a photo here</strong><span>or click to browse · JPG, PNG, WebP</span></>}
            </div>
            <input ref={fileInput} type="file" accept="image/*" hidden onChange={(e) => pick(e.target.files?.[0])} />
          </Section>

          <Section title="2 · What do you want?">
            <Segmented<Mode>
              value={mode}
              onChange={(m) => { setMode(m); setDrawing(false); }}
              options={[
                { value: "sketch", label: "Sketch / trace" },
                { value: "pbn", label: "Paint by numbers" },
              ]}
            />
            <label className="field">
              <span className="row"><span>Start from a preset</span></span>
              <select value="" onChange={(e) => e.target.value && applyPreset(e.target.value)}>
                <option value="">Choose…</option>
                {presetNames.map((n) => <option key={n} value={n}>{n}</option>)}
              </select>
            </label>
          </Section>

          {mode === "sketch" ? (
            <SketchControls params={params} set={setParams} schema={schema} />
          ) : (
            <PbnControls params={params} set={setParams} schema={schema} />
          )}

          {mode === "sketch" && (
            <Section title="Extra detail on a face" hint="Draw a box on the preview; that area is rendered with more detail.">
              <div className="btnrow">
                <button type="button" className={drawing ? "primary" : ""} disabled={!file} onClick={() => setDrawing((d) => !d)}>
                  {drawing ? "Drag on the picture…" : "Draw detail box"}
                </button>
                {sketch?.focus && <button type="button" onClick={() => setFocus(null)}>Clear</button>}
              </div>
              {sketch?.focus && <Slider label="Extra detail" value={sketch.focus_boost} spec={schema.sketch.focus_boost} onChange={(v) => setSketch((p) => (p ? { ...p, focus_boost: v } : p))} />}
            </Section>
          )}

          <PrintSize mode={mode} params={params} set={setParams} />

          <Section title="3 · Download" hint="Downloads are rendered at full resolution and can take a few seconds.">
            <div className="btnrow wrap">
              {mode === "sketch" ? (
                <button type="button" className="primary" disabled={!file || !!dl} onClick={() => doDownload("png")}>{dl === "png" ? "Rendering…" : "PNG (print size)"}</button>
              ) : (
                <>
                  <button type="button" className="primary" disabled={!file || !!dl} onClick={() => doDownload("svg_canvas")}>{dl === "svg_canvas" ? "Rendering…" : "SVG canvas to print"}</button>
                  <button type="button" disabled={!file || !!dl} onClick={() => doDownload("svg_guide")}>{dl === "svg_guide" ? "Rendering…" : "SVG colour guide"}</button>
                  <button type="button" disabled={!file || !!dl} onClick={() => doDownload("svg_painted")}>{dl === "svg_painted" ? "Rendering…" : "SVG painted preview"}</button>
                </>
              )}
              <button type="button" disabled={!file || !!dl} onClick={() => doDownload("recipe")}>Settings (recipe)</button>
              <button type="button" onClick={() => recipeInput.current?.click()}>Load settings</button>
              <input ref={recipeInput} type="file" accept="application/json,.json" hidden onChange={(e) => { loadRecipe(e.target.files?.[0]); e.target.value = ""; }} />
            </div>
          </Section>
        </aside>

        <main className="stagewrap">
          {!file || !originalUrl ? (
            <div className="empty">
              <h2>Start with a photo</h2>
              <p>Upload a customer photo and pick a style. Adjust the sliders and the preview updates by itself.</p>
            </div>
          ) : (
            <>
              <div className="toolbar">
                <Segmented<View>
                  value={view}
                  onChange={setView}
                  options={[
                    { value: "result", label: "Result" },
                    { value: "split", label: "Compare" },
                    { value: "original", label: "Photo" },
                  ]}
                />
                {result && (
                  <span className="meta" title="Same photo + same settings always gives the same fingerprint">
                    {result.ms} ms · fingerprint {result.recipe.output_sha256.slice(0, 10)}
                  </span>
                )}
              </div>
              {error && <p className="error" role="alert">{error}</p>}
              <Preview
                originalUrl={originalUrl}
                resultUrl={resultUrl}
                aspect={aspect}
                busy={busy}
                view={view}
                focus={mode === "sketch" ? sketch?.focus ?? null : null}
                drawing={drawing && mode === "sketch"}
                onFocus={setFocus}
              />
              {mode === "pbn" && result?.palette && (
                <div className="palette">
                  <div className="stats">
                    <span><b>{result.stats.colors}</b> colours</span>
                    <span><b>{result.stats.regions}</b> shapes</span>
                    <span>smallest <b>{result.stats.smallest_shape_mm} mm</b></span>
                    <span>prints at <b>{result.stats.print_size_cm?.[0]} × {result.stats.print_size_cm?.[1]} cm</b></span>
                  </div>
                  <ul>
                    {result.palette.map((c) => (
                      <li key={c.number} title={`${c.coverage}% of the picture · ${c.regions} shapes`}>
                        <i style={{ background: c.hex, color: lum(c.rgb) < 140 ? "#fff" : "#222" }}>{c.number}</i>
                        <code>{c.hex}</code>
                        <small>{c.coverage}%</small>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              <p className="note">Preview is a fast low-resolution render. Downloads are full resolution and match the preview.</p>
            </>
          )}
        </main>
      </div>
    </div>
  );
}

const round = (n: number) => Math.round(n * 1000) / 1000;
const lum = (rgb: number[]) => 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];
