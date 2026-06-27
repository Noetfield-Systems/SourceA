import { Hono } from "hono";

import {
  fetchState,
  fetchTask,
  submitTask,
} from "../services/task-service.js";

export function createTaskRoutes(): Hono {
  const routes = new Hono();

  routes.post("/tasks", async (c) => {
    const body: unknown = await c.req.json();
    const result = await submitTask(body);
    if (!result.ok) {
      return c.json({ ok: false, error: result.error }, 400);
    }
    return c.json(
      { task_id: result.task_id, status: result.status },
      202,
    );
  });

  routes.get("/tasks/:id", async (c) => {
    const result = await fetchTask(c.req.param("id"));
    if (!result.ok) {
      return c.json({ ok: false, error: result.error }, 404);
    }
    return c.json(result);
  });

  routes.get("/state/:id", async (c) => {
    const result = await fetchState(c.req.param("id"));
    if (!result.ok) {
      return c.json({ ok: false, error: result.error }, 404);
    }
    return c.json(result.state);
  });

  return routes;
}
