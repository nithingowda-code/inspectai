import type {
  Product,
  InspectionRecord,
  DashboardStats,
  ModelStatus,
  ProductReference
} from '../types';

const API_BASE = '/api';

export function getImageUrl(filePath: string | null | undefined): string {
  if (!filePath) return '';
  if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
    return filePath;
  }
  const idx = filePath.indexOf('/data/');
  if (idx !== -1) {
    return filePath.substring(idx);
  }
  if (filePath.startsWith('data/')) {
    return '/' + filePath;
  }
  return `/data/${filePath}`;
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const res = await fetch(`${API_BASE}/dashboard/stats`);
  if (!res.ok) throw new Error(`Failed to fetch dashboard statistics: ${res.statusText}`);
  return res.json();
}

export async function fetchProducts(): Promise<Product[]> {
  const res = await fetch(`${API_BASE}/products`);
  if (!res.ok) throw new Error(`Failed to fetch products: ${res.statusText}`);
  return res.json();
}

export async function fetchProduct(id: string): Promise<Product> {
  const res = await fetch(`${API_BASE}/products/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch product: ${res.statusText}`);
  return res.json();
}

export async function createProduct(productData: Partial<Product>): Promise<Product> {
  const res = await fetch(`${API_BASE}/products`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(productData),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to create product: ${res.statusText}`);
  }
  return res.json();
}

export async function updateProduct(id: string, productData: Partial<Product>): Promise<Product> {
  const res = await fetch(`${API_BASE}/products/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(productData),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to update product: ${res.statusText}`);
  }
  return res.json();
}

export async function deleteProduct(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/products/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete product: ${res.statusText}`);
}

export async function uploadReferenceImage(
  productId: string,
  file: File,
  isPrimary: boolean = false
): Promise<ProductReference> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('is_primary', String(isPrimary));

  const res = await fetch(`${API_BASE}/products/${productId}/references`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to upload reference image: ${res.statusText}`);
  }
  return res.json();
}

export async function deleteReferenceImage(productId: string, refId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/products/${productId}/references/${refId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete reference: ${res.statusText}`);
}

