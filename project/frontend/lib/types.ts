export type ChartType = "bar" | "line" | "pie";

export type ChartSeries = {
  name: string;
  values: Array<number>;
};

export type ChartSpec = {
  chart_type: ChartType;
  title: string;
  x_axis: string[];
  series: ChartSeries[];
  labels: string[];
  values: Array<number>;
  meta: Record<string, unknown>;
};

export type ReportSpec = {
  title: string;
  summary: string;
  insights: string[];
  recommendations: string[];
  conclusion: string;
};

export type TableSpec = {
  name: string;
  columns: string[];
  rows: Array<Record<string, unknown>>;
};

export type QueryRequest = {
  query: string;
  document_id?: string;
};

export type ApiResponse = {
  content: string;
  report: ReportSpec | null;
  charts: ChartSpec[];
  tables: TableSpec[];
  sources: string[];
};

export type UploadResponse = {
  document_id: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  status: string;
};

export type HealthResponse = {
  status: string;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  response?: ApiResponse;
};
