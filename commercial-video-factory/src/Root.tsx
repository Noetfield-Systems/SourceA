import React from "react";
import { Composition } from "remotion";
import { ProspectReel } from "./ProspectReel";
import { defaultProspectReelProps } from "./types";

export const RemotionRoot: React.FC = () => {
  const durationSeconds = defaultProspectReelProps.duration_seconds;
  return (
    <>
      <Composition
        id="ProspectReel"
        component={ProspectReel}
        durationInFrames={durationSeconds * 30}
        fps={30}
        width={1080}
        height={1920}
        defaultProps={defaultProspectReelProps}
      />
    </>
  );
};
