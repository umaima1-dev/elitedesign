"use client";
import type { FieldSpec } from "@/lib/types";
import type { ReactNode } from "react";

export function Section({ title, children, hint }: { title: string; children: ReactNode; hint?: string }) {
  return (
    <section className="section">
      <h3>{title}</h3>
      {hint && <p className="hint">{hint}</p>}
      {children}
    </section>
  );
}

export function Slider({
  label,
  value,
  onChange,
  spec,
  step,
  suffix = "",
  help,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  spec: FieldSpec | undefined;
  step?: number;
  suffix?: string;
  help?: string;
}) {
  const min = spec?.minimum ?? 0;
  const max = spec?.maximum ?? 100;
  const st = step ?? (spec?.type === "integer" ? 1 : 0.1);
  return (
    <label className="field">
      <span className="row">
        <span>{label}</span>
        <output>
          {Number.isInteger(value) ? value : value.toFixed(1)}
          {suffix}
        </output>
      </span>
      <input
        type="range"
        min={min}
        max={max}
        step={st}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
      />
      {help && <small>{help}</small>}
    </label>
  );
}

export function Segmented<T extends string>({
  value,
  onChange,
  options,
  label,
}: {
  value: T;
  onChange: (v: T) => void;
  options: { value: T; label: string }[];
  label?: string;
}) {
  return (
    <div className="field">
      {label && <span className="row"><span>{label}</span></span>}
      <div className="segmented" role="group" aria-label={label}>
        {options.map((o) => (
          <button
            type="button"
            key={o.value}
            className={o.value === value ? "on" : ""}
            aria-pressed={o.value === value}
            onClick={() => onChange(o.value)}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export function Toggle({ label, value, onChange }: { label: string; value: boolean; onChange: (v: boolean) => void }) {
  return (
    <label className="toggle">
      <input type="checkbox" checked={value} onChange={(e) => onChange(e.target.checked)} />
      <span>{label}</span>
    </label>
  );
}

export function NumberField({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  suffix,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min?: number;
  max?: number;
  step?: number;
  suffix?: string;
}) {
  return (
    <label className="field">
      <span className="row">
        <span>{label}</span>
      </span>
      <span className="numwrap">
        <input
          type="number"
          value={Number.isFinite(value) ? value : ""}
          min={min}
          max={max}
          step={step}
          onChange={(e) => {
            const v = Number(e.target.value);
            if (Number.isFinite(v)) onChange(v);
          }}
        />
        {suffix && <em>{suffix}</em>}
      </span>
    </label>
  );
}
