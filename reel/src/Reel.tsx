import React from 'react';
import { AbsoluteFill, Audio, Easing, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from 'remotion';
import { BeatCtx, C, SERIF, applyPalette, clamp, onBeat } from './kit';
import { PaperBg, SCENES } from './scenes';
import { ReelProps, Seg, Word } from './types';

export type { ReelProps, Seg, Word } from './types';

const OVER = 12; // frames the outgoing scene overlaps the incoming one

export const Reel: React.FC<ReelProps> = (p) => {
  const { fps, durationInFrames: T } = useVideoConfig();
  applyPalette(p.palette);
  // the voice runs the whole reel, so music stays ducked under it; it lifts a little in the breaths between sentences
  const mv = p.voice ? 0.06 : 0.5;
  const lift = p.voice ? 0.095 : 0.5;
  const last = p.segs.length - 1;
  const beats = p.beats || [];
  const cutAt = (i: number) => (i === 0 ? 0 : Math.round((p.segs[i].cut ?? p.segs[i].start - 0.12) * fps));
  const breaths = React.useMemo(() => {
    const ws = p.segs.flatMap((s) => s.words);
    const out: [number, number][] = [];
    for (let k = 1; k < ws.length; k++) if (ws[k].start - ws[k - 1].end > 0.14) out.push([ws[k - 1].end, ws[k].start]);
    return out;
  }, [p.segs]);
  const musicVol = (f: number) => {
    const t = f / fps;
    let v = mv;
    for (const [a, b] of breaths) {
      if (t > a && t < b) { v = mv + (lift - mv) * Math.min(1, (t - a) / 0.06, (b - t) / 0.06); break; }
    }
    return v * interpolate(f, [0, 3, T - 40, T], [0, 1, 1, 0], clamp);
  };
  return (
    <AbsoluteFill style={{ background: C.paper }}>
      <PaperBg />
      {p.segs.map((s, i) => {
        const from = cutAt(i);
        const next = i < last ? cutAt(i + 1) : T;
        const len = Math.max(1, next - from);
        return (
          <Sequence key={i} from={from} durationInFrames={len + (i < last ? OVER : 0)}>
            <BeatCtx.Provider value={{ beats, from }}>
              <SceneWrap s={s} p={p} len={len} i={i} exit={i < last} />
            </BeatCtx.Provider>
          </Sequence>
        );
      })}
      {p.voice || p.captions ? <Captions p={p} /> : null}
      <Chrome p={p} />
      {p.voice ? <Audio src={staticFile(p.voice)} /> : null}
      {p.sfx ? <Audio src={staticFile(p.sfx)} volume={0.55} /> : null}
      {p.music ? <Audio src={staticFile(p.music)} trimBefore={Math.round((p.musicFrom || 0) * fps)} volume={musicVol} /> : null}
    </AbsoluteFill>
  );
};

const SceneWrap: React.FC<{ s: Seg; p: ReelProps; len: number; i: number; exit: boolean }> = ({ s, p, len, i, exit }) => {
  const f = useCurrentFrame();
  const Comp = SCENES[s.scene] || SCENES.kinetic;
  const e = exit ? interpolate(f, [len - 4, len + OVER], [0, 1], { ...clamp, easing: Easing.bezier(0.55, 0, 0.75, 0.2) }) : 0;
  const dir = i % 2 ? 1 : -1;
  return (
    <AbsoluteFill style={{ transform: `translate(${dir * 1150 * e}px, ${-40 * e}px) rotate(${dir * 7 * e}deg)`, opacity: interpolate(e, [0, 0.55], [1, 0], clamp) }}>
      <Comp c={{ s, p, len, i }} />
    </AbsoluteFill>
  );
};

/** One or two words at a time, big italic serif, low and centred, synced to the voice. */
const chunk = (ws: Word[]) => {
  const out: Word[][] = [];
  let cur: Word[] = [];
  ws.forEach((w, k) => {
    cur.push(w);
    const chars = cur.reduce((a, x) => a + x.w.length, 0);
    const nxt = ws[k + 1];
    if (/[.,!?;:]$/.test(w.w) || cur.length >= 2 || chars >= 11 || (nxt && chars + nxt.w.length > 14)) { out.push(cur); cur = []; }
  });
  if (cur.length) out.push(cur);
  return out;
};

const Captions: React.FC<{ p: ReelProps }> = ({ p }) => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = f / fps;
  const seg = p.segs.find((s) => t >= s.start - 0.05 && t <= s.end + 0.4);
  if (!seg || seg.kind === 'cta') return null;
  let ws = seg.words;
  if (!ws.length) {
    const parts = seg.say.split(' ');
    const d = (seg.end - seg.start) / parts.length;
    ws = parts.map((w, i) => ({ w, start: seg.start + i * d, end: seg.start + (i + 1) * d }));
  }
  const chunks = chunk(ws);
  let idx = -1;
  chunks.forEach((c, k) => { if (t >= c[0].start - 0.04) idx = k; });
  if (idx < 0) return null;
  const c = chunks[idx];
  const endT = c[c.length - 1].end;
  const nextStart = idx < chunks.length - 1 ? chunks[idx + 1][0].start : seg.end + 0.4;
  if (t > Math.min(nextStart, endT + 0.6)) return null;
  const st = Math.round((c[0].start - 0.04) * fps);
  const sp = spring({ frame: f - st, fps, config: { damping: 15, stiffness: 210, mass: 0.6 } });
  const out = interpolate(t, [Math.min(nextStart, endT + 0.6) - 0.08, Math.min(nextStart, endT + 0.6)], [1, 0], clamp);
  const txt = c.map((w) => w.w.replace(/[.,;:!]+$/, '')).join(' ');
  const big = txt.length > 11 ? 104 : 124;
  return (
    <AbsoluteFill style={{ justifyContent: 'flex-start', alignItems: 'center', paddingTop: 1372 }}>
      <div style={{ fontFamily: SERIF, fontStyle: 'italic', fontSize: big, lineHeight: 1.05, color: C.ink, letterSpacing: '-0.015em', whiteSpace: 'nowrap',
        opacity: Math.min(sp * 1.6, 1) * out, transform: `translateY(${(1 - sp) * 34}px) scale(${0.92 + 0.08 * sp})`, filter: `blur(${(1 - Math.min(1, sp)) * 6}px)` }}>
        {c.map((w, k) => {
          const clean = w.w.replace(/[.,;:!]+$/, '');
          const hot = /^R?\d/.test(clean) || /^(free|seven|7|google|whatsapp)$/i.test(clean.replace(/[^a-z0-9]/gi, ''));
          return <span key={k} style={{ color: hot ? C.acc : C.ink, textDecoration: hot ? 'underline' : 'none', textDecorationThickness: 4, textUnderlineOffset: 14 }}>{clean}{k < c.length - 1 ? ' ' : ''}</span>;
        })}
      </div>
    </AbsoluteFill>
  );
};

/** Only a navy progress line and a small serif SV wordmark in the corner. No counters, no labels.
 *  The line nudges thicker on every music beat. */
const Chrome: React.FC<{ p: ReelProps }> = ({ p }) => {
  const f = useCurrentFrame();
  const { durationInFrames: T, fps } = useVideoConfig();
  const a = interpolate(f, [0, 18], [0, 1], clamp);
  const b = onBeat(f, fps, p.beats, 0.2);
  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', top: 0, left: 0, height: 7 + 4 * b, width: `${(100 * f) / T}%`, background: C.ink }} />
      <div style={{ position: 'absolute', top: 96, left: 80, fontFamily: SERIF, fontStyle: 'italic', fontSize: 54, lineHeight: 1, color: C.ink, opacity: 0.88 * a, letterSpacing: '-0.02em' }}>SV</div>
    </AbsoluteFill>
  );
};
