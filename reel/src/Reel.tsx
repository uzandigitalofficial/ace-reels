import React from 'react';
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { loadFont as loadSans } from '@remotion/google-fonts/InterTight';
import { loadFont as loadSerif } from '@remotion/google-fonts/InstrumentSerif';

const { fontFamily: SANS } = loadSans();
const { fontFamily: SERIF } = loadSerif();

export type Word = { w: string; start: number; end: number };
export type Seg = { kind: 'hook' | 'line' | 'cta'; show: string; say: string; start: number; end: number; words: Word[]; clip: string | null; device: 'full' | 'phone' | 'laptop'; clipFrom?: number };
export type ReelProps = { fps: number; total: number; voice: string | null; music: string | null; brand: { name: string; url: string; contact: string; accent: string }; segs: Seg[] };

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;

export const Reel: React.FC<ReelProps> = (p) => {
  const { fps, durationInFrames: T } = useVideoConfig();
  const mv = p.voice ? 0.14 : 0.55;
  return (
    <AbsoluteFill style={{ background: '#050505', fontFamily: SANS }}>
      {p.segs.map((s, i) => {
        const from = i === 0 ? 0 : Math.round((s.start - 0.12) * fps);
        const next = i < p.segs.length - 1 ? Math.round((p.segs[i + 1].start - 0.12) * fps) : T;
        return (
          <Sequence key={i} from={from} durationInFrames={Math.max(1, next - from)}>
            <Scene s={s} p={p} len={Math.max(1, next - from)} first={i === 0} />
          </Sequence>
        );
      })}
      <Captions p={p} />
      <Chrome p={p} />
      {p.voice ? <Audio src={staticFile(p.voice)} /> : null}
      {p.music ? <Audio src={staticFile(p.music)} volume={(f) => interpolate(f, [0, 20, T - 40, T], [0, mv, mv, 0], clamp)} /> : null}
    </AbsoluteFill>
  );
};

const Scene: React.FC<{ s: Seg; p: ReelProps; len: number; first: boolean }> = ({ s, p, len, first }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: f, fps, config: { damping: 200, mass: 0.7 } });
  const push = interpolate(f, [0, len], [1, 1.09]);
  const clip = s.clip ? staticFile(s.clip) : null;
  const from = s.clipFrom ?? 0;
  const full = s.device === 'full';
  const flash = first ? 0 : interpolate(f, [0, 5], [0.22, 0], clamp);
  return (
    <AbsoluteFill>
      {clip ? (
        <AbsoluteFill style={{ transform: `scale(${(full ? 1.22 : 1.3) * push + (1 - enter) * 0.12})`, filter: full ? `brightness(.46) saturate(1.2) blur(${7 + (1 - enter) * 14}px)` : 'blur(36px) brightness(.42) saturate(1.4)' }}>
          <OffthreadVideo src={clip} startFrom={from} muted style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        </AbsoluteFill>
      ) : null}
      <AbsoluteFill style={{ background: `radial-gradient(70% 45% at ${50 + 18 * Math.sin(f / 40)}% 30%, ${p.brand.accent}22, transparent 70%), linear-gradient(180deg, rgba(5,5,5,.55) 0%, transparent 28%, transparent 62%, rgba(5,5,5,.85) 100%)` }} />
      {s.device === 'phone' && clip ? <Phone clip={clip} from={from} f={f} enter={enter} len={len} accent={p.brand.accent} /> : null}
      {s.device === 'laptop' && clip ? <Laptop clip={clip} from={from} f={f} enter={enter} len={len} accent={p.brand.accent} /> : null}
      {s.kind === 'cta' ? <Cta s={s} p={p} f={f} /> : <Headline s={s} p={p} f={f} top={!full} />}
      <AbsoluteFill style={{ background: '#fff', opacity: flash }} />
    </AbsoluteFill>
  );
};