export async function runInspection(formData: FormData): Promise<InspectionRecord> {
  const res = await fetch(`${API_BASE}/inspections/run`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Inspection failed: ${res.statusText}`);
  }
  return res.json();
}

export interface DetectedChange {
  id: string;
  classification?: string;
  category?: string;
  type?: string;
  severity: string;
  location: { x: number; y: number; width: number; height: number };
  area_px: number;
  area_percent_of_object?: number;
  confidence_note?: string;
  confidence: number;
  description?: string;
}

export interface ComparisonResult {
  comparison_id: string;
  inspection_id?: string;
  overall_status: 'PASS' | 'FAIL' | 'REVIEW';
  overall_explanation: string;
  difference_index: number;
  similarity_index: number;
  sub_scores?: {
    shape_similarity: number;
    dimension_match: number;
    surface_integrity: number;
    deep_feature_similarity: number;
  };
  score_disclaimer?: string;
  dimensions?: {
    scale_method: string;
    unit: string;
    is_calibrated: boolean;
    ideal_length_px: number;
    ideal_width_px: number;
    test_length_px: number;
    test_width_px: number;
    length_deviation_pct: number;
    width_deviation_pct: number;
    area_deviation_pct: number;
    measured_length?: number | null;
    measured_width?: number | null;
    expected_length?: number | null;
    expected_width?: number | null;
    length_deviation?: number | null;
    width_deviation?: number | null;
    tolerance_status: string;
    explanation: string;
  };
  detected_regions?: DetectedChange[];
  checks_executed?: Array<{
    check_name: string;
    executed: boolean;
    status: string;
    score_or_value?: any;
    threshold_or_tolerance?: string;
    explanation: string;
    limitations?: string;
  }>;
  limitations: string[];
  alignment_quality?: {
    method: string;
    reliable: boolean;
    inliers_count: number;
    inlier_ratio: number;
    reprojection_error: number;
  };
  reference_image_url: string | null;
  inspection_image_url: string | null;
  heatmap_image_url: string | null;
  sidebyside_image_url: string | null;
  overlay_image_url: string | null;
  annotated_image_url: string | null;
  // Compatibility fields
  status?: 'PASS' | 'FAIL' | 'REVIEW';
  similarity_score?: number | null;
  anomaly_score?: number | null;
  explanation?: string;
  detected_changes?: DetectedChange[];
}

export interface RunComparisonOptions {
  referenceFile: File;
  inspectionFile: File;
  expectedLength?: number;
  expectedWidth?: number;
  posTolerance?: number;
  negTolerance?: number;
  unit?: string;
  scaleMethod?: string;
}

export async function runComparison(
  referenceOrOptions: File | RunComparisonOptions,
  maybeInspectionFile?: File
): Promise<ComparisonResult> {
  const formData = new FormData();

  if (referenceOrOptions instanceof File) {
    formData.append('reference_file', referenceOrOptions);
    if (maybeInspectionFile) {
      formData.append('inspection_file', maybeInspectionFile);
    }
  } else {
    formData.append('reference_file', referenceOrOptions.referenceFile);
    formData.append('inspection_file', referenceOrOptions.inspectionFile);
    if (referenceOrOptions.expectedLength !== undefined) {
      formData.append('expected_length', String(referenceOrOptions.expectedLength));
    }
    if (referenceOrOptions.expectedWidth !== undefined) {
      formData.append('expected_width', String(referenceOrOptions.expectedWidth));
    }
    if (referenceOrOptions.posTolerance !== undefined) {
      formData.append('pos_tolerance', String(referenceOrOptions.posTolerance));
    }
    if (referenceOrOptions.negTolerance !== undefined) {
      formData.append('neg_tolerance', String(referenceOrOptions.negTolerance));
    }
    if (referenceOrOptions.unit) {
      formData.append('unit', referenceOrOptions.unit);
    }
    if (referenceOrOptions.scaleMethod) {
      formData.append('scale_method', referenceOrOptions.scaleMethod);
    }
  }

  const res = await fetch(`${API_BASE}/compare`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Comparison failed: ${res.statusText}`);
  }
  return res.json();
}

export async function saveProductFromComparison(formData: FormData): Promise<{ status: string; product_id: string; name: string }> {
  const res = await fetch(`${API_BASE}/inspections/save-product-from-comparison`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Save product failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchInspections(params: {
  productId?: string;
  status?: string;
  mode?: string;
  search?: string;
  limit?: number;
  offset?: number;
} = {}): Promise<InspectionRecord[]> {
  const query = new URLSearchParams();
  if (params.productId) query.append('product_id', params.productId);
  if (params.status) query.append('status', params.status);
  if (params.mode) query.append('mode', params.mode);
  if (params.search) query.append('search', params.search);
  if (params.limit) query.append('limit', String(params.limit));
  if (params.offset) query.append('offset', String(params.offset));

  const res = await fetch(`${API_BASE}/inspections?${query.toString()}`);
  if (!res.ok) throw new Error(`Failed to fetch inspections: ${res.statusText}`);
  return res.json();
}

export async function fetchInspection(id: string): Promise<InspectionRecord> {
  const res = await fetch(`${API_BASE}/inspections/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch inspection details: ${res.statusText}`);
  return res.json();
}

export async function fetchModelStatus(): Promise<ModelStatus> {
  const res = await fetch(`${API_BASE}/model/status`);
  if (!res.ok) throw new Error(`Failed to fetch model status: ${res.statusText}`);
  return res.json();
}

export function getPdfReportUrl(id: string): string {
  return `${API_BASE}/inspections/${id}/report`;
}

export function getJsonReportUrl(id: string): string {
  return `${API_BASE}/inspections/${id}/report/json`;
}
