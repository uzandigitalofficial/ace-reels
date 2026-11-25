import React from 'react';
import { AbsoluteFill, Audio, OffthreadVideo, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { loadFont as loadSans } from '@remotion/google-fonts/InterTight';
import { loadFont as loadSerif } from '@remotion/google-fonts/InstrumentSerif';

const { fontFamily: SANS } = loadSans('normal', { weights: ['600', '800', '900'], subsets: ['latin'] });
const { fontFamily: SERIF } = loadSerif('italic', { weights: ['400'], subsets: ['latin'] });

export type Word = { w: string; start: number; end: number };
export type Seg = { kind: 'hook' | 'line' | 'cta'; show: string; say: string; start: number; end: number; words: Word[]; clip: string | null; device: 'full' | 'phone' | 'laptop'; clipFrom?: number; n?: number };
export type ReelProps = { fps: number; total: number; voice: string | null; music: string | null; kicker?: string; cta?: { channel: 'dm' | 'whatsapp'; text: string };
  brand: { name: string; url: string; contact: string; accent: string }; segs: Seg[] };

const clamp = { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' } as const;
const hash = (i: number) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

export const Reel: React.FC<ReelProps> = (p) => {
  const { fps, durationInFrames: T } = useVideoConfig();
  const mv = p.voice ? 0.13 : 0.6;
  return (
    <AbsoluteFill style={{ background: '#050505', fontFamily: SANS }}>
      {p.segs.map((s, i) => {
        const from = i === 0 ? 0 : Math.round((s.start - 0.12) * fps);
        const next = i < p.segs.length - 1 ? Math.round((p.segs[i + 1].start - 0.12) * fps) : T;
        return (
          <Sequence key={i} from={from} durationInFrames={Math.max(1, next - from)}>
            <Scene s={s} p={p} len={Math.max(1, next - from)} idx={i} />
          </Sequence>
        );
      })}
      {p.voice ? <Captions p={p} /> : null}
      <Chrome p={p} />
      {p.voice ? <Audio src={staticFile(p.voice)} /> : null}
      {p.music ? <Audio src={staticFile(p.music)} volume={(f) => interpolate(f, [0, 15, T - 40, T], [0, mv, mv, 0], clamp)} /> : null}
    </AbsoluteFill>
  );
};

const Ambient: React.FC<{ f: number; accent: string }> = ({ f, accent }) => (
  <AbsoluteFill style={{ overflow: 'hidden' }}>
    <AbsoluteFill style={{ background: `radial-gradient(45% 30% at ${50 + 30 * Math.sin(f / 45)}% ${28 + 10 * Math.cos(f / 60)}%, ${accent}30, transparent 70%), radial-gradient(40% 28% at ${40 - 25 * Math.cos(f / 55)}% ${78 + 8 * Math.sin(f / 50)}%, ${accent}1c, transparent 70%)` }} />
    <AbsoluteFill style={{ opacity: 0.09, backgroundImage: 'linear-gradient(rgba(255,255,255,.6) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,.6) 1px, transparent 1px)', backgroundSize: '90px 90px', backgroundPosition: `0 ${(f * 1.2) % 90}px`, maskImage: 'radial-gradient(70% 50% at 50% 50%, #000, transparent)' }} />
    {Array.from({ length: 36 }).map((_, i) => {
      const x = hash(i) * 1080, sp = 0.6 + hash(i + 50) * 1.6, sz = 2 + hash(i + 99) * 4;
      const y = 1980 - ((f * sp + hash(i + 7) * 1980) % 2040);
      return <div key={i} style={{ position: 'absolute', left: x + 20 * Math.sin(f / 30 + i), top: y, width: sz, height: sz, borderRadius: sz, background: accent, opacity: 0.18 + 0.4 * hash(i + 3), boxShadow: `0 0 ${sz * 4}px ${accent}` }} />;
    })}
  </AbsoluteFill>
);

const Scene: React.FC<{ s: Seg; p: ReelProps; len: number; idx: number }> = ({ s, p, len, idx }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame: f, fps, config: { damping: 200, mass: 0.7 } });
  const whip = idx === 0 ? 1 : spring({ frame: f, fps, config: { damping: 22, stiffness: 240, mass: 0.5 } });
  const dir = idx % 2 ? 1 : -1;
  const push = interpolate(f, [0, len], [1, 1.1]);
  const clip = s.clip ? staticFile(s.clip) : null;
  const from = s.clipFrom ?? 0;
  const full = s.device === 'full';
  return (
    <AbsoluteFill style={{ transform: `translateX(${(1 - whip) * dir * 420}px) scale(${1 + (1 - whip) * 0.08})`, filter: `blur(${(1 - whip) * 26}px)` }}>
      {clip ? (
        <AbsoluteFill style={{ transform: `scale(${(full ? 1.22 : 1.3) * push}) translateY(${Math.sin(f / 40) * 12}px)`, filter: full ? 'brightness(.36) saturate(1.2) blur(16px)' : 'blur(36px) brightness(.42) saturate(1.4)' }}>
          <OffthreadVideo src={clip} startFrom={from} muted style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
        </AbsoluteFill>
      ) : null}
      <Ambient f={f + idx * 97} accent={p.brand.accent} />
      <AbsoluteFill style={{ background: 'linear-gradient(180deg, rgba(5,5,5,.6) 0%, transparent 25%, transparent 60%, rgba(5,5,5,.88) 100%)' }} />
      {s.device === 'phone' && clip ? <Phone clip={clip} from={from} f={f} enter={enter} len={len} accent={p.brand.accent} /> : null}
      {s.device === 'laptop' && clip ? <Laptop clip={clip} from={from} f={f} enter={enter} len={len} accent={p.brand.accent} /> : null}
      {s.kind === 'cta' ? <Cta s={s} p={p} f={f} /> : <Headline s={s} p={p} f={f} top={!full} />}
      {s.kind === 'line' && s.n ? <Num n={s.n} f={f} accent={p.brand.accent} top={!full} /> : null}
      {s.kind === 'hook' && p.kicker ? <Chip text={p.kicker} f={f} accent={p.brand.accent} /> : null}
    </AbsoluteFill>
  );
};

