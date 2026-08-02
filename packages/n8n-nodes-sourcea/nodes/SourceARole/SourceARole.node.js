"use strict";

const { buildRoleEnvelope } = require("../../src/shared.cjs");

class SourceARole {
  description = {
    displayName: "SourceA Role",
    name: "sourceARole",
    group: ["transform"],
    version: 1,
    description: "Config-driven micro-role assignment (Planner/Critic/…)",
    defaults: { name: "SourceA Role" },
    inputs: ["main"],
    outputs: ["main"],
    properties: [
      {
        displayName: "Role ID",
        name: "roleId",
        type: "string",
        default: "sg_planner",
        required: true,
      },
      {
        displayName: "Control Mode",
        name: "controlMode",
        type: "options",
        options: [
          { name: "SINGLE", value: "SINGLE" },
          { name: "MAP", value: "MAP" },
          { name: "FANOUT", value: "FANOUT" },
          { name: "JOIN", value: "JOIN" },
          { name: "LOOP", value: "LOOP" },
        ],
        default: "SINGLE",
      },
      {
        displayName: "Correlation ID",
        name: "correlationId",
        type: "string",
        default: "",
      },
    ],
  };

  async execute() {
    const items = this.getInputData();
    const out = [];
    for (let i = 0; i < items.length; i++) {
      const envelope = await buildRoleEnvelope({
        role_id: this.getNodeParameter("roleId", i),
        control_mode: this.getNodeParameter("controlMode", i),
        correlation_id:
          this.getNodeParameter("correlationId", i) ||
          items[i].json.correlation_id ||
          undefined,
      });
      out.push({ json: { ...items[i].json, role: envelope } });
    }
    return [out];
  }
}

module.exports = { SourceARole };
