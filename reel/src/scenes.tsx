import React from 'react';
import { AbsoluteFill, Img, OffthreadVideo, interpolate, staticFile, useCurrentFrame } from 'remotion';
import { C, COND, Cross, Head, Icon, Obj, Pill, Pin, SANS, SERIF, Stamp, Tape, Tick, clamp, ease, halftone, lerp, plain, useSpring } from './kit';
import { Ctx } from './types';

const cap = (s: string) => s.charAt(0).toUpperCase() + s.slice(1);
const nicheOf = (c: Ctx) => c.p.niche || 'business';
const domainOf = (c: Ctx) => `your${nicheOf(c).replace(/[^a-z]/gi, '').toLowerCase()}.co.za`;
const text = (c: Ctx) => `${c.s.show} ${c.s.say}`.toLowerCase();
const typed = (f: number, str: string, delay: number, speed = 1.3) => str.slice(0, Math.max(0, Math.floor((f - delay) / speed)));

/** Headline block used by most scenes: the beat headline on top. No section labels, no numbering. */
const Top: React.FC<{ c: Ctx; size?: number }> = ({ c, size }) => <Head show={c.s.show} top={236} size={size} delay={3} />;

// ---------------------------------------------------------------- kinetic type statement
export const Kinetic: React.FC<{ c: Ctx }> = ({ c }) => {
  const f = useCurrentFrame();
  const hook = c.s.kind === 'hook';
  const len = plain(c.s.show).length;
  const fs = len <= 14 ? 172 : len <= 22 ? 150 : len <= 32 ? 128 : 110;
  const disc = useSpring(4, 'soft');
  // centre the block in the stage: rough line count from character widths of the heavy grotesk
  const lines = Math.max(1, Math.ceil((len * fs * 0.52) / 920));
  const top = Math.max(hook ? 620 : 580, Math.round(900 - (lines * fs * 0.98) / 2));
  return (
    <AbsoluteFill>
      <div style={{ position: 'absolute', left: 520, top: top - 120, width: 640, height: 640, borderRadius: 640, ...halftone(0.0, 10),
        backgroundImage: `radial-gradient(${C.acc} 2.4px, transparent 2.9px)`, backgroundSize: '13px 13px', opacity: 0.32 * disc,
        transform: `scale(${0.6 + 0.4 * disc}) rotate(${f * 0.15}deg)`, maskImage: 'radial-gradient(circle, #000 52%, transparent 71%)' }} />
      {hook && c.p.kicker ? <Obj x={80} y={top - 130} w={430} h={62} rot={-3} delay={0} radius={999} dots={false} shadow={false} dist={120}><Pill text={c.p.kicker} size={28} /></Obj> : null}
      <Head show={c.s.show} top={top} size={fs} delay={hook ? 4 : 2} underline />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- case file collage (question hooks)
export const CaseFile: React.FC<{ c: Ctx }> = ({ c }) => {
  const f = useCurrentFrame();
  const t = text(c);
  const word = /\bhow\b/.test(t) ? 'HOW?' : /\bwhy\b/.test(t) ? 'WHY?' : /\bwhat\b/.test(t) ? 'WHAT?' : /\bwho(se)?\b/.test(t) ? 'WHO?' : /\bwhere\b/.test(t) ? 'WHERE?'
    : /\bstill\b/.test(t) ? 'REALLY?' : /\?/.test(c.s.say) ? 'BE HONEST' : 'CHECK THIS';
  const gx = 120 + 420 * (0.5 + 0.5 * Math.sin(f / 34));
  const gy = 860 + 60 * Math.cos(f / 27);
  const g = useSpring(20, 'drop');
  return (
    <AbsoluteFill>
      {c.p.kicker ? <Obj x={80} y={200} w={430} h={62} rot={-2} delay={0} radius={999} dots={false} shadow={false} dist={100}><Pill text={c.p.kicker} size={26} /></Obj> : null}
      <Head show={c.s.show} top={300} size={plain(c.s.show).length > 26 ? 84 : 98} delay={3} />
      <Obj x={150} y={650} w={780} h={480} rot={-4} delay={8} radius={10} style={{ background: `linear-gradient(160deg, #EFE6D3, ${C.kraft} 60%, #DDCFB3)`, overflow: 'hidden' }}>
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(170deg, transparent 49.6%, rgba(20,33,61,.09) 50%, transparent 50.6%), linear-gradient(10deg, transparent 49.6%, rgba(20,33,61,.09) 50%, transparent 50.6%)' }} />
        <div style={{ position: 'absolute', left: 0, top: 0, width: '100%', height: '60%', background: 'linear-gradient(180deg, #E3D6BC, #DACAAD)', clipPath: 'polygon(0 0, 100% 0, 50% 100%)', boxShadow: 'inset 0 -2px 0 rgba(20,33,61,.08)' }} />
        <div style={{ position: 'absolute', left: 430, top: 296, width: 320, height: 156, background: C.cream, transform: 'rotate(2deg)', padding: '16px 24px', boxShadow: '0 3px 8px rgba(20,33,61,.12)' }}>
          <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 22, letterSpacing: '0.16em', color: C.soft }}>CASE FILE</div>
          <div style={{ fontFamily: COND, fontSize: word.length > 7 ? 60 : 76, lineHeight: 1.15, color: C.acc, letterSpacing: '0.02em', whiteSpace: 'nowrap' }}>{word}</div>
        </div>
      </Obj>
      <Seal x={540} y={918} delay={22} />
      <div style={{ position: 'absolute', left: gx, top: gy, opacity: g, transform: `translateY(${(1 - g) * -200}px) rotate(-28deg)`, zIndex: 50 }}>
        <Magnifier />
      </div>
    </AbsoluteFill>
  );
};

const Seal: React.FC<{ x: number; y: number; delay: number }> = ({ x, y, delay }) => {
  const p = useSpring(delay, 'pop');
  return (
    <div style={{ position: 'absolute', left: x - 72, top: y - 72, width: 144, height: 144, zIndex: 20, transform: `scale(${1.6 - 0.6 * p}) rotate(${-12 + 12 * p}deg)`, opacity: interpolate(p, [0, 0.3], [0, 1], clamp) }}>
      <div style={{ position: 'absolute', inset: -8, borderRadius: '46% 54% 50% 50%', background: C.wax, boxShadow: '0 6px 14px rgba(10,18,38,.35)' }} />
      <div style={{ position: 'absolute', inset: 12, borderRadius: 140, border: '4px solid rgba(255,255,255,.16)', background: 'radial-gradient(circle at 35% 30%, #3A4A6B, #14213D)', display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: SERIF, fontStyle: 'italic', fontSize: 64, color: 'rgba(242,235,221,.9)', textShadow: '0 -2px 0 rgba(0,0,0,.3)' }}>SV</div>
    </div>
  );
};

