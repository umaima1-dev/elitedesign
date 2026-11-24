export type Mode = "sketch" | "pbn";
export type Params = Record<string, any>;

export interface FieldSpec {
  type?: string | null;
  minimum?: number | null;
  maximum?: number | null;
  default?: any;
  description?: string | null;
  enum?: string[] | null;
}
export type Schema = Record<Mode, Record<string, FieldSpec>>;

export interface Preset {
  name: string;
  params: Params;
}
export type Presets = Record<Mode, Preset[]>;

export interface PaletteEntry {
  number: number;
  hex: string;
  rgb: number[];
  coverage: number;
  regions: number;
}

export interface Recipe {
  engine_version: string;
  mode: Mode;
  params: Params;
  input_sha256: string;
  max_side: number;
  output_sha256: string;
}

export interface ProcessResult {
  mode: Mode;
  quality: "preview" | "full";
  width: number;
  height: number;
  stats: Record<string, any>;
  recipe: Recipe;
  ms: number;
  image?: string; // data URL (sketch)
  svg?: string; // markup (pbn)
  palette?: PaletteEntry[];
}

export interface Focus {
  x: number;
  y: number;
  w: number;
  h: number;
}
