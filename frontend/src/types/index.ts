export interface User {
  id: string;
  username: string;
  full_name: string;
  email: string;
  role: 'admin' | 'officer' | 'analyst' | 'viewer';
  badge_number?: string;
  department?: string;
}

export interface SQLResult {
  query: string;
  columns: string[];
  rows: Record<string, any>[];
  row_count: number;
  execution_time_ms: number;
}

export interface ChartData {
  chart_type: 'bar' | 'line' | 'pie' | 'area';
  title: string;
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
    borderWidth?: number;
  }[];
}

export interface GraphNode {
  id: string;
  label: string;
  type: 'fir' | 'accused' | 'victim' | 'officer' | 'location' | 'financial';
  data?: Record<string, any>;
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label: string;
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  sql_query?: string;
  sql_result?: SQLResult;
  chart_data?: ChartData;
  graph_data?: GraphData;
  confidence?: number;
  evidence_refs?: string[];
  suggested_questions?: string[];
  language?: 'en' | 'kn';
  isStreaming?: boolean;
  created_at?: string;
}

export interface ConversationSummary {
  conversation_id: string;
  title: string;
  message_count: number;
  last_message_at: string;
  language: string;
}
