import { type ForgeTask, type ForgeTaskRecord, type SubmitTaskInput } from "../types/task.js";
export declare function createQueuedTask(input: SubmitTaskInput): Promise<{
    task: ForgeTask;
    record: ForgeTaskRecord;
}>;
export declare function updateTaskStatus(taskId: string, patch: Partial<ForgeTaskRecord>): Promise<ForgeTaskRecord>;