const Magnifier: React.FC = () => (
  <div style={{ position: 'relative', width: 230, height: 360 }}>
    <div style={{ position: 'absolute', left: 92, top: 210, width: 46, height: 150, borderRadius: 20, background: 'linear-gradient(90deg, #2A2E4A, #13162B)', boxShadow: '8px 12px 18px rgba(20,33,61,.3)' }} />
    <div style={{ position: 'absolute', left: 0, top: 0, width: 230, height: 230, borderRadius: 230, border: `20px solid ${C.ink}`, background: 'radial-gradient(circle at 35% 30%, rgba(255,255,255,.55), rgba(220,235,255,.12) 55%, rgba(255,255,255,.05))', boxShadow: '10px 16px 26px rgba(20,33,61,.28), inset 0 0 18px rgba(255,255,255,.6)' }} />
  </div>
);

// ---------------------------------------------------------------- checklist card
// Plan facts only (from the brand and content files). Used when a beat talks about what the plan includes.
const FACTS: [RegExp, string, string][] = [
  [/hosting/i, 'Hosting', 'No separate bill for it'], [/changes?\b/i, 'Changes', 'Up to 5 a month, sent on WhatsApp'], [/report/i, 'Monthly report', 'One page, in plain words'],
  [/domain/i, 'Your domain', 'Registered in your name'], [/whatsapp and call|call buttons?/i, 'WhatsApp and call buttons', 'From the first day'],
  [/7 days|seven days/i, 'Built in 7 days', 'From first call to live'], [/setup fee/i, 'No setup fee', 'Nothing extra to start'], [/month to month|notice/i, 'Month to month', "One month's notice to stop"],
];

export const Checklist: React.FC<{ c: Ctx }> = ({ c }) => {
  const parts = plain(c.s.show).split(/,\s+|\s+and\s+|\s*\+\s*/).map((x) => x.trim()).filter(Boolean);
  const facts = c.p.pillar !== 'teach' ? FACTS.filter(([r]) => r.test(c.s.say)) : [];
  const lines = c.p.segs.filter((x) => x.kind === 'line');
  const cur = Math.max(0, (c.s.n || 1) - 1);
  const split = facts.length >= 2 || parts.length >= 3;
  const rows = facts.length >= 2 ? facts.slice(0, 4).map(([, t, sub]) => ({ t, sub, state: 'done' as const }))
    : parts.length >= 3 ? parts.slice(0, 4).map((t) => ({ t: cap(t), sub: (FACTS.find(([r]) => r.test(t)) || [null, '', ''])[2], state: 'done' as const }))
    : lines.map((l, k) => ({ t: plain(l.show), sub: '', state: k < cur ? 'done' as const : k === cur ? 'now' as const : 'next' as const }));
  const rh = split ? 148 : 132;
  const h = rows.length * rh + 90;
  return (
    <AbsoluteFill>
      <Top c={c} />
      <Obj x={80} y={620} w={920} h={h} rot={-1.2} delay={6} radius={40} style={{ background: C.card }}>
        <div style={{ padding: '58px 50px 30px' }}>
          {rows.map((r, k) => {
            const d = 14 + k * 8;
            const on = r.state !== 'next';
            return (
              <Row key={k} delay={d} last={k === rows.length - 1} h={rh}>
                <Tick size={66} delay={r.state === 'now' ? 30 : d + 6} on={on} />
                <div style={{ marginLeft: 30, opacity: r.state === 'next' ? 0.32 : 1 }}>
                  <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 46, letterSpacing: '-0.03em', color: C.ink, lineHeight: 1.05 }}>{r.t}</div>
                  {r.sub ? <div style={{ fontFamily: SANS, fontWeight: 500, fontSize: 30, color: C.muted, marginTop: 8 }}>{r.sub}</div> : null}
                </div>
              </Row>
            );
          })}
        </div>
      </Obj>
      <Obj x={120} y={592} w={split ? 260 : 300} h={58} rot={-3} delay={12} radius={999} dots={false} shadow={false} dist={80} z={10}>
        <Pill text={split ? 'INCLUDED' : 'STEP BY STEP'} size={24} />
      </Obj>
    </AbsoluteFill>
  );
};

const Row: React.FC<{ delay: number; last: boolean; h: number; children: React.ReactNode }> = ({ delay, last, h, children }) => {
  const p = useSpring(delay, 'soft');
  return (
    <div style={{ height: h, display: 'flex', alignItems: 'center', borderBottom: last ? 'none' : `2px solid ${C.faint}`, opacity: p, transform: `translateX(${(1 - p) * 40}px)` }}>{children}</div>
  );
};

