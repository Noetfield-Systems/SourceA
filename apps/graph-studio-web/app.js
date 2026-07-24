import React, { useCallback, useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  addEdge,
  useEdgesState,
  useNodesState,
  Handle,
  Position,
} from "@xyflow/react";

const h = React.createElement;
const API = window.GRAPH_STUDIO_API || "";

function api(path, opts) {
  return fetch(`${API}${path}`, {
    headers: { "content-type": "application/json", ...(opts?.headers || {}) },
    ...opts,
  }).then(async (r) => {
    const j = await r.json().catch(() => ({}));
    return { ok: r.ok, status: r.status, body: j };
  });
}

function StudioNode({ data, selected }) {
  return h(
    "div",
    { className: selected ? "selected" : "", style: { borderColor: data.color || undefined } },
    h(Handle, { type: "target", position: Position.Left }),
    h("strong", null, data.label),
    h("div", { style: { color: "#8b9aab", fontSize: "0.7rem" } }, data.kind),
    data.runStatus
      ? h("div", { className: data.runStatus, style: { marginTop: 4, fontSize: "0.7rem" } }, data.runStatus)
      : null,
    h(Handle, { type: "source", position: Position.Right }),
  );
}

const nodeTypes = { studio: StudioNode };

function graphFromFlow(nodes, edges, meta) {
  return {
    blueprint_id: meta.blueprint_id,
    version: meta.version,
    title: meta.title,
    nodes: nodes.map((n) => ({
      id: n.id,
      node_kind: n.data.kind,
      manifest_version: n.data.manifest_version || "1.0.0",
      ...(n.data.config ? { config: n.data.config } : {}),
    })),
    edges: edges.map((e, i) => ({
      id: e.id || `e_${i}`,
      from_node: e.source,
      from_port: e.data?.from_port || e.sourceHandle || "out",
      to_node: e.target,
      to_port: e.data?.to_port || e.targetHandle || "in",
    })),
  };
}

function layoutFromFlow(nodes, meta) {
  return {
    blueprint_id: meta.blueprint_id,
    version: meta.version,
    positions: Object.fromEntries(
      nodes.map((n) => [n.id, { x: n.position.x, y: n.position.y, color: n.data.color }]),
    ),
  };
}

