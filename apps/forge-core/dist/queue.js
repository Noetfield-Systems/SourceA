import { Queue, Worker } from "bullmq";
import { FORGE_JOB_NAME, FORGE_QUEUE_NAME, getRedisUrl, } from "./paths.js";
export function getQueueConnection() {
    const url = new URL(getRedisUrl());
    return {
        host: url.hostname,
        port: Number(url.port || 6379),
        username: url.username || undefined,
        password: url.password || undefined,
        maxRetriesPerRequest: null,
    };
}
export function createTaskQueue() {
    return new Queue(FORGE_QUEUE_NAME, {
        connection: getQueueConnection(),
        defaultJobOptions: {
            attempts: 3,
            backoff: { type: "exponential", delay: 2000 },
            removeOnComplete: 100,
            removeOnFail: 200,
        },
    });
}
export async function enqueueTask(task, options) {
    const queue = createTaskQueue();
    const job = await queue.add(FORGE_JOB_NAME, task, {
        jobId: task.id,
        ...options,
    });
    await queue.close();
    return job.id ?? task.id;
}
export function createTaskWorker(processor) {
    return new Worker(FORGE_QUEUE_NAME, async (job) => {
        await processor(job.data);
    }, {
        connection: getQueueConnection(),
        concurrency: Number.parseInt(process.env.FORGE_WORKER_CONCURRENCY?.trim() || "2", 10),
    });
}
export { FORGE_QUEUE_NAME, FORGE_JOB_NAME };