// ---------------------------------------------------------------- Google style search result
export const Google: React.FC<{ c: Ctx }> = ({ c }) => {
  const f = useCurrentFrame();
  const n = nicheOf(c);
  const q = `${n} near me`;
  const neg = c.s.mood === 'neg';
  const grow = lerp(f, 34, 48);
  const others = [`${cap(n)} in your area`, `A ${n} down the road`, `Directory: ${n} listings`];
  const g = useSpring(44, 'drop');
  return (
    <AbsoluteFill>
      <Top c={c} />
      <Obj x={70} y={600} w={940} h={736} rot={0.8} delay={4} radius={40} style={{ background: C.card, overflow: 'hidden' }}>
        <div style={{ position: 'absolute', left: 40, top: 40, width: 860, height: 96, borderRadius: 48, border: `2px solid ${C.faint}`, boxShadow: '0 6px 18px rgba(20,33,61,.08)', display: 'flex', alignItems: 'center', padding: '0 34px', gap: 22 }}>
          <Icon name="search" size={42} delay={6} stroke={2.4} />
          <div style={{ fontFamily: SANS, fontWeight: 600, fontSize: 40, color: C.ink, letterSpacing: '-0.02em' }}>{typed(f, q, 10)}<span style={{ color: C.acc, opacity: f % 16 < 8 ? 1 : 0 }}>|</span></div>
        </div>
        <div style={{ position: 'absolute', left: 64, top: 166, display: 'flex', gap: 40, fontFamily: SANS, fontSize: 24, color: C.muted }}>
          <span style={{ color: C.ink, borderBottom: `4px solid ${C.acc}`, paddingBottom: 8 }}>All</span><span>Maps</span><span>Images</span><span>News</span>
        </div>
        <div style={{ position: 'absolute', left: 40, top: 230, width: 860 }}>
          {!neg ? (
            <div style={{ height: 196 * grow, overflow: 'hidden', opacity: grow }}>
              <div style={{ margin: '0 0 22px', padding: '22px 26px', borderRadius: 24, background: C.cream, borderLeft: `10px solid ${C.acc}` }}>
                <Result title={`Your ${cap(n)} | Prices, hours, bookings`} domain={domainOf(c)} strong />
                <div style={{ display: 'flex', gap: 14, marginTop: 14 }}>{['Call', 'WhatsApp', 'Directions'].map((x) => <span key={x} style={{ fontFamily: SANS, fontWeight: 700, fontSize: 24, color: C.ink, border: `2px solid ${C.faint}`, borderRadius: 999, padding: '6px 18px', background: '#fff' }}>{x}</span>)}</div>
              </div>
            </div>
          ) : null}
          {others.slice(0, neg ? 3 : 2).map((t, k) => <Fade key={k} delay={14 + k * 6}><div style={{ padding: '12px 26px', marginBottom: 2 }}><Result title={t} domain={`listing-${k + 1}.co.za`} /></div></Fade>)}
          {neg ? (
            <Fade delay={40}>
              <div style={{ margin: '10px 0 0', padding: '22px 26px', borderRadius: 24, border: `4px dashed ${C.acc}`, display: 'flex', alignItems: 'center', gap: 22 }}>
                <Cross size={56} delay={46} />
                <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 36, color: C.ink, letterSpacing: '-0.02em' }}>Your {n}? <span style={{ fontFamily: SERIF, fontStyle: 'italic', fontWeight: 400, color: C.acc }}>Nowhere.</span></div>
              </div>
            </Fade>
          ) : null}
        </div>
      </Obj>
      {neg ? <div style={{ position: 'absolute', left: 560 + 120 * Math.sin(f / 30), top: 930 + 60 * Math.cos(f / 23), opacity: g, transform: `translateY(${(1 - g) * -240}px) rotate(-24deg) scale(.82)`, zIndex: 50 }}><Magnifier /></div>
        : <Stamp text="THAT'S YOU" x={650} y={1200} delay={50} rot={-8} size={46} />}
    </AbsoluteFill>
  );
};

const Result: React.FC<{ title: string; domain: string; strong?: boolean }> = ({ title, domain, strong }) => (
  <div style={{ display: 'flex', gap: 20 }}>
    <div style={{ width: 46, height: 46, borderRadius: 46, background: strong ? C.acc : C.bar, flexShrink: 0, marginTop: 4 }} />
    <div style={{ flex: 1 }}>
      <div style={{ fontFamily: SANS, fontSize: 21, color: C.muted }}>{domain}</div>
      <div style={{ fontFamily: SANS, fontWeight: strong ? 800 : 700, fontSize: 33, color: strong ? C.ink : C.soft, letterSpacing: '-0.02em', marginTop: 2 }}>{title}</div>
      {!strong ? <div style={{ marginTop: 10, height: 14, width: '86%', borderRadius: 8, background: C.bar }} /> : null}
    </div>
  </div>
);

const Fade: React.FC<{ delay: number; children: React.ReactNode }> = ({ delay, children }) => {
  const p = useSpring(delay, 'soft');
  return <div style={{ opacity: p, transform: `translateY(${(1 - p) * 26}px)` }}>{children}</div>;
};

// ---------------------------------------------------------------- WhatsApp style chat
const question = (t: string, n: string) =>
  /price|cost|charge|how much/.test(t) ? 'Hi, how much do you charge?' : /hour|open|holiday|weekend/.test(t) ? 'Hi! Are you open this Saturday?' : /book|appointment|slot/.test(t) ? 'Hi, can I book for Friday?'
    : /where|address|location|direction/.test(t) ? 'Hi, where are you based?' : /quote/.test(t) ? 'Hi, can I get a quote please?' : /menu/.test(t) ? 'Hi, do you have a menu?' : `Hi, how much do you charge?`;

export const WhatsApp: React.FC<{ c: Ctx }> = ({ c }) => {
  const f = useCurrentFrame();
  const n = nicheOf(c);
  const neg = c.s.mood === 'neg';
  const q = question(text(c), n);
  const typing = f > 8 && f < 22;
  return (
    <AbsoluteFill>
      <Top c={c} />
      <Obj x={250} y={600} w={580} h={720} rot={-2} delay={4} radius={70} style={{ background: C.ink, padding: 16 }}>
        <div style={{ width: '100%', height: '100%', borderRadius: 56, overflow: 'hidden', background: '#EFE7DB', position: 'relative' }}>
          <div style={{ position: 'absolute', inset: 0, ...halftone(0.05, 14) }} />
          <div style={{ position: 'relative', height: 112, background: '#F8F6F1', display: 'flex', alignItems: 'center', gap: 18, padding: '18px 28px 0', borderBottom: `2px solid ${C.faint}` }}>
            <div style={{ width: 62, height: 62, borderRadius: 62, background: '#C9D3E6', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: SANS, fontWeight: 800, fontSize: 28, color: C.ink }}>C</div>
            <div><div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 30, color: C.ink }}>Customer</div>
              <div style={{ fontFamily: SANS, fontSize: 22, color: typing ? C.wa : C.muted }}>{typing ? 'typing...' : 'online'}</div></div>
          </div>
          <div style={{ position: 'relative', padding: '26px 22px', display: 'flex', flexDirection: 'column', gap: 16 }}>
            {typing ? <Bubble side="in" delay={9}><Dots /></Bubble> : null}
            {f >= 22 ? <Bubble side="in" delay={22} time="09:14">{q}</Bubble> : null}
            {neg ? (
              <>
                {f >= 50 ? <Bubble side="out" delay={50} time="13:20">Sorry, only seeing this now!</Bubble> : null}
                {f >= 68 ? <Bubble side="in" delay={68} time="13:21">No stress, I found someone else.</Bubble> : null}
              </>
            ) : (
              <>
                {f >= 34 ? <Bubble side="out" delay={34} time="09:14">Hi! It is all on our page:</Bubble> : null}
                {f >= 44 ? <Bubble side="out" delay={44}><LinkCard title={`Your ${cap(n)}`} domain={domainOf(c)} /></Bubble> : null}
                {f >= 64 ? <Bubble side="in" delay={64} time="09:15">Perfect, thank you!</Bubble> : null}
              </>
            )}
          </div>
        </div>
      </Obj>
      {neg ? <Obj x={50} y={1140} w={270} h={180} rot={-7} delay={38} radius={4} z={60} style={{ background: C.sticky, padding: '24px 26px' }}>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 22, color: 'rgba(20,33,61,.6)', letterSpacing: '0.1em' }}>MEANWHILE</div>
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 44, color: C.ink, letterSpacing: '-0.03em', lineHeight: 1 }}>4 hours<br />later</div>
      </Obj> : <Stamp text="ANSWERED" x={90} y={1130} delay={52} rot={-9} color={C.ink} size={44} />}
    </AbsoluteFill>
  );
};

