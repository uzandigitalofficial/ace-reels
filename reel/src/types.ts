export type Word = { w: string; start: number; end: number };
export type SceneName = 'kinetic' | 'casefile' | 'checklist' | 'google' | 'whatsapp' | 'sitebuild' | 'beforeafter' | 'price' | 'timeline' | 'icons' | 'footage' | 'cta';
export type Seg = {
  kind: 'hook' | 'line' | 'cta'; show: string; say: string; start: number; end: number; words: Word[];
  scene: SceneName; mood: 'neg' | 'pos'; n?: number;
  clip: string | null; clipFrom?: number;
};
export type Plan = { name: string; price: string; per: string; items: string[]; note: string };
export type ReelProps = {
  fps: number; total: number; voice: string | null; music: string | null; sfx?: string | null; captions?: boolean;
  pillar?: string; kicker?: string; niche?: string | null;
  palette?: Record<string, string> | null;
  cta?: { channel: 'dm' | 'whatsapp'; text: string };
  brand: { name: string; url: string; contact: string; accent: string; phone?: string; handle?: string };
  plans?: Plan[];
  segs: Seg[];
};
export type Ctx = { s: Seg; p: ReelProps; len: number; i: number };
