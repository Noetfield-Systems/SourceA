import { z } from "zod";

export const CampaignStepV1 = z.enum([
  "BRIEF_ANALYSIS",
  "AUDIO_READY",
  "VIDEO_RENDERING",
  "HUMAN_APPROVAL_REQUIRED",
  "DISPATCHED",
]);

export const VideoPromptLoopV1 = z.object({
  seed: z.number().optional(),
  positive_prompt: z.string(),
  negative_prompt: z.string().optional(),
  aspect_ratio: z.enum(["9:16", "1:1", "16:9"]).default("9:16"),
  variants: z.array(z.object({ label: z.string(), prompt: z.string() })).max(3).optional(),
});

export const CampaignAutomationV1 = z.object({
  id: z.string().uuid(),
  creator_id: z.string().uuid(),
  raw_brief: z.string().min(1),
  refined_script: z.string().optional(),
  voice_clone_id: z.string().optional(),
  video_prompt_loop: VideoPromptLoopV1.optional(),
  current_step: CampaignStepV1.default("BRIEF_ANALYSIS"),
});
export type CampaignAutomationV1 = z.infer<typeof CampaignAutomationV1>;