const Bubble: React.FC<{ side: 'in' | 'out'; delay: number; time?: string; dark?: boolean; children: React.ReactNode }> = ({ side, delay, time, dark, children }) => {
  const p = useSpring(delay, 'pop');
  const out = side === 'out';
  return (
    <div style={{ alignSelf: out ? 'flex-end' : 'flex-start', maxWidth: 430, transformOrigin: out ? 'right bottom' : 'left bottom', transform: `scale(${0.7 + 0.3 * p}) translateY(${(1 - p) * 20}px)`, opacity: interpolate(p, [0, 0.3], [0, 1], clamp),
      background: dark ? C.ink : out ? C.waBubble : '#fff', borderRadius: out ? '26px 26px 6px 26px' : '26px 26px 26px 6px', padding: '16px 22px', boxShadow: '0 2px 4px rgba(20,33,61,.1)',
      fontFamily: SANS, fontWeight: 500, fontSize: 30, lineHeight: 1.22, color: dark ? C.cream : C.ink }}>
      {children}
      {time ? <div style={{ textAlign: 'right', fontSize: 18, color: C.muted, marginTop: 4 }}>{time}{out ? <span style={{ color: '#6E9CC8' }}> ✓✓</span> : null}</div> : null}
    </div>
  );
};

const Dots: React.FC = () => {
  const f = useCurrentFrame();
  return <div style={{ display: 'flex', gap: 8, padding: '6px 4px' }}>{[0, 1, 2].map((k) => <div key={k} style={{ width: 14, height: 14, borderRadius: 14, background: C.muted, transform: `translateY(${Math.sin((f - k * 4) / 3) * 4}px)` }} />)}</div>;
};

const LinkCard: React.FC<{ title: string; domain: string }> = ({ title, domain }) => (
  <div style={{ width: 380, borderRadius: 18, overflow: 'hidden', background: '#fff', border: `2px solid ${C.faint}` }}>
    <div style={{ height: 120, background: C.ink, padding: '20px 22px', position: 'relative' }}>
      <div style={{ fontFamily: SERIF, fontStyle: 'italic', fontSize: 40, color: '#fff' }}>{title}</div>
      <div style={{ position: 'absolute', left: 22, bottom: 18, width: 120, height: 26, borderRadius: 26, background: 'rgba(242,235,221,.55)' }} />
    </div>
    <div style={{ padding: '12px 18px' }}>
      <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 26 }}>Prices, hours and booking</div>
      <div style={{ fontFamily: SANS, fontSize: 19, color: C.muted }}>{domain}</div>
    </div>
  </div>
);

// ---------------------------------------------------------------- site built block by block on a phone
export const SiteBuild: React.FC<{ c: Ctx }> = ({ c }) => {
  const f = useCurrentFrame();
  const n = nicheOf(c);
  const url = domainOf(c);
  const blocks = [
    { y: 84, h: 52, d: 10, tag: null },
    { y: 148, h: 220, d: 18, tag: 'what you do' },
    { y: 380, h: 158, d: 28, tag: 'your prices' },
    { y: 550, h: 72, d: 38, tag: 'WhatsApp + call' },
  ];
  const bx = 400;
  const by = 600;
  return (
    <AbsoluteFill>
      <Top c={c} />
      <Obj x={bx} y={by} w={480} h={700} rot={1.5} delay={4} radius={62} style={{ background: C.ink, padding: 14 }}>
        <div style={{ width: '100%', height: '100%', borderRadius: 50, overflow: 'hidden', background: '#FBFAF7', position: 'relative' }}>
          <div style={{ position: 'absolute', left: 14, top: 14, right: 14, height: 54, borderRadius: 27, background: '#ECE9E2', display: 'flex', alignItems: 'center', gap: 10, padding: '0 20px', fontFamily: SANS, fontSize: 20, color: C.ink }}>
            <Icon name="lock" size={20} delay={6} stroke={2.6} />{typed(f, url, 6, 1)}
          </div>
          {blocks.map((b, k) => <Block key={k} y={b.y} h={b.h} delay={b.d} k={k} n={n} />)}
          <Block y={634} h={44} delay={48} k={4} n={n} />
        </div>
      </Obj>
      {blocks.filter((b) => b.tag).map((b, k) => (
        <Obj key={k} x={70} y={by + 14 + b.y + b.h / 2 - 40} w={290} h={80} rot={k % 2 ? 2 : -2} delay={b.d + 6} radius={10} from="left" dist={180} style={{ background: '#fff', display: 'flex', alignItems: 'center', gap: 12, padding: '0 20px' }}>
          <div style={{ width: 16, height: 16, borderRadius: 16, background: C.acc, flexShrink: 0 }} />
          <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 24, color: C.ink, whiteSpace: 'nowrap' }}>{b.tag}</div>
          <Arrow delay={b.d + 14} />
        </Obj>
      ))}
    </AbsoluteFill>
  );
};

