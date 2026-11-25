import React from 'react';
import { Composition } from 'remotion';
import { Reel, ReelProps } from './Reel';

const demo: ReelProps = {
  fps: 30, total: 6, voice: null, music: null,
  brand: { name: 'Stolen Valour', url: 'stolenvalour.co.za', contact: 'WhatsApp 065 027 6518', accent: '#B8F2D6' },
  segs: [{ kind: 'hook', show: 'Your website is losing you clients', say: 'Your website is losing you clients', start: 0.3, end: 3, words: [], clip: null, device: 'full' }],
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
