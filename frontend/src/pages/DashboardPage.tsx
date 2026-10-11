import React, { useEffect, useState } from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Scan, 
  Layers, 
  ArrowUpRight, 
  Cpu, 
  RefreshCw,
  Plus,
  Clock
} from 'lucide-react';
import type { DashboardStats, Product } from '../types';
import { fetchDashboardStats, fetchProducts } from '../services/api';
import { StatusBadge, ModeBadge } from '../components/StatusBadge';

interface DashboardPageProps {
  onNavigate: (tab: string, inspectionId?: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, prodsData] = await Promise.all([
        fetchDashboardStats(),
        fetchProducts()
      ]);
      setStats(statsData);
      setProducts(prodsData);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading && !stats) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-slate-400 font-mono text-sm">Querying inspection database & hardware telemetry...</p>
      </div>
    );
  }

  if (error && !stats) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <div className="bg-rose-950/40 border border-rose-800/60 rounded-xl p-6 text-center space-y-3">
          <AlertTriangle className="w-10 h-10 text-rose-400 mx-auto" />
          <h3 className="text-lg font-bold text-white">Connection Error</h3>
          <p className="text-sm text-slate-300">{error}</p>
          <button
            onClick={loadData}
            className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-sm font-medium transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Top Banner / Hero */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white font-mono">
            MISSION CONTROL // <span className="text-cyan-400">QUALITY AUDIT</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time optical metrology, deep anomaly scores, and golden reference compliance telemetry.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={loadData}
            className="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white rounded-lg transition-colors"
            title="Refresh statistics"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => onNavigate('products')}
            className="flex items-center space-x-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white rounded-lg text-sm font-medium transition-colors"
          >
            <Plus className="w-4 h-4 text-cyan-400" />
            <span>Register Product</span>
          </button>
          <button
            onClick={() => onNavigate('inspect')}
            className="flex items-center space-x-2 px-5 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-lg text-sm transition-all shadow-lg shadow-cyan-500/20"
          >
            <Scan className="w-4 h-4" />
            <span>New Inspection</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Inspections */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Total Inspections</span>
            <span className="p-2 bg-slate-800 rounded-lg text-slate-300">
              <Scan className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline space-x-3">
            <span className="text-3xl font-bold text-white font-mono">{stats?.total_inspections ?? 0}</span>
            <span className="text-xs text-slate-400 font-mono">records in DB</span>
          </div>
          <div className="mt-2 text-xs text-slate-500 flex items-center space-x-1">
            <span>Pass rate:</span>
            <span className="font-semibold text-emerald-400">{stats?.pass_rate ?? 0}%</span>
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-cyan-500" />
        </div>

        {/* Passed */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-emerald-400">Passed Quality</span>
            <span className="p-2 bg-emerald-950/60 text-emerald-400 border border-emerald-800/40 rounded-lg">
              <CheckCircle2 className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline space-x-3">
            <span className="text-3xl font-bold text-emerald-400 font-mono">{stats?.passed_inspections ?? 0}</span>
            <span className="text-xs text-slate-400">within tolerances</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Acceptance standard fully verified
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-500" />
        </div>

        {/* Failed */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-rose-400">Rejected / Failed</span>
            <span className="p-2 bg-rose-950/60 text-rose-400 border border-rose-800/40 rounded-lg">
              <XCircle className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline space-x-3">
            <span className="text-3xl font-bold text-rose-400 font-mono">{stats?.failed_inspections ?? 0}</span>
            <span className="text-xs text-slate-400">anomalous / out-of-tol</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Flaws or dimensional deviation flagged
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-rose-500" />
        </div>

        {/* Requiring Review */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-amber-400">Operator Review</span>
            <span className="p-2 bg-amber-950/60 text-amber-400 border border-amber-800/40 rounded-lg">
              <AlertTriangle className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline space-x-3">
            <span className="text-3xl font-bold text-amber-400 font-mono">{stats?.review_inspections ?? 0}</span>
            <span className="text-xs text-slate-400">inconclusive / uncalibrated</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Requires human visual verification
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-amber-500" />
        </div>
      </div>

      {/* Hardware & Model Readiness Status Banner */}
      <div className="bg-slate-900 border border-cyan-900/40 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/30">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-semibold text-white">AI Vision Engine: ResNet-18 Backbone Active</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800">
                {stats?.model_device || 'Host CPU'}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Multi-scale patch anomaly estimation • Zero-shot reference comparison • OpenCV sub-pixel metrology
            </p>
          </div>
        </div>
        <button
          onClick={() => onNavigate('model')}
          className="flex items-center space-x-1.5 text-xs text-cyan-400 hover:text-cyan-300 font-medium px-3 py-1.5 rounded-md bg-cyan-950/50 border border-cyan-800/60 self-start sm:self-auto transition-colors"
        >
          <span>View Model Intelligence</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Main Content: Recent Inspections & Product Catalog */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Inspections Table (2 columns wide) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-cyan-400" />
              <h2 className="text-base font-bold text-white font-mono uppercase tracking-wide">
                Recent Quality Audits
              </h2>
            </div>
            <button
              onClick={() => onNavigate('history')}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 font-mono"
            >
              <span>View Full History ({stats?.total_inspections ?? 0})</span>
              <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>

          <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden">
            {stats?.recent_inspections && stats.recent_inspections.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800 font-mono">
                    <tr>
                      <th className="py-3 px-4">Inspection ID</th>
                      <th className="py-3 px-4">Product</th>
                      <th className="py-3 px-4">Mode</th>
                      <th className="py-3 px-4">Anomaly</th>
                      <th className="py-3 px-4">Outcome</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {stats.recent_inspections.map((rec) => (
                      <tr 
                        key={rec.id} 
                        className="hover:bg-slate-800/40 transition-colors cursor-pointer group"
                        onClick={() => onNavigate('results', rec.id)}
                      >
                        <td className="py-3.5 px-4 font-mono font-medium text-cyan-400">
                          {rec.id.substring(0, 8)}...
                        </td>
                        <td className="py-3.5 px-4 font-medium text-white max-w-[160px] truncate">
                          {rec.product_name || 'Generic Sample'}
                        </td>
                        <td className="py-3.5 px-4">
                          <ModeBadge mode={rec.mode} />
                        </td>
                        <td className="py-3.5 px-4 font-mono">
                          {rec.anomaly_score !== null && rec.anomaly_score !== undefined ? (
                            <span className={rec.anomaly_score >= (rec.anomaly_threshold || 0.32) ? 'text-rose-400 font-bold' : 'text-slate-300'}>
                              {rec.anomaly_score.toFixed(3)}
                            </span>
                          ) : (
                            <span className="text-slate-500">—</span>
                          )}
                        </td>
                        <td className="py-3.5 px-4">
                          <StatusBadge status={rec.overall_status} size="sm" />
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <span className="text-xs text-slate-400 group-hover:text-cyan-400 inline-flex items-center space-x-1">
                            <span>Open</span>
                            <ArrowUpRight className="w-3 h-3" />
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-8 text-center space-y-3">
                <Scan className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-sm text-slate-400">No inspection records logged yet.</p>
                <button
                  onClick={() => onNavigate('inspect')}
                  className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold"
                >
                  Run First Inspection
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Registered Products Quick Card (1 column wide) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              <h2 className="text-base font-bold text-white font-mono uppercase tracking-wide">
                Registered Catalog ({products.length})
              </h2>
            </div>
            <button
              onClick={() => onNavigate('products')}
              className="text-xs text-cyan-400 hover:text-cyan-300 font-mono"
            >
              Manage
            </button>
          </div>

          <div className="space-y-3">
            {products.slice(0, 4).map((p) => (
              <div
                key={p.id}
                onClick={() => onNavigate('products')}
                className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 p-4 rounded-xl cursor-pointer transition-all hover:bg-slate-800/40 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white text-sm truncate max-w-[180px]">{p.name}</span>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                    {p.category}
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
                  <span>Target: {p.expected_length}×{p.expected_width} {p.unit}</span>
                  <span className="text-slate-500">±{p.pos_tolerance}{p.unit}</span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-800/60 pt-2">
                  <span>{p.references.length} golden reference(s)</span>
                  <span className="text-cyan-400 font-medium">Ready</span>
                </div>
              </div>
            ))}

            {products.length === 0 && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-center space-y-2">
                <p className="text-xs text-slate-400">No manufactured products registered.</p>
                <button
                  onClick={() => onNavigate('products')}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-lg text-xs"
                >
                  Register Profile
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