const Phone: React.FC<{ clip: string; from: number; f: number; enter: number; len: number; accent: string }> = ({ clip, from, f, enter, len, accent }) => {
  const ry = interpolate(f, [0, len], [-20, 14]);
  const rx = 12 - 6 * enter;
  return (
    <AbsoluteFill style={{ perspective: 2400, alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ width: 540, height: 1120, marginTop: 330, borderRadius: 80, background: '#0b0b0c', padding: 15,
        boxShadow: `0 0 0 2px rgba(255,255,255,.2), 0 0 0 9px #050505, 0 0 0 10px rgba(255,255,255,.08), 0 100px 170px rgba(0,0,0,.85), 0 0 160px ${accent}26`,
        transform: `translateY(${(1 - enter) * 620}px) rotateX(${rx}deg) rotateY(${ry}deg) rotateZ(${-3 + 3 * enter}deg)` }}>
        <div style={{ width: '100%', height: '100%', borderRadius: 66, overflow: 'hidden', position: 'relative', background: '#000' }}>
          <OffthreadVideo src={clip} startFrom={from} muted style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(115deg, rgba(255,255,255,.18), transparent 30%)' }} />
          <div style={{ position: 'absolute', top: 18, left: '50%', width: 150, height: 40, marginLeft: -75, borderRadius: 30, background: '#000' }} />
        </div>
      </div>
    </AbsoluteFill>
  );
};

const Laptop: React.FC<{ clip: string; from: number; f: number; enter: number; len: number; accent: string }> = ({ clip, from, f, enter, len, accent }) => {
  const ry = interpolate(f, [0, len], [16, -10]);
  return (
    <AbsoluteFill style={{ perspective: 2000, alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ marginTop: 380, transform: `translateY(${(1 - enter) * 520}px) rotateX(${14 - 6 * enter}deg) rotateY(${ry}deg) scale(${0.92 + 0.08 * enter})` }}>
        <div style={{ width: 980, height: 630, borderRadius: 26, background: '#0b0b0c', padding: 14, boxShadow: `0 0 0 2px rgba(255,255,255,.18), 0 80px 150px rgba(0,0,0,.85), 0 0 150px ${accent}22` }}>
          <div style={{ width: '100%', height: '100%', borderRadius: 14, overflow: 'hidden', position: 'relative', background: '#000' }}>
            <OffthreadVideo src={clip} startFrom={from} muted style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(120deg, rgba(255,255,255,.14), transparent 35%)' }} />
          </div>
        </div>
        <div style={{ width: 1120, height: 30, margin: '0 -70px', borderRadius: '0 0 30px 30px', background: 'linear-gradient(#2a2b2e, #111214)', boxShadow: '0 30px 60px rgba(0,0,0,.7)' }} />
      </div>
    </AbsoluteFill>
  );
};

