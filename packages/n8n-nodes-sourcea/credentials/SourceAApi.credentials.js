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
  ];
}

module.exports = { SourceAApi };
