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
