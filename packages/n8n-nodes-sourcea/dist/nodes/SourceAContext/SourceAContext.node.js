"use strict";

const { buildContextEnvelope } = require("../../src/shared.cjs");

class SourceAContext {
  description = {
    displayName: "SourceA Context",
    name: "sourceAContext",
    group: ["transform"],
    version: 1,
    description: "Build ContextPack envelope refs for SourceA executive runs",
    defaults: { name: "SourceA Context" },
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
        displayName: "Event Type",
        name: "eventType",
        type: "string",
        default: "webpage.repair.requested",
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
      const targetUrl = this.getNodeParameter("targetUrl", i);
      const eventType = this.getNodeParameter("eventType", i);
      const correlationId =
        this.getNodeParameter("correlationId", i) ||
        items[i].json.correlation_id ||
        undefined;
      const envelope = await buildContextEnvelope({
        target_url: targetUrl,
        event_type: eventType,
        correlation_id: correlationId,
        payload: items[i].json,
      });
      out.push({ json: envelope });
    }
    return [out];
  }
}

module.exports = { SourceAContext };
