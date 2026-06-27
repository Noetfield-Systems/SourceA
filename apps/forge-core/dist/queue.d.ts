import { Queue, Worker, type ConnectionOptions, type JobsOptions } from "bullmq";
import type { ForgeTask } from "./types/task.js";
import { FORGE_JOB_NAME, FORGE_QUEUE_NAME } from "./paths.js";
export declare function getQueueConnection(): ConnectionOptions;
export declare function createTaskQueue(): Queue<ForgeTask>;
export declare function enqueueTask(task: ForgeTask, options?: JobsOptions): Promise<string>;
export declare function createTaskWorker(processor: (task: ForgeTask) => Promise<void>): Worker<ForgeTask>;
export { FORGE_QUEUE_NAME, FORGE_JOB_NAME };