const Arrow: React.FC<{ delay: number }> = ({ delay }) => {
  const f = useCurrentFrame();
  const p = interpolate(f - delay, [0, 10], [0, 1], { ...clamp, easing: ease });
  return (
    <svg width={90} height={40} viewBox="0 0 90 40" style={{ position: 'absolute', right: -84, top: 20, overflow: 'visible' }}>
      <path d="M2 20 C 30 6, 56 30, 84 18 M72 8 L 86 18 L 72 28" pathLength={1} fill="none" stroke={C.acc} strokeWidth={4} strokeLinecap="round" strokeLinejoin="round" strokeDasharray={1} strokeDashoffset={1 - p} />
    </svg>
  );
};

const Block: React.FC<{ y: number; h: number; delay: number; k: number; n: string }> = ({ y, h, delay, k, n }) => {
  const p = useSpring(delay, 'drop');
  const st: React.CSSProperties = { position: 'absolute', left: 18, right: 18, top: y, height: h, opacity: interpolate(p, [0, 0.3], [0, 1], clamp),
    transform: `translateY(${(1 - p) * -90}px) rotate(${(1 - p) * (k % 2 ? 5 : -5)}deg)` };
  if (k === 0) return <div style={{ ...st, display: 'flex', alignItems: 'center', gap: 14 }}><div style={{ width: 36, height: 36, borderRadius: 36, background: C.acc }} /><div style={{ width: 130, height: 16, borderRadius: 8, background: C.ink }} /><div style={{ flex: 1 }} />{[0, 1, 2].map((i) => <div key={i} style={{ width: 34, height: 5, borderRadius: 3, background: C.ink, marginTop: i ? 0 : 0 }} />)}</div>;
  if (k === 1) return <div style={{ ...st, borderRadius: 24, background: C.ink, padding: '28px 26px' }}>
    <div style={{ fontFamily: SERIF, fontStyle: 'italic', fontSize: 54, color: '#fff', lineHeight: 1 }}>Your {n}</div>
    <div style={{ width: '70%', height: 14, borderRadius: 8, background: 'rgba(255,255,255,.3)', marginTop: 18 }} />
    <div style={{ width: '50%', height: 14, borderRadius: 8, background: 'rgba(255,255,255,.3)', marginTop: 10 }} />
    <div style={{ position: 'absolute', left: 26, bottom: 24, background: C.cream, color: C.ink, fontFamily: SANS, fontWeight: 800, fontSize: 22, padding: '10px 22px', borderRadius: 999 }}>Book now</div></div>;
  if (k === 2) return <div style={st}>{[0, 1, 2].map((i) => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 14, height: 52, borderBottom: i < 2 ? `2px solid ${C.faint}` : 'none' }}>
    <div style={{ width: 150 + i * 30, height: 16, borderRadius: 8, background: C.ink, opacity: 0.8 }} /><div style={{ flex: 1 }} /><div style={{ width: 80, height: 30, borderRadius: 15, background: C.bar }} /></div>)}</div>;
  if (k === 3) return <div style={{ ...st, display: 'flex', gap: 12 }}>
    <div style={{ flex: 1, borderRadius: 18, background: C.wa, color: '#fff', fontFamily: SANS, fontWeight: 800, fontSize: 26, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10 }}><Icon name="chat" size={28} color="#fff" delay={delay + 4} stroke={2.6} />WhatsApp</div>
    <div style={{ flex: 1, borderRadius: 18, background: C.ink, color: '#fff', fontFamily: SANS, fontWeight: 800, fontSize: 26, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10 }}><Icon name="phone" size={26} color="#fff" delay={delay + 4} stroke={2.6} />Call</div></div>;
  return <div style={{ ...st, left: 22, right: 30, display: 'flex', alignItems: 'center', gap: 10, fontFamily: SANS, fontSize: 19, color: C.muted }}><Icon name="clock" size={26} delay={delay + 2} />Mon to Sat<div style={{ flex: 1 }} /><Icon name="pin" size={26} delay={delay + 4} color={C.acc} /><span style={{ marginRight: 6 }}>Map</span></div>;
};

