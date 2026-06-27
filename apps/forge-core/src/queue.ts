import { Queue, Worker, type ConnectionOptions, type JobsOptions } from "bullmq";

import type { ForgeTask } from "./types/task.js";
import {
  FORGE_JOB_NAME,
  FORGE_QUEUE_NAME,
  getRedisUrl,
} from "./paths.js";

export function getQueueConnection(): ConnectionOptions {
  const url = new URL(getRedisUrl());
  return {
    host: url.hostname,
    port: Number(url.port || 6379),
    username: url.username || undefined,
    password: url.password || undefined,
    maxRetriesPerRequest: null,
  };
}

export function createTaskQueue(): Queue<ForgeTask> {
  return new Queue<ForgeTask>(FORGE_QUEUE_NAME, {
    connection: getQueueConnection(),
    defaultJobOptions: {
      attempts: 3,
      backoff: { type: "exponential", delay: 2000 },
      removeOnComplete: 100,
      removeOnFail: 200,
    },
  });
}

export async function enqueueTask(
  task: ForgeTask,
  options?: JobsOptions,
): Promise<string> {
  const queue = createTaskQueue();
  const job = await queue.add(FORGE_JOB_NAME, task, {
    jobId: task.id,
    ...options,
  });
  await queue.close();
  return job.id ?? task.id;
}

export function createTaskWorker(
  processor: (task: ForgeTask) => Promise<void>,
): Worker<ForgeTask> {
  return new Worker<ForgeTask>(
    FORGE_QUEUE_NAME,
    async (job) => {
      await processor(job.data);
    },
    {
      connection: getQueueConnection(),
      concurrency: Number.parseInt(
        process.env.FORGE_WORKER_CONCURRENCY?.trim() || "2",
        10,
      ),
    },
  );
}

export { FORGE_QUEUE_NAME, FORGE_JOB_NAME };
