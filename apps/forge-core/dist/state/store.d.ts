import { ForgeRunState, PersistedState } from "../types/state.js";
import { ForgeTaskRecord } from "../types/task.js";
export declare function saveTaskRecord(record: ForgeTaskRecord): Promise<string>;
export declare function loadTaskRecord(taskId: string): Promise<ForgeTaskRecord | null>;
export declare function saveRunState(state: ForgeRunState): Promise<string>;
export declare function loadRunState(taskId: string): Promise<ForgeRunState | null>;
export declare function toPersistedState(state: ForgeRunState): PersistedState;
export declare function saveReceipt(taskId: string, receipt: Record<string, unknown>): Promise<string>;