function App() {
  const [registry, setRegistry] = useState([]);
  const [meta, setMeta] = useState({
    blueprint_id: "webpage_repair_l0_v1",
    version: "1.0.0",
    title: "Webpage Repair L0",
  });
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selected, setSelected] = useState(null);
  const [status, setStatus] = useState("Load golden blueprint to start");
  const [planHash, setPlanHash] = useState("");
  const [runGraph, setRunGraph] = useState(null);
  const [configText, setConfigText] = useState("{}");

  const loadGolden = useCallback(async () => {
    const r = await api("/v1/blueprints/golden");
    if (!r.ok) {
      setStatus(`golden load failed: ${r.status}`);
      return;
    }
    const { graph, layout } = r.body;
    setMeta({
      blueprint_id: graph.blueprint_id,
      version: graph.version,
      title: graph.title,
    });
    const pos = layout?.positions || {};
    setNodes(
      graph.nodes.map((n, i) => ({
        id: n.id,
        type: "studio",
        position: pos[n.id] || { x: (i % 5) * 220, y: Math.floor(i / 5) * 140 },
        data: {
          label: n.node_kind.replace(/_/g, " "),
          kind: n.node_kind,
          manifest_version: n.manifest_version,
          config: n.config || {},
          color: pos[n.id]?.color,
        },
      })),
    );
    setEdges(
      graph.edges.map((e) => ({
        id: e.id,
        source: e.from_node,
        target: e.to_node,
        data: { from_port: e.from_port, to_port: e.to_port },
      })),
    );
    setStatus(`Loaded golden ${graph.blueprint_id}@${graph.version}`);
    setPlanHash("");
    setRunGraph(null);
  }, [setNodes, setEdges]);

  useEffect(() => {
    api("/v1/registry").then((r) => {
      if (r.ok) setRegistry(r.body.manifests || []);
    });
    loadGolden();
  }, [loadGolden]);

  const onConnect = useCallback(
    (connection) =>
      setEdges((eds) => addEdge({ ...connection, data: { from_port: "out", to_port: "in" } }, eds)),
    [setEdges],
  );

  const onSelectionChange = useCallback(({ nodes: ns }) => {
    const n = ns[0];
    setSelected(n || null);
    setConfigText(JSON.stringify(n?.data?.config || {}, null, 2));
  }, []);

  const applyConfig = () => {
    if (!selected) return;
    try {
      const cfg = JSON.parse(configText);
      setNodes((ns) =>
        ns.map((n) => (n.id === selected.id ? { ...n, data: { ...n.data, config: cfg } } : n)),
      );
      setStatus(`Updated config for ${selected.id}`);
    } catch (e) {
      setStatus(`Config JSON invalid: ${e.message}`);
    }
  };

  const addFromPalette = (m) => {
    const id = `n_${m.node_kind}_${Math.random().toString(36).slice(2, 7)}`;
    setNodes((ns) => [
      ...ns,
      {
        id,
        type: "studio",
        position: { x: 80 + ns.length * 24, y: 80 + ns.length * 18 },
        data: {
          label: m.title,
          kind: m.node_kind,
          manifest_version: m.version,
          config: {},
        },
      },
    ]);
  };

  const validate = async () => {
    const graph = graphFromFlow(nodes, edges, meta);
    const r = await api("/v1/blueprints/validate", { method: "POST", body: JSON.stringify({ graph }) });
    if (r.body.ok) {
      setPlanHash(r.body.plan.plan_hash);
      setStatus(`Validate PASS · plan_hash=${r.body.plan.plan_hash.slice(0, 16)}…`);
    } else {
      setStatus(`Validate FAIL · ${(r.body.errors || []).map((e) => e.code).join(", ")}`);
    }
  };

  const publish = async () => {
    const graph = graphFromFlow(nodes, edges, meta);
    const layout = layoutFromFlow(nodes, meta);
    const r = await api("/v1/blueprints/publish", {
      method: "POST",
      body: JSON.stringify({ graph, layout }),
    });
    if (r.body.ok) {
      setPlanHash(r.body.plan_hash);
      setStatus(`Published · plan_hash=${r.body.plan_hash}`);
    } else {
      setStatus(`Publish FAIL · ${JSON.stringify(r.body.errors || r.body.error)}`);
    }
  };

  const run = async () => {
    if (!planHash) {
      setStatus("Publish first to pin plan_hash");
      return;
    }
    setStatus("Running pinned plan…");
    const r = await api("/v1/runs", {
      method: "POST",
      body: JSON.stringify({
        plan_hash: planHash,
        event: {
          event_id: `gs_${Date.now()}`,
          payload: {
            target_url: "https://sourcea.app/operating-brain-install",
            task_type: "webpage_repair",
          },
        },
      }),
    });
    setRunGraph(r.body.run_graph || null);
    if (r.body.run_graph?.nodes) {
      const byId = Object.fromEntries(r.body.run_graph.nodes.map((n) => [n.id, n.status]));
      setNodes((ns) =>
        ns.map((n) => ({ ...n, data: { ...n.data, runStatus: byId[n.id] || n.data.runStatus } })),
      );
    }
    setStatus(
      `Run ${r.body.run_id || "?"} · terminal=${r.body.terminal || "?"} · mesh=${r.body.mesh_run_id || "none"}`,
    );
  };

  const selectedManifest = useMemo(
    () => registry.find((m) => m.node_kind === selected?.data?.kind),
    [registry, selected],
  );

  return h(
    "div",
    { className: "shell" },
    h(
      "header",
      null,
      h("div", { className: "brand" }, "SourceA Graph Studio"),
      h(
        "div",
        { className: "law" },
        "Canvas ≠ Brain · plan_hash pins Mesh · React Flow is UI-only",
      ),
    ),
    h(
      "aside",
      { className: "palette" },
      h("h2", null, "Palette"),
      ...registry.map((m) =>
        h(
          "button",
          { key: m.node_kind, type: "button", onClick: () => addFromPalette(m) },
          m.title,
        ),
      ),
    ),
    h(
      "main",
      { className: "canvas" },
      h(
        ReactFlow,
        {
          nodes,
          edges,
          onNodesChange,
          onEdgesChange,
          onConnect,
          onSelectionChange,
          nodeTypes,
          fitView: true,
        },
        h(Background, { gap: 18, color: "#2a3542" }),
        h(Controls),
        h(MiniMap),
      ),
    ),
    h(
      "aside",
      { className: "inspector" },
      h("h2", null, "Inspector"),
      selected
        ? h(
            React.Fragment,
            null,
            h("div", null, h("strong", null, selected.data.label)),
            h("div", { style: { color: "#8b9aab", fontSize: "0.8rem" } }, selected.data.kind),
            selectedManifest?.budget?.human_tax_visible
              ? h(
                  "div",
                  { style: { marginTop: 8, color: "#c4a35a", fontSize: "0.8rem" } },
                  "Human Tax: visible",
                )
              : null,
            h("label", null, "Config (JSON Schema)"),
            h("textarea", {
              rows: 8,
              value: configText,
              onChange: (e) => setConfigText(e.target.value),
            }),
            h(
              "button",
              { type: "button", onClick: applyConfig, style: { marginTop: 8 } },
              "Apply config",
            ),
            selectedManifest
              ? h(
                  React.Fragment,
                  null,
                  h("label", null, "Schema"),
                  h("pre", null, JSON.stringify(selectedManifest.config_schema, null, 2)),
                )
              : null,
          )
        : h("p", { style: { color: "#8b9aab", fontSize: "0.85rem" } }, "Select a node"),
      runGraph
        ? h(
            "div",
            { className: "node-status" },
            h("h2", null, "Run Graph"),
            h(
              "ul",
              { style: { padding: 0 } },
              ...(runGraph.nodes || []).map((n) =>
                h("li", { key: n.id, className: n.status }, `${n.id}: ${n.status}`),
              ),
            ),
          )
        : null,
    ),
    h(
      "div",
      { className: "toolbar" },
      h("button", { type: "button", onClick: loadGolden }, "Load golden"),
      h("button", { type: "button", onClick: validate }, "Validate"),
      h("button", { type: "button", className: "primary", onClick: publish }, "Publish"),
      h("button", { type: "button", className: "primary", onClick: run }, "Run"),
      h("div", { className: "status" }, status),
    ),
  );
}

createRoot(document.getElementById("root")).render(h(App));
