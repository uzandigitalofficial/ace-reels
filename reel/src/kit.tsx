import React from 'react';
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from 'remotion';
import { loadFont as loadSans } from '@remotion/google-fonts/InterTight';
import { loadFont as loadSerif } from '@remotion/google-fonts/InstrumentSerif';
import { loadFont as loadCond } from '@remotion/google-fonts/Anton';

export const SANS = loadSans('normal', { weights: ['500', '600', '700', '800', '900'], subsets: ['latin'] }).fontFamily;
export const SERIF = loadSerif('italic', { weights: ['400'], subsets: ['latin'] }).fontFamily;
export const COND = loadCond('normal', { weights: ['400'], subsets: ['latin'] }).fontFamily;

/** Cream and navy only (design-v6b). `acc` is the highlight ink (navy, the italic serif words); `soft` is the lighter navy
 *  for secondary text. The one exception is `wa`, a muted WhatsApp green used only inside realistic chat and button mock-ups.
 *  Values are overwritten from brands/<brand>.json colours at render time (applyPalette). */
export const C = {
  paper: '#F2EBDD', ink: '#14213D', acc: '#14213D', soft: '#3A4A6B', card: '#FFFFFF', cream: '#FBF7EE',
  muted: 'rgba(58,74,107,.86)', faint: 'rgba(20,33,61,.13)', bar: '#E9E1D1', sticky: '#FFFCF4', kraft: '#E6DAC2', wax: '#1F2E52',
  wa: '#4F9B73', waBubble: '#DCF3D6',
};

export type Palette = Partial<Record<keyof typeof C, string>>;
export const applyPalette = (p?: Palette | null) => { if (p) Object.assign(C, Object.fromEntries(Object.entries(p).filter(([k, v]) => k in C && typeof v === 'string'))); };

export const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
export const ease = Easing.bezier(0.22, 1, 0.36, 1);
export const lerp = (f: number, a: number, b: number, from = 0, to = 1) => interpolate(f, [a, b], [from, to], { ...clamp, easing: ease });

/** Paper drop: a little overshoot, settles like a card landing on a desk. */
export const useSpring = (delay: number, cfg: 'drop' | 'soft' | 'pop' = 'drop') => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const config = cfg === 'drop' ? { damping: 14, stiffness: 120, mass: 0.9 } : cfg === 'pop' ? { damping: 11, stiffness: 190, mass: 0.6 } : { damping: 200, stiffness: 120, mass: 0.8 };
  return spring({ frame: f - delay, fps, config });
};

export const halftone = (alpha = 0.3, size = 8) => ({
  backgroundImage: `radial-gradient(rgba(20,33,61,${alpha}) 1.5px, transparent 2px)`,
  backgroundSize: `${size}px ${size}px`,
});

type ObjProps = {
  x: number; y: number; w: number; h?: number; delay?: number; rot?: number; from?: 'top' | 'left' | 'right' | 'bottom';
  dist?: number; radius?: number; dots?: boolean; shadow?: boolean; z?: number; drift?: boolean; style?: React.CSSProperties; children?: React.ReactNode;
};

/** Any paper object: drops in with a spring, a settling rotation, a soft shadow and a halftone drop shadow. */
export const Obj: React.FC<ObjProps> = ({ x, y, w, h, delay = 0, rot = 0, from = 'top', dist = 260, radius = 28, dots = true, shadow = true, z, drift = true, style, children }) => {
  const f = useCurrentFrame();
  const p = useSpring(delay);
  const lift = 1 - p;
  const l = Math.max(0, lift);
  const sg = rot >= 0 ? 1 : -1;
  const dx = from === 'left' ? -dist * lift : from === 'right' ? dist * lift : 0;
  const dy = from === 'top' ? -dist * lift : from === 'bottom' ? dist * lift : 0;
  const idle = drift ? Math.sin((f + delay * 7) / 46) * 0.35 : 0;
  const bob = drift ? Math.sin((f + delay * 5) / 39) * 2.5 : 0;
  return (
    <div style={{ position: 'absolute', left: x, top: y, width: w, height: h, zIndex: z, opacity: interpolate(p, [0, 0.35], [0, 1], clamp),
      transform: `translate(${dx}px, ${dy + bob}px) rotate(${rot + sg * 9 * lift + idle}deg) scale(${1 + 0.07 * l})` }}>
      {dots ? <div style={{ position: 'absolute', inset: 0, borderRadius: radius, ...halftone(0.26), transform: `translate(${14 + 36 * l}px, ${18 + 44 * l}px)`, opacity: 0.85 - 0.5 * l }} /> : null}
      <div style={{ position: 'relative', width: '100%', height: '100%', borderRadius: radius,
        boxShadow: shadow ? `0 ${6 + 30 * l}px ${22 + 50 * l}px rgba(20,33,61,${0.13 + 0.05 * l}), 0 1px 2px rgba(20,33,61,.08)` : undefined, ...style }}>
        {children}
      </div>
    </div>
  );
};

