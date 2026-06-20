export type ProspectReelProps = {
  schema?: "remotion-prospect-reel-v1";
  company: string;
  lane: "WBC" | "AB1" | "NW1" | "AEG";
  hook: string;
  pain: string;
  proof_line: string;
  scenario: string;
  verdict: string;
  receipt_hash: string;
  proof_url: string;
  w1_film_url?: string;
  cta: string;
  brand: string;
  accent: string;
  duration_seconds: number;
  pipeline_row_id?: string;
  broll_video_file?: string;
};

export const defaultProspectReelProps: ProspectReelProps = {
  schema: "remotion-prospect-reel-v1",
  company: "Acme Platform",
  lane: "AB1",
  hook: "Your agents act before policy runs?",
  pain: "Irreversible sends without signed receipts — GRC can't prove what happened.",
  proof_line: "BLOCK · ESCALATE · ALLOW — every gate signed on disk",
  scenario: "outbound",
  verdict: "ESCALATE",
  receipt_hash: "sha256:8f3a9c2e…c91e",
  proof_url: "https://sourcea.com/sourcea/proof/live.html",
  w1_film_url: "https://sourcea.com/sourcea/proof.html#w1-demo-film",
  cta: "Book 15-min proof",
  brand: "SourceA",
  accent: "#69d419",
  duration_seconds: 30,
};
