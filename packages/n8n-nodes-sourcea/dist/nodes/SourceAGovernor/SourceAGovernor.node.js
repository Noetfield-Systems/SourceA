"use strict";

const { callGovernor } = require("../../src/shared.cjs");

class SourceAGovernor {
  description = {
    displayName: "SourceA Governor",
    name: "sourceAGovernor",
    group: ["transform"],
    version: 1,
    description: "Call SourceA Executive Mesh Governor — returns envelope refs only",
    defaults: { name: "SourceA Governor" },
    inputs: ["main"],
    outputs: ["main"],
    properties: [
      {
        displayName: "Target URL",
        name: "targetUrl",
        type: "string",
        default: "",
        required: true,
      },
      {
        displayName: "Idempotency Key",
        name: "idempotencyKey",
        type: "string",
        default: "",
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
      const targetUrl =
        this.getNodeParameter("targetUrl", i) ||
        items[i].json.target_url ||
        (items[i].json.summary && items[i].json.summary.target_url);
      const envelope = await callGovernor({
        target_url: targetUrl,
        idempotency_key: this.getNodeParameter("idempotencyKey", i) || undefined,
        correlation_id:
          this.getNodeParameter("correlationId", i) ||
          items[i].json.correlation_id ||
          undefined,
        payload: items[i].json,
      });
      out.push({ json: envelope });
    }
    return [out];
  }
}

module.exports = { SourceAGovernor };
