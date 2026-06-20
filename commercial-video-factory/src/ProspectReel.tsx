import React from "react";
import {
  AbsoluteFill,
  interpolate,
  spring,
  useCurrentFrame,
  useVideoConfig,
  Video,
  staticFile,
} from "remotion";
import type { ProspectReelProps } from "./types";

const FPS = 30;

type Beat = {
  start: number;
  end: number;
  kind: "hook" | "pain" | "proof" | "cta";
};

function beats(durationSeconds: number): Beat[] {
  const total = durationSeconds * FPS;
  return [
    { start: 0, end: Math.floor(total * 0.17), kind: "hook" },
    { start: Math.floor(total * 0.17), end: Math.floor(total * 0.4), kind: "pain" },
    { start: Math.floor(total * 0.4), end: Math.floor(total * 0.78), kind: "proof" },
    { start: Math.floor(total * 0.78), end: total, kind: "cta" },
  ];
}

const PopText: React.FC<{
  text: string;
  frame: number;
  enterAt: number;
  accent: string;
  size?: number;
}> = ({ text, frame, enterAt, accent, size = 72 }) => {
  const { fps } = useVideoConfig();
  const progress = spring({
    frame: frame - enterAt,
    fps,
    config: { damping: 14, stiffness: 180, mass: 0.7 },
  });
  const opacity = interpolate(progress, [0, 1], [0, 1]);
  const scale = interpolate(progress, [0, 1], [0.82, 1]);
  if (frame < enterAt) return null;
  return (
    <div
      style={{
        opacity,
        transform: `scale(${scale})`,
        fontSize: size,
        fontWeight: 900,
        lineHeight: 1.05,
        letterSpacing: "-0.03em",
        color: "#f8fafc",
        textAlign: "center",
        padding: "0 48px",
        textShadow: `0 0 40px ${accent}55`,
      }}
    >
      {text}
    </div>
  );
};

/** SHIP_BLOCKED_MOCK — only when broll_video_file absent (dev preview) */
const ProofBeat: React.FC<{
  props: ProspectReelProps;
  frame: number;
  enterAt: number;
}> = ({ props, frame, enterAt }) => {
  const { fps, durationInFrames } = useVideoConfig();
  const progress = spring({ frame: frame - enterAt, fps, config: { damping: 16 } });
  if (frame < enterAt) return null;

  if (props.broll_video_file) {
    const local = frame - enterAt;
    return (
      <div
        style={{
          width: "92%",
          maxWidth: 980,
          borderRadius: 20,
          overflow: "hidden",
          border: `2px solid ${props.accent}55`,
          boxShadow: `0 24px 80px rgba(0,0,0,0.5)`,
          opacity: interpolate(progress, [0, 1], [0, 1]),
          transform: `scale(${interpolate(progress, [0, 1], [0.94, 1])})`,
        }}
      >
        <Video
          src={staticFile(props.broll_video_file)}
          style={{ width: "100%", height: "auto" }}
          startFrom={Math.floor((enterAt % durationInFrames) * 0.4)}
        />
        <div
          style={{
            position: "absolute",
            bottom: 24,
            left: 24,
            right: 24,
            color: "#f8fafc",
            fontSize: 22,
            fontWeight: 700,
            textShadow: "0 2px 12px rgba(0,0,0,0.8)",
          }}
        >
          {props.company} · {props.verdict} · real UI
        </div>
      </div>
    );
  }

  return <TerminalMock props={props} frame={frame} enterAt={enterAt} />;
};

