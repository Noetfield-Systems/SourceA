import { governTask } from "@sourcea/forge-governance";
export async function checkGovernance(task) {
    return governTask({
        agent_id: task.agent_id,
        agent_role: task.role,
        action_type: task.action_type,
        task_id: task.id,
        payload: task.payload,
        dry_run: process.env.FORGE_GOVERNANCE_DRY_RUN?.trim() !== "0",
    });
}
