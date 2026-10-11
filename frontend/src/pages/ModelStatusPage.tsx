import React, { useEffect, useState } from 'react';
import { 
  Cpu, 
  CheckCircle2, 
  Layers, 
  Database, 
  RefreshCw, 
  AlertCircle, 
  FileCode, 
  HardDrive 
} from 'lucide-react';
import type { ModelStatus } from '../types';
import { fetchModelStatus } from '../services/api';

export const ModelStatusPage: React.FC = () => {
  const [status, setStatus] = useState<ModelStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadStatus = async () => {
    setLoading(true);
    try {
      const data = await fetchModelStatus();
      setStatus(data);
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve model telemetry');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-slate-400 font-mono text-sm">Querying neural backbone and hardware accelerator status...</p>
      </div>
    );
  }

  if (error || !status) {
    return (
      <div className="p-8 max-w-3xl mx-auto">
        <div className="bg-rose-950/40 border border-rose-800 rounded-xl p-6 text-center space-y-3">
          <AlertCircle className="w-10 h-10 text-rose-400 mx-auto" />
          <h2 className="text-lg font-bold text-white">Model Telemetry Unavailable</h2>
          <p className="text-sm text-slate-300">{error}</p>
          <button
            onClick={loadStatus}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-16 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white font-mono flex items-center space-x-2">
            <Cpu className="w-6 h-6 text-cyan-400" />
            <span>AI MODEL ARCHITECTURE & TELEMETRY</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Verified technical state of the computer vision pipeline, neural feature extractor, and local embedding banks.
          </p>
        </div>
        <button
          onClick={loadStatus}
          className="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white rounded-lg self-start sm:self-auto transition-colors"
          title="Refresh telemetry"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Hardware & Backbone Readiness Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 relative overflow-hidden bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-1">
            <span className="text-xs font-mono uppercase text-slate-500">Pipeline Status</span>
            <div className="flex items-center space-x-2 mt-1">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <span className="text-lg font-bold text-white font-mono">OPERATIONAL</span>
            </div>
            <p className="text-xs text-slate-400">Ready for instant zero-shot reference indexing.</p>
          </div>

          <div className="space-y-1">
            <span className="text-xs font-mono uppercase text-slate-500">Compute Hardware Device</span>
            <div className="text-lg font-bold text-cyan-400 font-mono mt-1">
              {status.device_name}
            </div>
            <p className="text-xs text-slate-400">Low-latency localized inference without cloud dependency.</p>
          </div>

          <div className="space-y-1">
            <span className="text-xs font-mono uppercase text-slate-500">Pretrained Weights</span>
            <div className="text-base font-semibold text-slate-200 mt-1">
              {status.weights_status}
            </div>
            <p className="text-xs text-slate-400">Torchvision ResNet-18 residual bottleneck layers.</p>
          </div>
        </div>
      </div>

      {/* Specifications & Artifacts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Architecture Specs */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider flex items-center space-x-2 border-b border-slate-800 pb-3">
            <Layers className="w-4 h-4 text-cyan-400" />
            <span>Neural Backbone Specifications</span>
          </h2>
          <div className="space-y-2.5 text-xs text-slate-300">
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Backbone Model:</span>
              <span className="font-mono text-white font-medium">{status.backbone}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Feature Vector Dimension:</span>
              <span className="font-mono text-cyan-400 font-medium">{status.embedding_dim}-dimensional</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Spatial Patch Representation:</span>
              <span className="font-mono text-white font-medium">Layer 4 (512 × 8 × 8)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Metric Formulation:</span>
              <span className="font-mono text-white font-medium">Patch L2 Norm + Global Cosine Distance</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Execution Framework:</span>
              <span className="font-mono text-white font-medium">PyTorch 2.x + TorchVision</span>
            </div>
          </div>
        </div>

        {/* Local Embeddings Banks */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider flex items-center space-x-2 border-b border-slate-800 pb-3">
            <Database className="w-4 h-4 text-cyan-400" />
            <span>Cached Product Reference Banks</span>
          </h2>
          <div className="space-y-2.5 text-xs text-slate-300">
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Registered Product Banks:</span>
              <span className="font-mono text-cyan-400 font-bold">{status.total_reference_banks} cache banks (.npz)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Total Reference Samples Indexed:</span>
              <span className="font-mono text-white font-medium">{status.total_reference_embeddings} golden samples</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Cache Storage Location:</span>
              <span className="font-mono text-slate-400 truncate max-w-[220px]">model_artifacts/products/</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Retraining Requirement:</span>
              <span className="font-mono text-emerald-400 font-medium">Zero Downtime (Dynamic Indexing)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Supported Defect Classes */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider flex items-center space-x-2 border-b border-slate-800 pb-3">
          <HardDrive className="w-4 h-4 text-cyan-400" />
          <span>Supported Manufacturing Flaw Classes</span>
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {status.supported_defect_types.map((type, i) => (
            <div key={i} className="bg-slate-950 p-3 rounded-lg border border-slate-800/80 text-xs text-slate-200 font-mono flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 shrink-0" />
              <span>{type}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Transparent Evaluation */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider flex items-center space-x-2 border-b border-slate-800 pb-3">
          <FileCode className="w-4 h-4 text-cyan-400" />
          <span>Evaluation Status & Industrial Training Pipeline</span>
        </h2>
        
        <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-xs space-y-2">
          <div className="flex items-center space-x-2 text-amber-400 font-mono font-semibold">
            <AlertCircle className="w-4 h-4" />
            <span>Honest Model Transparency Protocol:</span>
          </div>
          <p className="text-slate-300 leading-relaxed">
            {status.evaluation_metrics.status} — {status.evaluation_metrics.note}
          </p>
        </div>

        <div className="space-y-2">
          <span className="text-xs font-mono text-slate-400 uppercase">
            Dataset Training Instructions (MVTec AD / Custom Factory Data):
          </span>
          <pre className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-xs text-cyan-300 font-mono overflow-x-auto leading-relaxed">
            {status.training_instructions}
          </pre>
        </div>
      </div>
    </div>
  );
};
