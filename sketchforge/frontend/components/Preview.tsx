"use client";
import { useCallback, useRef, useState } from "react";
import type { Focus } from "@/lib/types";

type View = "result" | "split" | "original";

interface Props {
  originalUrl: string;
  resultUrl: string | null;
  aspect: number; // width / height
  busy: boolean;
  view: View;
  focus: Focus | null;
  drawing: boolean;
  onFocus: (f: Focus | null) => void;
}

export default function Preview({ originalUrl, resultUrl, aspect, busy, view, focus, drawing, onFocus }: Props) {
  const box = useRef<HTMLDivElement>(null);
  const [split, setSplit] = useState(50);
  const [draft, setDraft] = useState<Focus | null>(null);
  const drag = useRef<{ x: number; y: number } | null>(null);

  const rel = useCallback((e: React.PointerEvent) => {
    const r = box.current!.getBoundingClientRect();
    return {
      x: Math.min(1, Math.max(0, (e.clientX - r.left) / r.width)),
      y: Math.min(1, Math.max(0, (e.clientY - r.top) / r.height)),
    };
  }, []);

  const down = (e: React.PointerEvent) => {
    (e.currentTarget as HTMLElement).setPointerCapture(e.pointerId);
    if (drawing) {
      drag.current = rel(e);
      setDraft(null);
    } else if (view === "split") {
      setSplit(rel(e).x * 100);
      drag.current = { x: -1, y: -1 };
    }
  };
  const move = (e: React.PointerEvent) => {
    if (!drag.current) return;
    const p = rel(e);
    if (drawing && drag.current.x >= 0) {
      const a = drag.current;
      setDraft({ x: Math.min(a.x, p.x), y: Math.min(a.y, p.y), w: Math.abs(p.x - a.x), h: Math.abs(p.y - a.y) });
    } else if (view === "split") {
      setSplit(p.x * 100);
    }
  };
  const up = () => {
    if (drawing && draft && draft.w > 0.03 && draft.h > 0.03) onFocus(draft);
    drag.current = null;
    setDraft(null);
  };

  const shown = draft || focus;
  const showResult = resultUrl && view !== "original";
  return (
    <div
      ref={box}
      className={`stage ${drawing ? "drawing" : view === "split" ? "splitting" : ""}`}
      style={{ aspectRatio: String(aspect) }}
      onPointerDown={down}
      onPointerMove={move}
      onPointerUp={up}
      onPointerCancel={up}
    >
      {/* eslint-disable-next-line @next/next/no-img-element */}
      <img src={originalUrl} alt="Original photo" draggable={false} />
      {showResult && (
        // eslint-disable-next-line @next/next/no-img-element
        <img
          className="result"
          src={resultUrl!}
          alt="Result"
          draggable={false}
          style={view === "split" ? { clipPath: `inset(0 0 0 ${split}%)` } : undefined}
        />
      )}
      {view === "split" && resultUrl && <div className="divider" style={{ left: `${split}%` }}><span /></div>}
      {shown && (
        <div
          className="focusbox"
          style={{ left: `${shown.x * 100}%`, top: `${shown.y * 100}%`, width: `${shown.w * 100}%`, height: `${shown.h * 100}%` }}
        >
          <span>extra detail</span>
        </div>
      )}
      {busy && <div className="busy" aria-live="polite">Rendering…</div>}
    </div>
  );
}