/** SHIP_BLOCKED_MOCK — dev preview only; outbound must use w1-demo.mp4 real UI b-roll */
const TerminalMock: React.FC<{
  props: ProspectReelProps;
  frame: number;
  enterAt: number;
}> = ({ props, frame, enterAt }) => {
  const { fps } = useVideoConfig();
  const progress = spring({ frame: frame - enterAt, fps, config: { damping: 16 } });
  if (frame < enterAt) return null;
  const lines = [
    `$ sourcea-boot --json`,
    `→ policy.eval   verdict=${props.verdict}`,
    `→ receipt.signed  ${props.receipt_hash.slice(0, 22)}…`,
    "→ replay.check    chain=OK",
    "← tamper-FAIL     signature invalid",
  ];
  const visible = Math.min(lines.length, Math.floor(interpolate(progress, [0, 1], [1, lines.length + 0.5])));
  return (
    <div
      style={{
        width: "88%",
        maxWidth: 920,
        borderRadius: 16,
        border: `1px solid ${props.accent}44`,
        background: "rgba(15, 23, 42, 0.92)",
        boxShadow: `0 24px 80px rgba(0,0,0,0.45), 0 0 0 1px ${props.accent}22`,
        overflow: "hidden",
        fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace",
        fontSize: 28,
        opacity: interpolate(progress, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(progress, [0, 1], [24, 0])}px)`,
      }}
    >
      <div
        style={{
          padding: "14px 18px",
          borderBottom: "1px solid rgba(148,163,184,0.2)",
          color: "#94a3b8",
          fontSize: 20,
        }}
      >
        sourcea-boot proof — {props.company}
      </div>
      <div style={{ padding: "22px 24px", color: "#e2e8f0", lineHeight: 1.55 }}>
        {lines.slice(0, visible).map((line, i) => (
          <div
            key={i}
            style={{
              color: line.includes("tamper-FAIL")
                ? "#f87171"
                : line.includes("verdict=")
                  ? props.accent
                  : "#cbd5e1",
            }}
          >
            {line}
          </div>
        ))}
      </div>
    </div>
  );
};

export const ProspectReel: React.FC<ProspectReelProps> = (props) => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();
  const beatList = beats(props.duration_seconds);
  const active = beatList.find((b) => frame >= b.start && frame < b.end) ?? beatList[0];

  const meshOpacity = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill
      style={{
        background: "#060a0f",
        fontFamily: "Inter, system-ui, sans-serif",
        overflow: "hidden",
      }}
    >
      <AbsoluteFill
        style={{
          opacity: meshOpacity,
          background: `
            radial-gradient(ellipse 80% 60% at 20% 0%, ${props.accent}22, transparent 55%),
            radial-gradient(ellipse 60% 50% at 90% 20%, #0d948822, transparent 50%)
          `,
        }}
      />

      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", padding: 40 }}>
        {active.kind === "hook" && (
          <PopText text={props.hook} frame={frame} enterAt={active.start + 4} accent={props.accent} size={68} />
        )}
        {active.kind === "pain" && (
          <>
            <div style={{ position: "absolute", top: 120, color: props.accent, fontSize: 22, fontWeight: 700, letterSpacing: "0.12em" }}>
              {props.company.toUpperCase()}
            </div>
            <PopText text={props.pain} frame={frame} enterAt={active.start + 6} accent={props.accent} size={52} />
          </>
        )}
        {active.kind === "proof" && (
          <ProofBeat props={props} frame={frame} enterAt={active.start + 8} />
        )}
        {active.kind === "cta" && (
          <>
            <PopText text={props.proof_line} frame={frame} enterAt={active.start + 4} accent={props.accent} size={44} />
            {(() => {
              const s = spring({
                frame: frame - active.start - 20,
                fps: FPS,
                config: { damping: 12, stiffness: 120 },
              });
              return (
                <div
                  style={{
                    marginTop: 48,
                    padding: "22px 36px",
                    borderRadius: 999,
                    background: props.accent,
                    color: "#042f2e",
                    fontSize: 32,
                    fontWeight: 800,
                    opacity: s,
                    transform: `scale(${interpolate(s, [0, 1], [0.88, 1])})`,
                  }}
                >
                  {props.cta}
                </div>
              );
            })()}
            <div style={{ marginTop: 28, color: "#64748b", fontSize: 22 }}>{props.brand} · witnessbc.com</div>
          </>
        )}
      </AbsoluteFill>

      <div
        style={{
          position: "absolute",
          bottom: 36,
          left: 40,
          right: 40,
          display: "flex",
          justifyContent: "space-between",
          color: "#475569",
          fontSize: 18,
          fontFamily: "ui-monospace, monospace",
        }}
      >
        <span>{props.lane}</span>
        <span>
          {Math.min(props.duration_seconds, Math.ceil(frame / FPS))}s / {props.duration_seconds}s
        </span>
      </div>

      <div
        style={{
          position: "absolute",
          bottom: 0,
          left: 0,
          height: 4,
          width: `${(frame / durationInFrames) * 100}%`,
          background: props.accent,
        }}
      />
    </AbsoluteFill>
  );
};
