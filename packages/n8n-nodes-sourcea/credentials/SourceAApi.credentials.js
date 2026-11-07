"use strict";

class SourceAApi {
  name = "sourceAApi";
  displayName = "SourceA API";
  documentationUrl = "https://sourcea.app";
  properties = [
    {
      displayName: "Governor Base URL",
      name: "governorUrl",
      type: "string",
      default: "https://sourcea-executive-governor-v1.sina-kazemnezhad-ca.workers.dev",
    },
    {
      displayName: "Governor Ingress Token",
      name: "apiToken",
      type: "string",
      typeOptions: { password: true },
      default: "",
      required: true,
      description: "Stored as an n8n credential; never place this token in workflow JSON.",
    },
  ];
}

module.exports = { SourceAApi };
