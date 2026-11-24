"use client";
import type { Mode, Params, Schema } from "@/lib/types";
import { NumberField, Section, Segmented, Slider, Toggle } from "./ui";

interface Props {
  params: Params;
  set: (patch: Params) => void;
  schema: Schema;
}

export function SketchControls({ params: p, set, schema }: Props) {
  const sp = schema.sketch;
  const style = p.style as string;
  const S = (key: string, label: string, extra: Partial<Parameters<typeof Slider>[0]> = {}) => (
    <Slider label={label} value={p[key]} spec={sp[key]} onChange={(v) => set({ [key]: v })} {...extra} />
  );
  return (
    <>
      <Section title="Style">
        <Segmented
          value={style}
          onChange={(v) => set({ style: v })}
          options={[
            { value: "pencil", label: "Pencil" },
            { value: "lineart", label: "Outline" },
            { value: "hatch", label: "Hatch" },
            { value: "value", label: "Tones" },
          ]}
        />
      </Section>

      <Section title="Look">
        {S("detail", "Detail", { help: "Higher keeps finer features (eyes, hair, texture)." })}
        {S("contrast", "Contrast")}
        {(style === "pencil" || style === "hatch") && S("shadow", "Shadow depth")}
        {style === "lineart" && S("line_threshold", "Line sensitivity", { help: "Higher picks up more lines." })}
        {style === "lineart" && S("line_weight", "Line thickness", { step: 0.1 })}
        {(style === "value" || style === "hatch") && S("levels", style === "value" ? "Number of tones" : "Hatch layers")}
        {style === "hatch" && S("hatch_spacing", "Line spacing", { step: 0.5 })}
        {style === "hatch" && S("hatch_angle", "Base angle", { suffix: "°" })}
        {style === "hatch" && <Toggle label="Lines follow the shape of the subject" value={p.hatch_flow} onChange={(v) => set({ hatch_flow: v })} />}
        {style === "hatch" && S("jitter", "Hand-drawn wobble")}
        {(style === "pencil" || style === "hatch") && S("grain", "Paper grain")}
        {style !== "lineart" && S("outline", "Contour lines", { help: "Mixes an outline into the drawing." })}
      </Section>

      <Section title="Paper & transfer">
        <Segmented
          label="Paper"
          value={p.paper}
          onChange={(v) => set({ paper: v })}
          options={[
            { value: "white", label: "White" },
            { value: "cream", label: "Cream" },
          ]}
        />
        {S("grid_cols", "Transfer grid (columns)", { help: "0 turns the grid off." })}
      </Section>
    </>
  );
}

export function PbnControls({ params: p, set, schema }: Props) {
  const sp = schema.pbn;
  const S = (key: string, label: string, extra: Partial<Parameters<typeof Slider>[0]> = {}) => (
    <Slider label={label} value={p[key]} spec={sp[key]} onChange={(v) => set({ [key]: v })} {...extra} />
  );
  return (
    <>
      <Section title="Colours & shapes">
        {S("colors", "Number of colours")}
        {S("min_shape_mm", "Smallest shape", {
          step: 0.5,
          suffix: " mm",
          help: "Every shape is at least this wide at the print size, so each one fits a brush tip and a number.",
        })}
      </Section>
      <Section title="Smoothing">
        {S("pre_smooth", "Smooth out texture", { help: "Stops skin, fabric and noise becoming speckles." })}
        {S("cleanup", "Tidy edges")}
        {S("edge_smooth", "Curve smoothness")}
      </Section>
      <Section title="Output">
        <Segmented
          label="Preview view"
          value={p.view}
          onChange={(v) => set({ view: v })}
          options={[
            { value: "canvas", label: "Canvas" },
            { value: "guide", label: "Guide" },
            { value: "painted", label: "Painted" },
          ]}
        />
        {S("line_weight", "Line thickness", { step: 0.1 })}
        <Toggle label="Show numbers" value={p.numbers} onChange={(v) => set({ numbers: v })} />
        <Toggle label="Show colour key" value={p.legend} onChange={(v) => set({ legend: v })} />
      </Section>
    </>
  );
}

export function PrintSize({ mode, params, set }: { mode: Mode; params: Params; set: (patch: Params) => void }) {
  return (
    <Section title="Print size">
      <NumberField
        label="Width of the final artwork"
        value={params.print_width_cm ?? 30}
        min={5}
        max={500}
        step={1}
        suffix="cm"
        onChange={(v) => set({ print_width_cm: Math.min(500, Math.max(1, v)) })}
      />
      {mode === "sketch" && <p className="hint">The PNG is tagged with the right DPI so it prints at exactly this width.</p>}
    </Section>
  );
}
