import {Composition} from 'remotion';
import {Receipts, TOTAL} from './Video';

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Receipts"
      component={Receipts}
      durationInFrames={TOTAL}
      fps={30}
      width={1920}
      height={1080}
    />
  );
};