const Headline: React.FC<{ s: Seg; p: ReelProps; f: number; top: boolean }> = ({ s, p, f, top }) => {
  const { fps } = useVideoConfig();
  const words = s.show.split(' ');
  const hook = s.kind === 'hook';
  const size = top ? 78 : s.show.length > 28 ? 112 : 132;
  return (
    <AbsoluteFill style={{ justifyContent: top ? 'flex-start' : 'center', alignItems: 'center', padding: top ? '250px 70px 0' : '0 70px 240px' }}>
      <div style={{ textAlign: 'center', fontSize: size, lineHeight: 0.98, letterSpacing: '-0.04em', color: '#fff', textShadow: '0 10px 50px rgba(0,0,0,.55)' }}>
        {words.map((w, k) => {
          const sp = spring({ frame: f - 2 - k * (hook ? 4 : 3), fps, config: { damping: 13, stiffness: 190, mass: 0.6 } });
          const hl = k === words.length - 1 || /^R\d/.test(w);
          return (
            <span key={k} style={{ display: 'inline-block', marginRight: '0.24em', transform: `translateY(${(1 - sp) * 70}px) scale(${0.65 + 0.35 * sp})`, opacity: Math.min(1, sp * 1.5),
              color: hl ? p.brand.accent : '#fff', fontFamily: hl ? SERIF : SANS, fontStyle: hl ? 'italic' : 'normal', fontWeight: hl ? 400 : 900, letterSpacing: hl ? '-0.01em' : undefined }}>{w}</span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const Cta: React.FC<{ s: Seg; p: ReelProps; f: number }> = ({ s, p, f }) => {
  const { fps } = useVideoConfig();
  const a = (d: number) => spring({ frame: f - d, fps, config: { damping: 16, stiffness: 150 } });
  const st = (d: number) => ({ opacity: a(d), transform: `translateY(${(1 - a(d)) * 50}px)` });
  return (
    <AbsoluteFill style={{ justifyContent: 'center', alignItems: 'center', textAlign: 'center', padding: '0 80px 260px' }}>
      <div style={{ ...st(0), fontFamily: SERIF, fontStyle: 'italic', fontSize: 150, color: '#fff', lineHeight: 1 }}>{p.brand.name}</div>
      <div style={{ ...st(6), marginTop: 36, fontWeight: 900, fontSize: 70, letterSpacing: '-0.03em', color: p.brand.accent, lineHeight: 1.02 }}>{s.show}</div>
      <div style={{ ...st(12), marginTop: 46, fontWeight: 600, fontSize: 34, letterSpacing: '0.28em', color: '#fff' }}>{p.brand.url.toUpperCase()}</div>
      <div style={{ ...st(16), marginTop: 14, fontWeight: 600, fontSize: 30, letterSpacing: '0.12em', color: 'rgba(255,255,255,.7)' }}>{p.brand.contact.toUpperCase()}</div>
    </AbsoluteFill>
  );
};

const Captions: React.FC<{ p: ReelProps }> = ({ p }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const seg = p.segs.find((s) => t >= s.start - 0.05 && t <= s.end + 0.3);
  if (!seg) return null;
  let ws = seg.words;
  if (!ws.length) {
    const parts = seg.say.split(' ');
    const d = (seg.end - seg.start) / parts.length;
    ws = parts.map((w, i) => ({ w, start: seg.start + i * d, end: seg.start + (i + 1) * d }));
  }
  const pages: Word[][] = [];
  for (let i = 0; i < ws.length; i += 3) pages.push(ws.slice(i, i + 3));
  const page = pages.find((pg) => t <= pg[pg.length - 1].end + 0.06) || pages[pages.length - 1];
  return (
    <AbsoluteFill style={{ justifyContent: 'flex-end', alignItems: 'center', paddingBottom: 250 }}>
      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', justifyContent: 'center', maxWidth: 940 }}>
        {page.map((w, k) => {
          const active = t >= w.start - 0.02 && t < w.end + 0.04;
          const shown = t >= w.start - 0.08;
          const sp = spring({ frame: Math.max(0, Math.round((t - w.start) * fps)), fps, config: { damping: 11, stiffness: 240 } });
          return (
            <span key={k} style={{ fontSize: 66, fontWeight: 800, letterSpacing: '-0.02em', padding: '4px 18px 8px', borderRadius: 16,
              background: active ? p.brand.accent : 'rgba(0,0,0,0)', color: active ? '#050505' : '#fff', opacity: shown ? 1 : 0,
              transform: `scale(${active ? 0.88 + 0.14 * sp : 1})`, textShadow: active ? 'none' : '0 4px 28px rgba(0,0,0,.85)' }}>{w.w}</span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

const Chrome: React.FC<{ p: ReelProps }> = ({ p }) => {
  const f = useCurrentFrame();
  const { durationInFrames: T } = useVideoConfig();
  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', top: 120, width: '100%', textAlign: 'center', fontWeight: 600, fontSize: 22, letterSpacing: '0.5em', color: 'rgba(255,255,255,.75)', opacity: interpolate(f, [0, 20], [0, 1], clamp) }}>{p.brand.name.toUpperCase()}</div>
      <div style={{ position: 'absolute', top: 0, left: 0, height: 6, width: `${(100 * f) / T}%`, background: p.brand.accent }} />
    </AbsoluteFill>
  );
};
