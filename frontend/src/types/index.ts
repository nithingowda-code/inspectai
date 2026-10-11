export interface ProductReference {
  id: string;
  file_path: string;
  filename: string;
  is_primary: boolean;
  created_at: string;
}

export interface Product {
  id: string;
  name: string;
  category: string;
  description?: string;
  expected_length: number;
  expected_width: number;
  expected_thickness?: number;
  unit: string;
  pos_tolerance: number;
  neg_tolerance: number;
  calibration_factor: number;
  created_at: string;
  updated_at: string;
  references: ProductReference[];
  inspections_count: number;
}

export interface DefectItem {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  location?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  confidence: number;
  description: string;
}

export interface CheckResult {
  check_name: string;
  executed: boolean;
  status: 'PASS' | 'REVIEW' | 'FAIL' | 'SKIPPED';
  score_or_value?: number | null;
  threshold_or_tolerance?: string | null;
  explanation: string;
  limitations?: string | null;
}

export interface InspectionRecord {
  id: string;
  product_id?: string | null;
  product_name?: string | null;
  mode: 'dimensional' | 'defect' | 'reference' | 'combined';
  inspection_image_path: string;
  annotated_image_path?: string | null;
  heatmap_image_path?: string | null;
  reference_image_path?: string | null;
  overall_status: 'PASS' | 'REVIEW' | 'FAIL';
  overall_explanation: string;
  anomaly_score?: number | null;
  anomaly_threshold?: number | null;
  anomaly_status?: string | null;
  measured_length?: number | null;
  measured_width?: number | null;
  expected_length?: number | null;
  expected_width?: number | null;
  length_deviation?: number | null;
  width_deviation?: number | null;
  unit: string;
  dimensional_status?: string | null;
  reference_similarity_score?: number | null;
  reference_status?: string | null;
  detected_defects: DefectItem[];
  checks_executed: CheckResult[];
  limitations: string[];
  metadata: Record<string, any>;
  created_at: string;
}

export interface DashboardStats {
  total_inspections: number;
  passed_inspections: number;
  failed_inspections: number;
  review_inspections: number;
  pass_rate: number;
  registered_products_count: number;
  total_references_count: number;
  model_ready: boolean;
  model_device: string;
  recent_inspections: InspectionRecord[];
  category_distribution: Record<string, number>;
  daily_trend: Array<{
    date: string;
    total: number;
    pass: number;
    fail: number;
    review: number;
  }>;
}

export interface ModelStatus {
  is_ready: boolean;
  model_name: string;
  architecture: string;
  backbone: string;
  embedding_dim: number;
  device: string;
  device_name: string;
  weights_status: string;
  total_reference_banks: number;
  total_reference_embeddings: number;
  supported_defect_types: string[];
  last_evaluated_at?: string | null;
  evaluation_metrics: Record<string, any>;
  training_instructions: string;
}