export const Pin: React.FC<{ x: number; y: number; color?: string; delay?: number }> = ({ x, y, color = C.acc, delay = 0 }) => {
  const p = useSpring(delay, 'pop');
  return (
    <div style={{ position: 'absolute', left: x - 22, top: y - 22, width: 44, height: 44, transform: `scale(${p}) translateY(${(1 - p) * -30}px)`, zIndex: 30 }}>
      <div style={{ position: 'absolute', left: 22, top: 30, width: 18, height: 10, borderRadius: 10, background: 'rgba(20,33,61,.25)', filter: 'blur(3px)' }} />
      <div style={{ width: 44, height: 44, borderRadius: 44, background: `radial-gradient(circle at 35% 30%, #fff8 0 14%, ${color} 34%, #0A1226 100%)`, boxShadow: '0 4px 8px rgba(0,0,0,.25)' }} />
    </div>
  );
};

export const Tape: React.FC<{ x: number; y: number; w?: number; rot?: number; delay?: number }> = ({ x, y, w = 150, rot = -6, delay = 0 }) => {
  const p = useSpring(delay, 'soft');
  return <div style={{ position: 'absolute', left: x, top: y, width: w, height: 44, zIndex: 25, opacity: p, transform: `rotate(${rot}deg) scaleX(${0.4 + 0.6 * p})`,
    background: 'rgba(240,230,200,.72)', boxShadow: '0 2px 6px rgba(20,33,61,.1)', clipPath: 'polygon(2% 0, 98% 4%, 100% 50%, 97% 100%, 1% 96%, 0 50%)' }} />;
};

export const Pill: React.FC<{ text: string; bg?: string; fg?: string; size?: number; style?: React.CSSProperties }> = ({ text, bg = C.acc, fg = C.cream, size = 26, style }) => (
  <div style={{ display: 'inline-block', background: bg, color: fg, fontFamily: SANS, fontWeight: 800, fontSize: size, letterSpacing: '0.08em', padding: `${size * 0.42}px ${size * 0.9}px`, borderRadius: 999, whiteSpace: 'nowrap', ...style }}>{text}</div>
);

/** Split a headline into words and pick the accent: *marked* words, else a price, else the last word. */
export const parseAccent = (show: string) => {
  const raw = show.split(/\s+/).filter(Boolean);
  const marked = raw.map((w) => /^\*.*\*[.,!?]?$/.test(w) || /^\*/.test(w) || /\*[.,!?]?$/.test(w));
  const words = raw.map((w) => w.replace(/\*/g, ''));
  if (marked.some(Boolean)) {
    let on = false; const acc: boolean[] = [];
    raw.forEach((w) => { const st = w.startsWith('*'); const en = /\*[.,!?]?$/.test(w); if (st) on = true; acc.push(on); if (en) on = false; });
    return { words, acc };
  }
  const price = words.findIndex((w) => /^R\d/.test(w));
  const k = price >= 0 ? price : words.length - 1;
  return { words, acc: words.map((_, i) => i === k) };
};

export const plain = (show: string) => show.replace(/\*/g, '');

/** Heavy grotesk headline, one italic serif coral accent word, words dropping in. */
export const Head: React.FC<{ show: string; top: number; size?: number; delay?: number; width?: number; align?: 'left' | 'center'; underline?: boolean; color?: string }> = ({ show, top, size, delay = 0, width = 920, align = 'left', underline = false, color = C.ink }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const { words, acc } = parseAccent(show);
  const len = plain(show).length;
  const fs = size ?? (len <= 14 ? 118 : len <= 22 ? 104 : len <= 30 ? 92 : 80);
  return (
    <div style={{ position: 'absolute', top, left: (1080 - width) / 2, width, textAlign: align, fontFamily: SANS, fontWeight: 900, fontSize: fs, lineHeight: 0.98, letterSpacing: '-0.045em', color, textWrap: 'balance' } as React.CSSProperties}>
      {words.map((w, k) => {
        const sp = spring({ frame: f - delay - k * 3, fps, config: { damping: 13, stiffness: 150, mass: 0.7 } });
        const a = acc[k];
        const ul = underline && a && (k === words.length - 1 || !acc[k + 1]);
        return (
          <span key={k} style={{ display: 'inline-block', position: 'relative', marginRight: '0.22em', opacity: interpolate(sp, [0, 0.4], [0, 1], clamp),
            transform: `translateY(${(1 - sp) * 60}px) rotate(${(1 - sp) * (k % 2 ? 6 : -6)}deg)`,
            ...(a ? { fontFamily: SERIF, fontWeight: 400, fontStyle: 'italic', color: C.acc, fontSize: fs * 1.1, letterSpacing: '-0.015em' } : {}) }}>
            {w}
            {ul ? <Swash delay={delay + k * 3 + 10} /> : null}
          </span>
        );
      })}
    </div>
  );
};

