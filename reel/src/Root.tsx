import React from 'react';
import { Composition } from 'remotion';
import { Reel, ReelProps } from './Reel';

const demo: ReelProps = {
  fps: 30, total: 6, voice: null, music: null, kicker: 'READ THIS FIRST', niche: 'salon',
  brand: { name: 'Stolen Valour', url: 'stolenvalour.co.za', contact: 'WhatsApp 065 027 6518', accent: '#14213D' },
  segs: [{ kind: 'hook', show: 'Your website is losing you *clients*', say: 'Your website is losing you clients', start: 0.04, end: 5, words: [], scene: 'kinetic', mood: 'neg', clip: null }],
};

export const Root: React.FC = () => (
  <Composition
    id="Reel"
    component={Reel as any}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={180}
    defaultProps={demo as any}
    calculateMetadata={({ props }: any) => ({ durationInFrames: Math.ceil(props.total * props.fps) })}
  />
);
