"use client";

import { useMemo } from "react";
import {
  ReactFlow,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Position,
  Handle,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { GraphData } from "@/types";
import { Network, ShieldAlert, User, MapPin, Landmark, FileText } from "lucide-react";

interface RelationshipGraphProps {
  graph: GraphData;
}

const entityIcons: Record<string, any> = {
  fir: FileText,
  accused: ShieldAlert,
  victim: User,
  officer: User,
  location: MapPin,
  financial: Landmark,
};

function CustomNode({ data }: { data: any }) {
  const Icon = entityIcons[data.type] || FileText;

  return (
    <div
      className="px-3 py-2 rounded-xl border border-slate-700 shadow-lg backdrop-blur-md text-slate-100 flex items-center gap-2 min-w-30"
      style={{ backgroundColor: `${data.color}25`, borderColor: data.color }}
    >
      <Handle type="target" position={Position.Top} className="w-2 h-2 bg-indigo-400!" />
      <div
        className="p-1.5 rounded-lg flex items-center justify-center text-white"
        style={{ backgroundColor: data.color }}
      >
        <Icon className="w-3.5 h-3.5" />
      </div>
      <div>
        <div className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
          {data.type}
        </div>
        <div className="text-xs font-semibold truncate max-w-32.5">{data.label}</div>
      </div>
      <Handle type="source" position={Position.Bottom} className="w-2 h-2 bg-indigo-400!" />
    </div>
  );
}

const nodeTypes = { custom: CustomNode };

export function RelationshipGraph({ graph }: RelationshipGraphProps) {
  if (!graph || !graph.nodes || graph.nodes.length === 0) return null;

  // Auto-arrange layout in a circle/grid
  const initialNodes = useMemo(() => {
    const total = graph.nodes.length;
    const radius = Math.min(220, total * 30);
    const centerX = 250;
    const centerY = 180;

    return graph.nodes.map((n, i) => {
      const angle = (i / total) * 2 * Math.PI;
      const x = centerX + radius * Math.cos(angle);
      const y = centerY + radius * Math.sin(angle);

      return {
        id: n.id,
        type: "custom",
        position: { x, y },
        data: {
          label: n.label,
          type: n.type,
          color: n.data?.color || "#6366f1",
        },
      };
    });
  }, [graph]);

  const initialEdges = useMemo(() => {
    return graph.edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      label: e.label,
      animated: true,
      style: { stroke: "#818cf8", strokeWidth: 2 },
      labelStyle: { fill: "#94a3b8", fontSize: 10 },
      labelBgStyle: { fill: "#0f172a", fillOpacity: 0.8 },
    }));
  }, [graph]);

  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  return (
    <div className="my-4 border border-indigo-500/20 rounded-xl bg-slate-950/90 overflow-hidden shadow-2xl">
      <div className="p-3 bg-slate-900/80 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Network className="w-4 h-4 text-indigo-400" />
          <h4 className="text-sm font-semibold text-slate-200">Entity Relationship Graph</h4>
        </div>
        <div className="text-xs text-slate-400 font-mono">
          {nodes.length} entities • {edges.length} connections
        </div>
      </div>
      <div className="w-full h-80">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          nodeTypes={nodeTypes}
          fitView
        >
          <Background color="#334155" gap={16} />
          <Controls className="bg-slate-900 border-slate-700 text-slate-200 fill-slate-200" />
        </ReactFlow>
      </div>
    </div>
  );
}