const Swash: React.FC<{ delay: number }> = ({ delay }) => {
  const f = useCurrentFrame();
  const p = interpolate(f - delay, [0, 14], [0, 1], { ...clamp, easing: ease });
  return (
    <svg viewBox="0 0 300 30" preserveAspectRatio="none" style={{ position: 'absolute', left: '-4%', bottom: '-0.12em', width: '108%', height: '0.22em', overflow: 'visible' }}>
      <path d="M4 20 C 70 6, 160 4, 296 14" pathLength={1} fill="none" stroke={C.acc} strokeWidth={7} strokeLinecap="round" strokeDasharray={1} strokeDashoffset={1 - p} />
    </svg>
  );
};

/** Green tick circle that pops and draws its check. */
export const Tick: React.FC<{ size?: number; delay?: number; on?: boolean; color?: string }> = ({ size = 60, delay = 0, on = true, color = C.ink }) => {
  const f = useCurrentFrame();
  const p = useSpring(delay, 'pop');
  const d = interpolate(f - delay - 4, [0, 10], [0, 1], { ...clamp, easing: ease });
  if (!on) return <div style={{ width: size, height: size, borderRadius: size, border: `3px dashed ${C.faint}`, flexShrink: 0 }} />;
  return (
    <div style={{ width: size, height: size, borderRadius: size, background: color, flexShrink: 0, transform: `scale(${p})`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <svg viewBox="0 0 24 24" width={size * 0.58} height={size * 0.58}><path d="M20 6 9 17l-5-5" pathLength={1} fill="none" stroke="#fff" strokeWidth={3.4} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={1} strokeDashoffset={1 - d} /></svg>
    </div>
  );
};

export const Cross: React.FC<{ size?: number; delay?: number }> = ({ size = 60, delay = 0 }) => {
  const f = useCurrentFrame();
  const p = useSpring(delay, 'pop');
  const d = interpolate(f - delay - 4, [0, 10], [0, 1], { ...clamp, easing: ease });
  return (
    <div style={{ width: size, height: size, borderRadius: size, background: C.soft, flexShrink: 0, transform: `scale(${p})`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <svg viewBox="0 0 24 24" width={size * 0.52} height={size * 0.52}><path d="M18 6 6 18M6 6l12 12" pathLength={1} fill="none" stroke="#fff" strokeWidth={3.4} strokeLinecap="round" strokeDasharray={1} strokeDashoffset={1 - d} /></svg>
    </div>
  );
};

/** Rubber stamp that thumps down. */
export const Stamp: React.FC<{ text: string; x: number; y: number; delay: number; color?: string; rot?: number; size?: number }> = ({ text, x, y, delay, color = C.acc, rot = -10, size = 40 }) => {
  const p = useSpring(delay, 'pop');
  return (
    <div style={{ position: 'absolute', left: x, top: y, zIndex: 40, opacity: interpolate(p, [0, 0.3], [0, 0.95], clamp), transform: `rotate(${rot}deg) scale(${2.2 - 1.2 * p})`,
      border: `5px solid ${color}`, borderRadius: 14, padding: '6px 18px', color, fontFamily: COND, fontSize: size, letterSpacing: '0.06em', whiteSpace: 'nowrap', mixBlendMode: 'multiply' }}>{text}</div>
  );
};

// Lucide icons (ISC licence, lucide.dev), inlined so the render needs no extra package. Drawn on with pathLength.
type El = [string, Record<string, string | number>];
export const ICONS: Record<string, El[]> = {
  globe: [['circle', { cx: 12, cy: 12, r: 10 }], ['path', { d: 'M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20' }], ['path', { d: 'M2 12h20' }]],
  search: [['circle', { cx: 11, cy: 11, r: 8 }], ['path', { d: 'm21 21-4.3-4.3' }]],
  chat: [['path', { d: 'M7.9 20A9 9 0 1 0 4 16.1L2 22Z' }]],
  phone: [['path', { d: 'M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z' }]],
  calendar: [['path', { d: 'M8 2v4' }], ['path', { d: 'M16 2v4' }], ['rect', { width: 18, height: 18, x: 3, y: 4, rx: 2 }], ['path', { d: 'M3 10h18' }], ['path', { d: 'm9 16 2 2 4-4' }]],
  clock: [['circle', { cx: 12, cy: 12, r: 10 }], ['path', { d: 'M12 6v6l4 2' }]],
  pin: [['path', { d: 'M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z' }], ['circle', { cx: 12, cy: 10, r: 3 }]],
  tag: [['path', { d: 'M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z' }], ['circle', { cx: 7.5, cy: 7.5, r: 1 }]],
  link: [['path', { d: 'M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71' }], ['path', { d: 'M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71' }]],
  report: [['path', { d: 'M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z' }], ['path', { d: 'M14 2v4a2 2 0 0 0 2 2h4' }], ['path', { d: 'M10 9H8' }], ['path', { d: 'M16 13H8' }], ['path', { d: 'M16 17H8' }]],
  pencil: [['path', { d: 'M21.174 6.812a1 1 0 0 0-3.986-3.987L3.842 16.174a2 2 0 0 0-.5.83l-1.321 4.352a.5.5 0 0 0 .623.622l4.353-1.32a2 2 0 0 0 .83-.497z' }], ['path', { d: 'm15 5 4 4' }]],
  server: [['rect', { width: 20, height: 8, x: 2, y: 2, rx: 2 }], ['rect', { width: 20, height: 8, x: 2, y: 14, rx: 2 }], ['path', { d: 'M6 6h.01' }], ['path', { d: 'M6 18h.01' }]],
  shield: [['path', { d: 'M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z' }], ['path', { d: 'm9 12 2 2 4-4' }]],
  image: [['rect', { width: 18, height: 18, x: 3, y: 3, rx: 2 }], ['circle', { cx: 9, cy: 9, r: 2 }], ['path', { d: 'm21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21' }]],
  phoneDevice: [['rect', { width: 14, height: 20, x: 5, y: 2, rx: 2 }], ['path', { d: 'M12 18h.01' }]],
  zap: [['path', { d: 'M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z' }]],
  hourglass: [['path', { d: 'M5 22h14' }], ['path', { d: 'M5 2h14' }], ['path', { d: 'M17 22v-4.172a2 2 0 0 0-.586-1.414L12 12l-4.414 4.414A2 2 0 0 0 7 17.828V22' }], ['path', { d: 'M7 2v4.172a2 2 0 0 0 .586 1.414L12 12l4.414-4.414A2 2 0 0 0 17 6.172V2' }]],
  mail: [['rect', { width: 20, height: 16, x: 2, y: 4, rx: 2 }], ['path', { d: 'm22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7' }]],
  lock: [['rect', { width: 18, height: 11, x: 3, y: 11, rx: 2 }], ['path', { d: 'M7 11V7a5 5 0 0 1 10 0v4' }]],
  star: [['path', { d: 'M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z' }]],
  help: [['circle', { cx: 12, cy: 12, r: 10 }], ['path', { d: 'M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3' }], ['path', { d: 'M12 17h.01' }]],
  pointer: [['path', { d: 'M14 4.1 12 6' }], ['path', { d: 'm5.1 8-2.9-.8' }], ['path', { d: 'm6 12-1.9 2' }], ['path', { d: 'M7.2 2.2 8 5.1' }], ['path', { d: 'M9.037 9.69a.498.498 0 0 1 .653-.653l11 4.5a.5.5 0 0 1-.074.949l-4.349 1.041a1 1 0 0 0-.74.739l-1.04 4.35a.5.5 0 0 1-.95.074z' }]],
};

export const Icon: React.FC<{ name: string; size?: number; color?: string; delay?: number; stroke?: number }> = ({ name, size = 80, color = C.ink, delay = 0, stroke = 2 }) => {
  const f = useCurrentFrame();
  const p = interpolate(f - delay, [0, 18], [0, 1], { ...clamp, easing: ease });
  const els = ICONS[name] || ICONS.globe;
  return (
    <svg viewBox="0 0 24 24" width={size} height={size} fill="none" stroke={color} strokeWidth={stroke} strokeLinecap="round" strokeLinejoin="round" style={{ overflow: 'visible' }}>
      {els.map(([tag, at], i) => React.createElement(tag, { key: i, ...at, pathLength: 1, strokeDasharray: 1, strokeDashoffset: 1 - p }))}
    </svg>
  );
};
