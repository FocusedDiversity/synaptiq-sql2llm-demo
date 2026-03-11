export interface QueryRequest {
  query: string;
}

export interface VisualizationConfig {
  type: "bar" | "line" | "pie" | "table";
  x_column: string | null;
  y_column: string | null;
  title: string | null;
}

export interface QueryResponse {
  generated_sql: string;
  columns: string[];
  rows: (string | number | boolean | null)[][];
  truncated: boolean;
  visualization: VisualizationConfig | null;
  insight: string | null;
  error: string | null;
}

export interface ErrorResponse {
  error: string;
  generated_sql: string | null;
}

export interface SuggestionCategory {
  category: string;
  queries: string[];
}

export interface SchemaColumn {
  name: string;
  type: string;
  nullable: boolean;
  primary_key: boolean;
}

export interface SchemaTable {
  name: string;
  columns: SchemaColumn[];
  row_count: number;
}

export interface HistoryEntry {
  query: string;
  timestamp: number;
  generated_sql: string;
}