// ---------------------------------------------------------------- before and after
export const BeforeAfter: React.FC<{ c: Ctx }> = ({ c }) => {
  const f = useCurrentFrame();
  const n = nicheOf(c);
  const load = Math.min(0.62, interpolate(f, [12, 60], [0, 0.62], clamp));
  return (
    <AbsoluteFill>
      <Top c={c} />
      <Obj x={70} y={600} w={170} h={50} rot={-3} delay={6} radius={999} dots={false} shadow={false} z={10}><Pill text="BEFORE" bg={C.ink} size={22} /></Obj>
      <Obj x={70} y={650} w={410} h={640} rot={-3} delay={4} radius={22} style={{ background: '#E7DFCF', overflow: 'hidden' }}>
        <div style={{ height: 58, background: '#A99F8B', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 'Times New Roman, serif', fontSize: 20, color: '#F5F0E6', letterSpacing: '0.1em' }}>WELCOME TO OUR WEBSITE!!</div>
        <div style={{ margin: 18, height: 150, border: '2px dashed #B4AA96', display: 'flex', alignItems: 'center', justifyContent: 'center' }}><Icon name="image" size={60} color="#B4AA96" delay={10} /></div>
        {Array.from({ length: 9 }).map((_, i) => <div key={i} style={{ margin: '0 18px 10px', height: 9, width: `${70 + ((i * 37) % 28)}%`, background: '#C3B9A5', borderRadius: 3 }} />)}
        <div style={{ position: 'absolute', left: 30, right: 30, bottom: 60, height: 120, borderRadius: 12, background: C.cream, padding: '18px 20px', boxShadow: '0 4px 12px rgba(0,0,0,.12)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, fontFamily: SANS, fontSize: 20, color: C.muted }}>
            <div style={{ transform: `rotate(${Math.floor(f / 10) * 180}deg)` }}><Icon name="hourglass" size={28} color={C.muted} delay={8} /></div>Loading...</div>
          <div style={{ marginTop: 18, height: 14, borderRadius: 7, background: '#E2D9C7' }}><div style={{ width: `${load * 100}%`, height: '100%', borderRadius: 7, background: '#A99F8B' }} /></div>
        </div>
      </Obj>
      <Obj x={524} y={588} w={150} h={50} rot={2} delay={20} radius={999} dots={false} shadow={false} z={10} from="right"><Pill text="AFTER" size={22} /></Obj>
      <Obj x={524} y={638} w={410} h={640} rot={2} delay={16} radius={22} from="right" dist={320} style={{ background: '#fff', overflow: 'hidden' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '18px 20px' }}><div style={{ width: 26, height: 26, borderRadius: 26, background: C.acc }} /><div style={{ width: 110, height: 12, borderRadius: 6, background: C.ink }} /></div>
        <div style={{ margin: '0 18px', height: 210, borderRadius: 20, background: C.ink, padding: '24px 22px', position: 'relative' }}>
          <div style={{ fontFamily: SERIF, fontStyle: 'italic', fontSize: 50, color: '#fff', lineHeight: 1 }}>Your {n}</div>
          <div style={{ width: '64%', height: 12, borderRadius: 6, background: 'rgba(255,255,255,.3)', marginTop: 16 }} />
          <div style={{ position: 'absolute', left: 22, bottom: 22, background: C.cream, color: C.ink, fontFamily: SANS, fontWeight: 800, fontSize: 20, padding: '9px 18px', borderRadius: 999 }}>Book now</div>
        </div>
        {[0, 1, 2].map((i) => <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 14, margin: '16px 22px 0' }}><Tick size={34} delay={30 + i * 5} /><div style={{ height: 14, width: 170 + i * 30, borderRadius: 7, background: C.ink, opacity: 0.75 }} /></div>)}
        <div style={{ display: 'flex', gap: 10, margin: '26px 18px 0' }}>
          <div style={{ flex: 1, height: 62, borderRadius: 16, background: C.wa, color: '#fff', fontFamily: SANS, fontWeight: 800, fontSize: 22, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>WhatsApp</div>
          <div style={{ flex: 1, height: 62, borderRadius: 16, background: C.ink, color: '#fff', fontFamily: SANS, fontWeight: 800, fontSize: 22, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Call</div>
        </div>
      </Obj>
      <Stamp text="SLOW" x={150} y={1150} delay={44} rot={-14} size={58} />
      <Stamp text="CLEAR" x={640} y={1150} delay={54} rot={-8} size={58} color={C.ink} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- price card
// Prices are never rolled or counted: only the real figure from the brand file is ever on screen. It slams in instead.
const Money: React.FC<{ v: string; delay: number; style: React.CSSProperties }> = ({ v, delay, style }) => {
  const p = useSpring(delay, 'pop');
  return <div style={{ ...style, opacity: interpolate(p, [0, 0.3], [0, 1], clamp), transform: `scale(${1.35 - 0.35 * p}) rotate(${(1 - p) * -4}deg)`, transformOrigin: 'left bottom' }}>{v}</div>;
};

export const Price: React.FC<{ c: Ctx }> = ({ c }) => {
  const f = useCurrentFrame();
  const plans = c.p.plans || [];
  const studio = plans[0];
  const show = plans[1];
  if (!studio) return <Kinetic c={c} />;
  const both = !!show && /R ?5,?000|showroom|bigger/i.test(text(c));
  if (!both) {
    return (
      <AbsoluteFill>
        <Top c={c} />
        <Obj x={100} y={610} w={880} h={700} rot={-1.5} delay={4} radius={44} style={{ background: C.card, padding: '64px 58px' }}>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 18 }}>
            <Money v={studio.price} delay={10} style={{ fontFamily: SANS, fontWeight: 900, fontSize: 150, letterSpacing: '-0.06em', color: C.ink, lineHeight: 0.9 }} />
            <div style={{ fontFamily: SERIF, fontStyle: 'italic', fontSize: 66, color: C.acc }}>{studio.per}</div>
          </div>
          <div style={{ height: 0, borderTop: `3px dashed ${C.faint}`, margin: '30px 0 16px' }} />
          {studio.items.slice(0, 6).map((it, k) => <Fade key={k} delay={22 + k * 5}><div style={{ display: 'flex', alignItems: 'center', gap: 22, height: 58 }}><Tick size={42} delay={26 + k * 5} /><div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 36, color: C.ink, letterSpacing: '-0.02em' }}>{it}</div></div></Fade>)}
          <div style={{ position: 'absolute', left: 58, bottom: 34, fontFamily: SANS, fontSize: 23, color: C.muted, letterSpacing: '0.04em' }}>{studio.note}</div>
        </Obj>
        <Obj x={140} y={580} w={330} h={58} rot={-4} delay={10} radius={999} dots={false} shadow={false} z={10}><Pill text={`${studio.name.toUpperCase()} PLAN`} size={24} /></Obj>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill>
      <Top c={c} />
      {[studio, show].map((pl, k) => (
        <React.Fragment key={k}>
          <Obj x={90} y={610 + k * 360} w={900} h={320} rot={k ? 1.5 : -1.5} delay={4 + k * 14} radius={36} from={k ? 'right' : 'top'} style={{ background: k ? C.ink : C.card, padding: '58px 46px 30px', display: 'flex', gap: 34 }}>
            <div style={{ width: 380, flexShrink: 0 }}>
              <Money v={pl.price} delay={10 + k * 14} style={{ fontFamily: SANS, fontWeight: 900, fontSize: 112, letterSpacing: '-0.06em', color: k ? C.cream : C.ink, lineHeight: 0.9 }} />
              <div style={{ fontFamily: SERIF, fontStyle: 'italic', fontSize: 50, color: k ? C.cream : C.acc, marginTop: 6 }}>{pl.per}</div>
              <div style={{ fontFamily: SANS, fontSize: 20, color: k ? 'rgba(242,235,221,.7)' : C.muted, marginTop: 14 }}>{pl.note}</div>
            </div>
            <div style={{ flex: 1 }}>{pl.items.slice(0, 4).map((it, j) => <div key={j} style={{ display: 'flex', alignItems: 'center', gap: 14, height: 54 }}><Tick size={32} delay={18 + k * 14 + j * 4} /><div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 27, color: k ? C.cream : C.ink }}>{it}</div></div>)}</div>
          </Obj>
          <Obj x={130} y={584 + k * 360} w={290} h={54} rot={k ? 2 : -4} delay={10 + k * 14} radius={999} dots={false} shadow={false} z={10}><Pill text={pl.name.toUpperCase()} size={22} bg={k ? C.cream : C.acc} fg={k ? C.ink : C.cream} /></Obj>
        </React.Fragment>
      ))}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- day 1 to day 7 timeline
export const Timeline: React.FC<{ c: Ctx }> = ({ c }) => {
  const f = useCurrentFrame();
  const line = interpolate(f, [10, 46], [0, 1], { ...clamp, easing: ease });
  const steps: [string, string][] = [['DAY 1', 'First call. Domain in your name.'], ['DAY 2 TO 6', 'Your pages get built.'], ['DAY 7', 'Live, with WhatsApp and call buttons.']];
  return (
    <AbsoluteFill>
      <Top c={c} />
      <div style={{ position: 'absolute', left: 100, top: 812, width: 880 * line, height: 6, borderRadius: 3, background: C.ink }} />
      {Array.from({ length: 7 }).map((_, k) => {
        const d = 8 + k * 5;
        const live = k === 6;
        return (
          <Obj key={k} x={89 + k * 131} y={620} w={116} h={160} rot={((k * 37) % 7) - 3} delay={d} radius={14} style={{ background: live ? C.acc : C.card, overflow: 'hidden' }}>
            <div style={{ height: 38, background: live ? C.soft : C.ink, color: C.cream, fontFamily: SANS, fontWeight: 700, fontSize: 18, letterSpacing: '0.2em', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>DAY</div>
            <div style={{ fontFamily: COND, fontSize: 76, color: live ? C.cream : C.ink, textAlign: 'center', lineHeight: 1.45 }}>{k + 1}</div>
            {!live ? <div style={{ position: 'absolute', right: 6, bottom: 6 }}><Tick size={30} delay={d + 22} /></div> : null}
          </Obj>
        );
      })}
      {steps.map(([d, t], k) => (
        <Obj key={k} x={90} y={870 + k * 140} w={900} h={118} rot={k === 1 ? 1 : -0.8} delay={34 + k * 9} radius={24} from="left" dist={300} style={{ background: C.card, display: 'flex', alignItems: 'center', gap: 26, padding: '0 30px' }}>
          <Pill text={d} size={20} bg={k === 2 ? C.acc : C.ink} />
          <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 36, color: C.ink, letterSpacing: '-0.02em' }}>{t}</div>
        </Obj>
      ))}
      <Stamp text="LIVE" x={850} y={598} delay={58} rot={12} size={44} color={C.ink} />
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- icon grid
const CAT: [string, string, RegExp][] = [
  ['globe', 'Website', /website|site\b|online|homepage/], ['search', 'Google', /google|search|found|find you|near me/], ['chat', 'WhatsApp', /whatsapp|message|chat|\bdm\b|enquir/],
  ['phone', 'Call button', /\bcall|phone number/], ['calendar', 'Bookings', /book/], ['clock', 'Hours', /hour|open|holiday|weekend/], ['pin', 'Location', /address|location|where|map|direction|suburb|area/],
  ['tag', 'Prices', /price|cost|rand|r\d/], ['link', 'Your domain', /domain|link|url/], ['report', 'Monthly report', /report/], ['pencil', 'Changes', /change|update|edit/],
  ['server', 'Hosting', /hosting/], ['shield', 'Trust', /trust|safe|legit|real business/], ['image', 'Photos', /photo|picture|gallery|your work/], ['star', 'Reviews', /review/],
  ['help', 'FAQs', /question|faq/], ['mail', 'Email', /email/], ['lock', 'Secure', /padlock|https|secure/], ['phoneDevice', 'Mobile', /mobile|on a phone|thumb|screen/], ['zap', 'Fast', /fast|speed|slow|load/],
];

export const Icons: React.FC<{ c: Ctx }> = ({ c }) => {
  const t = text(c);
  const hit = CAT.filter(([, , r]) => r.test(t));
  const pick = [...hit, ...CAT.filter((x) => !hit.includes(x) && ['globe', 'search', 'chat', 'phone', 'pin', 'clock', 'tag', 'calendar'].includes(x[0]))].slice(0, 6);
  return (
    <AbsoluteFill>
      <Top c={c} />
      {pick.map(([ic, lb], k) => {
        const on = hit.includes(pick[k]);
        const x = 92 + (k % 3) * 302;
        const y = 610 + Math.floor(k / 3) * 330;
        const d = 8 + k * 5;
        return (
          <Obj key={k} x={x} y={y} w={272} h={296} rot={((k * 53) % 5) - 2} delay={d} radius={36} style={{ background: C.card, border: on ? `4px solid ${C.acc}` : '4px solid transparent', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 26 }}>
            <Icon name={ic} size={104} color={on ? C.acc : C.ink} delay={d + 6} stroke={1.8} />
            <div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 32, color: C.ink, letterSpacing: '-0.02em' }}>{lb}</div>
            {on ? <div style={{ position: 'absolute', right: 22, top: 22 }}><Tick size={36} delay={d + 16} /></div> : null}
          </Obj>
        );
      })}
    </AbsoluteFill>
  );
};

// ---------------------------------------------------------------- site footage inside a pinned polaroid
export const Footage: React.FC<{ c: Ctx }> = ({ c }) => {
  const f = useCurrentFrame();
  const clip = c.s.clip ? staticFile(c.s.clip) : null;
  return (
    <AbsoluteFill>
      <Top c={c} />
      <Obj x={70} y={600} w={940} h={700} rot={0.5} delay={2} radius={22} dots={false} style={{ background: C.kraft, ...halftone(0.07, 12), border: `14px solid ${C.cream}`, boxShadow: 'inset 0 0 40px rgba(20,33,61,.12), 0 20px 50px rgba(20,33,61,.2)' }} />
      <Obj x={200} y={640} w={460} h={630} rot={-4} delay={10} radius={4} style={{ background: '#FDFCF8', padding: '22px 22px 0' }}>
        <div style={{ width: '100%', height: 500, background: C.ink, overflow: 'hidden', position: 'relative' }}>
          {clip ? <OffthreadVideo src={clip} startFrom={c.s.clipFrom || 0} muted style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'top' }} /> : <MiniSite n={nicheOf(c)} />}
          <div style={{ position: 'absolute', inset: 0, background: `linear-gradient(${120 + 10 * Math.sin(f / 30)}deg, rgba(255,255,255,.18), transparent 40%)` }} />
        </div>
        <div style={{ fontFamily: SERIF, fontStyle: 'italic', fontSize: 44, color: C.ink, textAlign: 'center', marginTop: 22 }}>{`your ${nicheOf(c)}`}</div>
      </Obj>
      <Pin x={430} y={662} delay={22} />
      <Obj x={660} y={760} w={300} h={260} rot={6} delay={20} radius={4} style={{ background: C.sticky, padding: 28 }}>
        <div style={{ fontFamily: SANS, fontWeight: 700, fontSize: 20, letterSpacing: '0.12em', color: 'rgba(20,33,61,.6)' }}>ON A PHONE</div>
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 40, lineHeight: 1.02, letterSpacing: '-0.03em', color: C.ink, marginTop: 12 }}>Fast, clear, one tap to call</div>
      </Obj>
      <Tape x={740} y={740} w={140} rot={8} delay={26} />
    </AbsoluteFill>
  );
};