const Chip: React.FC<{ text: string; f: number; accent: string }> = ({ text, f, accent }) => {
  const { fps } = useVideoConfig();
  const a = spring({ frame: f - 1, fps, config: { damping: 12, stiffness: 200 } });
  const pulse = 1 + 0.04 * Math.sin(f / 5);
  return (
    <div style={{ position: 'absolute', top: 560, width: '100%', display: 'flex', justifyContent: 'center' }}>
      <div style={{ transform: `scale(${a * pulse}) rotate(${-2 + 2 * a}deg)`, background: accent, color: '#050505', fontWeight: 900, fontSize: 36, letterSpacing: '0.12em', padding: '14px 28px', borderRadius: 999 }}>{text}</div>
    </div>
  );
};

const Num: React.FC<{ n: number; f: number; accent: string; top: boolean }> = ({ n, f, accent, top }) => {
  const { fps } = useVideoConfig();
  const a = spring({ frame: f, fps, config: { damping: 14, stiffness: 160 } });
  return (
    <div style={{ position: 'absolute', top: top ? 165 : 470, left: 0, width: '100%', textAlign: 'center', fontWeight: 900, fontSize: top ? 96 : 130, lineHeight: 1, color: 'transparent', WebkitTextStroke: `3px ${accent}`, opacity: 0.9 * a, transform: `translateY(${(1 - a) * -60}px) scale(${0.7 + 0.3 * a})` }}>{String(n).padStart(2, '0')}</div>
  );
};

