import React, { useState, useEffect } from 'react';
import { 
  History, 
  Search, 
  Download, 
  Eye, 
  RefreshCw, 
  FileText 
} from 'lucide-react';
import type { InspectionRecord, Product } from '../types';
import { fetchInspections, fetchProducts, getPdfReportUrl, getJsonReportUrl } from '../services/api';
import { StatusBadge, ModeBadge } from '../components/StatusBadge';

interface InspectionHistoryPageProps {
  onSelectInspection: (inspectionId: string) => void;
}

export const InspectionHistoryPage: React.FC<InspectionHistoryPageProps> = ({
  onSelectInspection
}) => {
  const [inspections, setInspections] = useState<InspectionRecord[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Filters
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [modeFilter, setModeFilter] = useState<string>('');
  const [productFilter, setProductFilter] = useState<string>('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [inspData, prodsData] = await Promise.all([
        fetchInspections({
          search: searchTerm || undefined,
          status: statusFilter || undefined,
          mode: modeFilter || undefined,
          productId: productFilter || undefined,
          limit: 100,
        }),
        fetchProducts()
      ]);
      setInspections(inspData);
      setProducts(prodsData);
    } catch (err: any) {
      console.error('Failed to load inspection history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter, modeFilter, productFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white font-mono flex items-center space-x-2">
            <History className="w-6 h-6 text-cyan-400" />
            <span>INSPECTION AUDIT LOGS</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Historical quality assurance records, measurement deviations, anomaly telemetry, and certified reports.
          </p>
        </div>
        <button
          onClick={loadData}
          className="flex items-center space-x-2 px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-mono self-start sm:self-auto transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Records</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search by Inspection ID or defect details..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <select
            value={productFilter}
            onChange={(e) => setProductFilter(e.target.value)}
            className="px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Products</option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Statuses</option>
            <option value="PASS">PASS</option>
            <option value="REVIEW">REVIEW</option>
            <option value="FAIL">FAIL</option>
          </select>

          <select
            value={modeFilter}
            onChange={(e) => setModeFilter(e.target.value)}
            className="px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Modes</option>
            <option value="combined">Combined</option>
            <option value="dimensional">Dimensional</option>
            <option value="defect">Defect</option>
            <option value="reference">Reference</option>
          </select>

          <button
            type="submit"
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-mono font-semibold transition-colors"
          >
            Apply Filters
          </button>
        </form>
      </div>

      {/* Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        {loading ? (
          <div className="py-16 text-center space-y-3">
            <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin mx-auto" />
            <p className="text-xs text-slate-400 font-mono">Querying audit logs...</p>
          </div>
        ) : inspections.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 font-mono">
                <tr>
                  <th className="py-3 px-4">Inspection ID</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Target Product</th>
                  <th className="py-3 px-4">Mode</th>
                  <th className="py-3 px-4">Measured Size</th>
                  <th className="py-3 px-4">Anomaly</th>
                  <th className="py-3 px-4">Verdict</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {inspections.map((rec) => (
                  <tr
                    key={rec.id}
                    className="hover:bg-slate-800/40 transition-colors group cursor-pointer"
                    onClick={() => onSelectInspection(rec.id)}
                  >
                    <td className="py-3.5 px-4 font-mono font-medium text-cyan-400">
                      {rec.id.substring(0, 8)}...
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                      {new Date(rec.created_at).toLocaleDateString()} {new Date(rec.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-white max-w-[160px] truncate">
                      {rec.product_name || 'Generic Sample'}
                    </td>
                    <td className="py-3.5 px-4">
                      <ModeBadge mode={rec.mode} />
                    </td>
                    <td className="py-3.5 px-4 font-mono text-[11px]">
                      {rec.measured_length ? (
                        <span>
                          {rec.measured_length}×{rec.measured_width} {rec.unit}
                        </span>
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 font-mono">
                      {rec.anomaly_score !== null && rec.anomaly_score !== undefined ? (
                        <span className={rec.anomaly_score >= (rec.anomaly_threshold || 0.32) ? 'text-rose-400 font-bold' : 'text-slate-300'}>
                          {rec.anomaly_score.toFixed(3)}
                        </span>
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={rec.overall_status} size="sm" />
                    </td>
                    <td className="py-3.5 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end space-x-1">
                        <button
                          onClick={() => onSelectInspection(rec.id)}
                          className="p-1.5 text-slate-400 hover:text-cyan-400 rounded hover:bg-slate-800"
                          title="View Result Details"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                        <a
                          href={getPdfReportUrl(rec.id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1.5 text-slate-400 hover:text-emerald-400 rounded hover:bg-slate-800"
                          title="Download PDF Report"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </a>
                        <a
                          href={getJsonReportUrl(rec.id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1.5 text-slate-400 hover:text-amber-400 rounded hover:bg-slate-800"
                          title="Download Raw JSON"
                        >
                          <FileText className="w-3.5 h-3.5" />
                        </a>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-16 text-center space-y-3">
            <History className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-xs text-slate-400">No inspection records match current filter criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
};
