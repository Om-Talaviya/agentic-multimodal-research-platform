/**
 * TypeScript types for Real-Time Multi-Agent Collaborative Research Canvas & Visual Ideation Studio.
 */

export type CanvasNodeType =
  | 'hypothesis'
  | 'evidence'
  | 'paper'
  | 'agent_thought'
  | 'data_series'
  | 'conclusion'
  | 'counter_claim';

export type CanvasEdgeRelation =
  | 'supports'
  | 'refutes'
  | 'derives_from'
  | 'correlates_with'
  | 'branches_to'
  | 'questions';

export interface CanvasNode {
  id: string;
  node_type: CanvasNodeType;
  title: string;
  content?: string;
  confidence_score: number;
  status: string;
  position_x: number;
  position_y: number;
  width: number;
  height: number;
  color_accent?: string;
  metadata_json?: Record<string, any>;
  created_at?: string;
}

export interface CanvasEdge {
  id: string;
  source_node_id: string;
  target_node_id: string;
  relation_type: CanvasEdgeRelation;
  label?: string;
  weight: number;
  metadata_json?: Record<string, any>;
  created_at?: string;
}

export interface CanvasBoard {
  id: string;
  title: string;
  description?: string;
  viewport_state: {
    zoom: number;
    pan_x: number;
    pan_y: number;
  };
  background_grid: 'dots' | 'lines' | 'crosses' | 'clean';
  status: string;
  created_at: string;
  nodes?: CanvasNode[];
  edges?: CanvasEdge[];
}

export interface CanvasMetrics {
  total_canvas_boards: number;
  total_canvas_nodes: number;
  total_canvas_edges: number;
  node_type_distribution: Record<string, number>;
  average_nodes_per_board: number;
}