const Phone: React.FC<{ clip: string; from: number; f: number; enter: number; len: number; accent: string }> = ({ clip, from, f, enter, len, accent }) => {
  const ry = interpolate(f, [0, len], [-20, 14]);
  const rx = 12 - 6 * enter;
  return (
    <AbsoluteFill style={{ perspective: 2400, alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ width: 540, height: 1120, marginTop: 330, borderRadius: 80, background: '#0b0b0c', padding: 15,
        boxShadow: `0 0 0 2px rgba(255,255,255,.2), 0 0 0 9px #050505, 0 0 0 10px rgba(255,255,255,.08), 0 100px 170px rgba(0,0,0,.85), 0 0 160px ${accent}30`,
        transform: `translateY(${(1 - enter) * 620 + Math.sin(f / 18) * 14}px) rotateX(${rx}deg) rotateY(${ry}deg) rotateZ(${-3 + 3 * enter + Math.sin(f / 26)}deg)` }}>
        <div style={{ width: '100%', height: '100%', borderRadius: 66, overflow: 'hidden', position: 'relative', background: '#000' }}>
          <OffthreadVideo src={clip} startFrom={from} muted style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          <div style={{ position: 'absolute', inset: 0, background: `linear-gradient(${115 + 20 * Math.sin(f / 30)}deg, rgba(255,255,255,.2), transparent 32%)` }} />
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
      <div style={{ marginTop: 380, transform: `translateY(${(1 - enter) * 520 + Math.sin(f / 20) * 12}px) rotateX(${14 - 6 * enter}deg) rotateY(${ry}deg) scale(${0.92 + 0.08 * enter})` }}>
        <div style={{ width: 980, height: 630, borderRadius: 26, background: '#0b0b0c', padding: 14, boxShadow: `0 0 0 2px rgba(255,255,255,.18), 0 80px 150px rgba(0,0,0,.85), 0 0 150px ${accent}26` }}>
          <div style={{ width: '100%', height: '100%', borderRadius: 14, overflow: 'hidden', position: 'relative', background: '#000' }}>
            <OffthreadVideo src={clip} startFrom={from} muted style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            <div style={{ position: 'absolute', inset: 0, background: `linear-gradient(${120 + 15 * Math.sin(f / 30)}deg, rgba(255,255,255,.16), transparent 35%)` }} />
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
    <AbsoluteFill style={{ justifyContent: top ? 'flex-start' : 'center', alignItems: 'center', padding: top ? '290px 70px 0' : '120px 70px 240px', transform: `translateY(${Math.sin(f / 22) * 5}px)` }}>
      <div style={{ textAlign: 'center', fontSize: size, lineHeight: 0.98, letterSpacing: '-0.04em', color: '#fff', textShadow: '0 10px 50px rgba(0,0,0,.55)' }}>
        {words.map((w, k) => {
          const sp = spring({ frame: f - 2 - k * (hook ? 4 : 3), fps, config: { damping: 13, stiffness: 190, mass: 0.6 } });
          const hl = k === words.length - 1 || /^R\d/.test(w);
          const wob = hl ? Math.sin((f - k * 4) / 9) * 2 : 0;
          return (
            <span key={k} style={{ display: 'inline-block', marginRight: '0.24em', transform: `translateY(${(1 - sp) * 70}px) scale(${0.65 + 0.35 * sp}) rotate(${wob * 0.6}deg)`, opacity: Math.min(1, sp * 1.5),
              color: hl ? p.brand.accent : '#fff', fontFamily: hl ? SERIF : SANS, fontStyle: hl ? 'italic' : 'normal', fontWeight: hl ? 400 : 900 }}>{w}</span>
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
  const wa = p.cta?.channel === 'whatsapp';
  const msg = p.cta?.text || 'SITE';
  const typed = Math.max(0, Math.min(msg.length, Math.floor((f - 22) / 2)));
  const sent = f > 22 + msg.length * 2 + 8;
  const pop = spring({ frame: f - (22 + msg.length * 2 + 8), fps, config: { damping: 10, stiffness: 220 } });
  return (
    <AbsoluteFill style={{ alignItems: 'center', textAlign: 'center', paddingTop: 330 }}>
      <div style={{ ...st(0), fontFamily: SERIF, fontStyle: 'italic', fontSize: 130, color: '#fff', lineHeight: 1 }}>{p.brand.name}</div>
      <div style={{ ...st(6), marginTop: 26, fontWeight: 900, fontSize: 64, letterSpacing: '-0.03em', color: p.brand.accent, lineHeight: 1.04, padding: '0 80px' }}>{s.show}</div>
      <div style={{ ...st(12), marginTop: 60, width: 860, borderRadius: 40, background: wa ? '#0b141a' : 'rgba(20,20,22,.92)', border: '1px solid rgba(255,255,255,.12)', padding: 34, boxShadow: '0 40px 90px rgba(0,0,0,.6)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 18, marginBottom: 30 }}>
          <div style={{ width: 70, height: 70, borderRadius: 70, background: p.brand.accent, color: '#050505', fontWeight: 900, fontSize: 30, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>SV</div>
          <div style={{ textAlign: 'left' }}><div style={{ color: '#fff', fontWeight: 800, fontSize: 32 }}>{wa ? 'Stolen Valour' : '@stolenvalour.co.za'}</div><div style={{ color: 'rgba(255,255,255,.55)', fontSize: 24 }}>{wa ? '065 027 6518' : 'Message'}</div></div>
        </div>
        <div style={{ display: 'flex', justifyContent: 'flex-end', minHeight: 96 }}>
          {sent ? <div style={{ transform: `scale(${0.6 + 0.4 * pop})`, transformOrigin: 'right bottom', background: wa ? '#005c4b' : '#3a5bff', color: '#fff', fontSize: 40, fontWeight: 700, padding: '20px 30px', borderRadius: 30 }}>{msg} <span style={{ fontSize: 24, opacity: 0.7 }}>{wa ? '✓✓' : ''}</span></div> : null}
        </div>
        <div style={{ marginTop: 18, height: 84, borderRadius: 42, background: 'rgba(255,255,255,.08)', display: 'flex', alignItems: 'center', padding: '0 30px', color: '#fff', fontSize: 36, textAlign: 'left' }}>
          {sent ? <span style={{ opacity: 0.4 }}>Message...</span> : <span>{msg.slice(0, typed)}<span style={{ opacity: f % 16 < 8 ? 1 : 0 }}>|</span></span>}
        </div>
      </div>
      <div style={{ ...st(18), marginTop: 46, fontWeight: 600, fontSize: 30, letterSpacing: '0.28em', color: 'rgba(255,255,255,.8)' }}>{p.brand.url.toUpperCase()}</div>
    </AbsoluteFill>
  );
};

const Captions: React.FC<{ p: ReelProps }> = ({ p }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const seg = p.segs.find((s) => t >= s.start - 0.05 && t <= s.end + 0.3);
  if (!seg || seg.kind === 'cta') return null;
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
              transform: `scale(${active ? 0.88 + 0.14 * sp : 1}) translateY(${shown ? 0 : 20}px)`, textShadow: active ? 'none' : '0 4px 28px rgba(0,0,0,.85)' }}>{w.w}</span>
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
