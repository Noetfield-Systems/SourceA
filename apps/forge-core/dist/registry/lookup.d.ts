import type { ForgeRunState } from "../types/state.js";
import type { ForgeTaskRecord } from "../types/task.js";
export declare function getTaskById(taskId: string): Promise<ForgeTaskRecord | null>;
export declare function getStateByTaskId(taskId: string): Promise<ForgeRunState | null>;
export declare function loadAgentRegistry(): Promise<Record<string, unknown>>;