const MiniSite: React.FC<{ n: string }> = ({ n }) => (
  <div style={{ padding: 24, background: '#FBFAF7', height: '100%' }}>
    <div style={{ height: 180, borderRadius: 18, background: C.ink, padding: 22 }}><div style={{ fontFamily: SERIF, fontStyle: 'italic', fontSize: 46, color: '#fff' }}>Your {n}</div></div>
    {[0, 1, 2].map((i) => <div key={i} style={{ height: 14, width: `${80 - i * 12}%`, background: C.bar, borderRadius: 7, marginTop: 22 }} />)}
  </div>
);

// ---------------------------------------------------------------- CTA card
export const Cta: React.FC<{ c: Ctx }> = ({ c }) => {
  const f = useCurrentFrame();
  const wa = c.p.cta?.channel === 'whatsapp';
  const msg = c.p.cta?.text || 'SITE';
  const t0 = 30;
  const typedN = Math.max(0, Math.min(msg.length, Math.floor((f - t0) / 1.6)));
  const sentAt = t0 + msg.length * 1.6 + 8;
  const sent = f > sentAt;
  const phone = c.p.brand.phone || '065 027 6518';
  return (
    <AbsoluteFill>
            <Head show={c.s.show} top={252} underline />
      <Obj x={90} y={560} w={190} h={190} rot={-5} delay={8} radius={46} style={{ background: C.ink, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ fontFamily: SERIF, fontStyle: 'italic', fontSize: 104, color: C.cream, lineHeight: 1 }}>SV</div>
      </Obj>
      <Fade delay={14}><div style={{ position: 'absolute', left: 320, top: 600 }}>
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 58, letterSpacing: '-0.04em', color: C.ink }}>{c.p.brand.name}</div>
        <div style={{ fontFamily: SANS, fontSize: 26, color: C.muted, marginTop: 6 }}>{wa ? `WhatsApp ${phone}` : c.p.brand.handle || '@stolenvalour.co.za'}</div>
      </div></Fade>
      <Obj x={90} y={810} w={900} h={380} rot={1.2} delay={16} radius={40} style={{ background: C.card, padding: 34 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 18, paddingBottom: 24, borderBottom: `2px solid ${C.faint}` }}>
          <div style={{ width: 64, height: 64, borderRadius: 64, background: C.ink, color: C.cream, fontFamily: SERIF, fontStyle: 'italic', fontSize: 34, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>SV</div>
          <div><div style={{ fontFamily: SANS, fontWeight: 800, fontSize: 30, color: C.ink }}>{wa ? c.p.brand.name : c.p.brand.handle || '@stolenvalour.co.za'}</div>
            <div style={{ fontFamily: SANS, fontSize: 22, color: C.muted }}>{wa ? phone : 'Message'}</div></div>
        </div>
        <div style={{ height: 120, display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
          {sent ? <Bubble side="out" delay={Math.ceil(sentAt)} dark={!wa}><span style={{ fontWeight: 800, fontSize: 38 }}>{msg}</span></Bubble> : null}
        </div>
        <div style={{ height: 80, borderRadius: 40, background: C.cream, display: 'flex', alignItems: 'center', padding: '0 30px', fontFamily: SANS, fontSize: 34, color: C.ink }}>
          {sent ? <span style={{ opacity: 0.4 }}>Message...</span> : <span>{msg.slice(0, typedN)}<span style={{ color: C.acc, opacity: f % 16 < 8 ? 1 : 0 }}>|</span></span>}
        </div>
      </Obj>
      <Obj x={680} y={1100} w={300} h={140} rot={-6} delay={sentAt + 6} radius={4} style={{ background: C.sticky, padding: '22px 26px' }}>
        <div style={{ fontFamily: SANS, fontWeight: 900, fontSize: 38, lineHeight: 1.02, letterSpacing: '-0.03em', color: C.ink }}>Free, no<br />obligation</div>
      </Obj>
      <Fade delay={sentAt + 2}><div style={{ position: 'absolute', left: 90, top: 1240, fontFamily: SANS, fontWeight: 900, fontSize: wa ? 84 : 110, letterSpacing: '-0.045em', color: C.ink, lineHeight: 1 }}>
        {wa ? <>WhatsApp<br /><span style={{ fontFamily: SERIF, fontWeight: 400, fontStyle: 'italic', color: C.acc, fontSize: 96 }}>{phone}</span></> : <>DM us <span style={{ fontFamily: SERIF, fontWeight: 400, fontStyle: 'italic', color: C.acc, fontSize: 130 }}>{msg}</span></>}
      </div></Fade>
    </AbsoluteFill>
  );
};

export const SCENES: Record<string, React.FC<{ c: Ctx }>> = {
  kinetic: Kinetic, casefile: CaseFile, checklist: Checklist, google: Google, whatsapp: WhatsApp, sitebuild: SiteBuild,
  beforeafter: BeforeAfter, price: Price, timeline: Timeline, icons: Icons, footage: Footage, cta: Cta,
};

export const PaperBg: React.FC = () => {
  const f = useCurrentFrame();
  return (
    <AbsoluteFill style={{ background: C.paper, overflow: 'hidden' }}>
      <Img src={staticFile('paper/paper-cream.jpg')} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${1.02 + f * 0.00003})` }} />
    </AbsoluteFill>
  );
};
