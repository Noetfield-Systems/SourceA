import { spawn } from "node:child_process";
import { GovernDecisionSchema, getGovernanceCliPath, getScriptsDir, } from "@sourcea/forge-core";
function runGovernanceCli(request) {
    return new Promise((resolve, reject) => {
        const child = spawn("python3", [getGovernanceCliPath()], {
            env: {
                ...process.env,
                PYTHONPATH: getScriptsDir(),
            },
            stdio: ["pipe", "pipe", "pipe"],
        });
        let stdout = "";
        let stderr = "";
        child.stdout.on("data", (chunk) => {
            stdout += chunk.toString();
        });
        child.stderr.on("data", (chunk) => {
            stderr += chunk.toString();
        });
        child.on("error", reject);
        child.on("close", (code) => {
            if (!stdout.trim()) {
                reject(new Error(stderr || `governance_cli_exit_${code}`));
                return;
            }
            try {
                const parsed = GovernDecisionSchema.parse(JSON.parse(stdout));
                resolve(parsed);
            }
            catch (error) {
                reject(error instanceof Error
                    ? error
                    : new Error(`governance_parse_failed:${stdout}`));
            }
        });
        child.stdin.write(JSON.stringify(request));
        child.stdin.end();
    });
}
export async function checkGovernance(task) {
    const dryRun = process.env.FORGE_GOVERNANCE_DRY_RUN?.trim() !== "0" &&
        process.env.FORGE_GOVERNANCE_DRY_RUN?.trim() !== "false";
    return runGovernanceCli({
        agent_id: task.agent_id,
        agent_role: task.role,
        action_type: task.action_type,
        task_id: task.id,
        payload: task.payload,
        dry_run: dryRun,
        legal_review: false,
    });
}
