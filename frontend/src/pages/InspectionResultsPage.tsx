import React, { useEffect, useState } from 'react';
import { 
  Download, 
  ArrowLeft, 
  RefreshCw, 
  AlertTriangle, 
  Ruler, 
  Eye, 
  FileText, 
  Info 
} from 'lucide-react';
import type { InspectionRecord } from '../types';
import { fetchInspection, getImageUrl, getPdfReportUrl, getJsonReportUrl } from '../services/api';
import { StatusBadge, ModeBadge } from '../components/StatusBadge';

interface InspectionResultsPageProps {
  inspectionId: string;
  onBack: () => void;
  onInspectAgain: () => void;
}

export const InspectionResultsPage: React.FC<InspectionResultsPageProps> = ({
  inspectionId,
  onBack,
  onInspectAgain
}) => {
  const [record, setRecord] = useState<InspectionRecord | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeImageView, setActiveImageView] = useState<'annotated' | 'heatmap' | 'original' | 'reference'>('annotated');

  useEffect(() => {
    setLoading(true);
    fetchInspection(inspectionId)
      .then((data) => {
        setRecord(data);
        if (data.annotated_image_path) {
          setActiveImageView('annotated');
        } else if (data.heatmap_image_path) {
          setActiveImageView('heatmap');
        } else {
          setActiveImageView('original');
        }
      })
      .catch((err) => setError(err.message || 'Failed to load inspection record'))
      .finally(() => setLoading(false));
  }, [inspectionId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-slate-400 font-mono text-sm">Decoding inspection telemetry and visual overlays...</p>
      </div>
    );
  }

  if (error || !record) {
    return (
      <div className="p-8 max-w-3xl mx-auto text-center space-y-4">
        <div className="bg-rose-950/40 border border-rose-800 rounded-xl p-6">
          <AlertTriangle className="w-10 h-10 text-rose-400 mx-auto mb-2" />
          <h2 className="text-lg font-bold text-white">Record Not Found</h2>
          <p className="text-sm text-slate-300 mt-1">{error || 'Inspection ID invalid'}</p>
          <button
            onClick={onBack}
            className="mt-4 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  let currentImageUrl = '';
  if (activeImageView === 'annotated' && record.annotated_image_path) {
    currentImageUrl = getImageUrl(record.annotated_image_path);
  } else if (activeImageView === 'heatmap' && record.heatmap_image_path) {
    currentImageUrl = getImageUrl(record.heatmap_image_path);
  } else if (activeImageView === 'reference' && record.reference_image_path) {
    currentImageUrl = getImageUrl(record.reference_image_path);
  } else {
    currentImageUrl = getImageUrl(record.inspection_image_path);
  }

  return (
    <div className="space-y-8 pb-16">
      {/* Top Navigation & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="p-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg text-slate-300 hover:text-white transition-colors"
            title="Go Back"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold font-mono text-white">
                AUDIT REPORT // <span className="text-cyan-400">{record.id.substring(0, 8)}</span>
              </span>
              <ModeBadge mode={record.mode} />
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Specimen: <span className="text-white font-medium">{record.product_name || 'Generic Sample'}</span> • Logged on {new Date(record.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Export and Action buttons */}
        <div className="flex items-center space-x-2.5">
          <a
            href={getPdfReportUrl(record.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1.5 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 hover:text-white rounded-lg text-xs font-medium transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>Download PDF</span>
          </a>
          <a
            href={getJsonReportUrl(record.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1.5 px-3 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-400 hover:text-white rounded-lg text-xs font-mono transition-colors"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>JSON</span>
          </a>
          <button
            onClick={onInspectAgain}
            className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-lg text-xs transition-colors shadow-sm shadow-cyan-500/20"
          >
            Inspect Another
          </button>
        </div>
      </div>

      {/* Decision Outcome Banner */}
      <div className={`p-5 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
        record.overall_status === 'PASS'
          ? 'bg-emerald-950/40 border-emerald-800/60 text-emerald-200'
          : record.overall_status === 'FAIL'
          ? 'bg-rose-950/40 border-rose-800/60 text-rose-200'
          : 'bg-amber-950/40 border-amber-800/60 text-amber-200'
      }`}>
        <div className="flex items-start space-x-3.5">
          <div className="mt-0.5">
            <StatusBadge status={record.overall_status} size="lg" />
          </div>
          <div>
            <h2 className="text-sm font-bold tracking-wide uppercase font-mono">
              Final System Verification
            </h2>
            <p className="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
              {record.overall_explanation}
            </p>
          </div>
        </div>

        <div className="font-mono text-right text-xs shrink-0 self-end sm:self-center border-t sm:border-t-0 sm:border-l border-slate-800/80 pt-2 sm:pt-0 sm:pl-4">
          <div className="text-slate-400">Tolerance Criteria:</div>
          <div className="font-semibold text-white">Strict Deterministic QC</div>
        </div>
      </div>

      {/* Main Inspection Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Viewer */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between bg-slate-900 p-1.5 rounded-xl border border-slate-800">
            <div className="flex items-center space-x-1 text-xs">
              {record.annotated_image_path && (
                <button
                  onClick={() => setActiveImageView('annotated')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                    activeImageView === 'annotated'
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Metrology HUD
                </button>
              )}
              {record.heatmap_image_path && (
                <button
                  onClick={() => setActiveImageView('heatmap')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                    activeImageView === 'heatmap'
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Defect Heatmap
                </button>
              )}
              <button
                onClick={() => setActiveImageView('original')}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                  activeImageView === 'original'
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Raw Specimen
              </button>
              {record.reference_image_path && (
                <button
                  onClick={() => setActiveImageView('reference')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                    activeImageView === 'reference'
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Golden Reference
                </button>
              )}
            </div>

            <span className="text-[10px] font-mono text-slate-500 uppercase px-2">
              Layer: {activeImageView}
            </span>
          </div>

          <div className="relative bg-slate-950 border border-slate-800 rounded-xl overflow-hidden min-h-[420px] flex items-center justify-center p-2 group">
            {currentImageUrl ? (
              <img
                src={currentImageUrl}
                alt={`Inspection layer ${activeImageView}`}
                className="max-h-[520px] w-auto object-contain rounded-lg shadow-2xl transition-all"
              />
            ) : (
              <div className="text-slate-500 text-xs font-mono">No imagery layer available</div>
            )}

            <div className="absolute bottom-4 left-4 px-3 py-1 rounded bg-slate-950/80 backdrop-blur-md border border-slate-800 text-[11px] font-mono text-slate-300">
              {activeImageView === 'annotated' && 'Optical Metrology: MinAreaRect & Dimensional Deviations'}
              {activeImageView === 'heatmap' && 'Anomaly Heatmap: ResNet18 Layer4 Patch Distance Overlay'}
              {activeImageView === 'original' && 'Raw Specimen: Native Optical Sensor Frame'}
              {activeImageView === 'reference' && 'Approved Golden Reference Specimen'}
            </div>
          </div>
        </div>

        {/* Right Column: Quantitative Metrology */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <Ruler className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider">
                  Optical Metrology Results
                </h3>
              </div>
              {record.dimensional_status && (
                <StatusBadge status={record.dimensional_status} size="sm" />
              )}
            </div>

            {record.measured_length !== null && record.measured_length !== undefined ? (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                    <span className="text-[10px] font-mono text-slate-400 uppercase">Length Axis</span>
                    <div className="text-lg font-bold text-white font-mono mt-0.5">
                      {record.measured_length.toFixed(2)} <span className="text-xs text-slate-400 font-normal">{record.unit}</span>
                    </div>
                    <div className="flex items-center justify-between text-[11px] mt-1.5 pt-1.5 border-t border-slate-800">
                      <span className="text-slate-500">Exp: {record.expected_length ?? '—'}</span>
                      <span className={`font-mono font-medium ${
                        record.length_deviation && Math.abs(record.length_deviation) > 2.0 ? 'text-rose-400' : 'text-emerald-400'
                      }`}>
                        Δ {record.length_deviation ? (record.length_deviation > 0 ? `+${record.length_deviation}` : record.length_deviation) : '0.00'}
                      </span>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                    <span className="text-[10px] font-mono text-slate-400 uppercase">Width Axis</span>
                    <div className="text-lg font-bold text-white font-mono mt-0.5">
                      {record.measured_width?.toFixed(2) ?? '—'} <span className="text-xs text-slate-400 font-normal">{record.unit}</span>
                    </div>
                    <div className="flex items-center justify-between text-[11px] mt-1.5 pt-1.5 border-t border-slate-800">
                      <span className="text-slate-500">Exp: {record.expected_width ?? '—'}</span>
                      <span className={`font-mono font-medium ${
                        record.width_deviation && Math.abs(record.width_deviation) > 2.0 ? 'text-rose-400' : 'text-emerald-400'
                      }`}>
                        Δ {record.width_deviation ? (record.width_deviation > 0 ? `+${record.width_deviation}` : record.width_deviation) : '0.00'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="text-[11px] text-slate-400 font-mono bg-slate-950/60 p-2 rounded border border-slate-800/50">
                  Formula: Deviation = Measured ({record.unit}) − Expected ({record.unit})
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">
                Dimensional measurement was not enabled or no contour could be isolated.
              </p>
            )}
          </div>

          {/* Anomaly & Surface Defect Summary */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <Eye className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider">
                  Anomaly & Defect Analysis
                </h3>
              </div>
              {record.anomaly_status && (
                <StatusBadge status={record.anomaly_status} size="sm" />
              )}
            </div>

            {record.anomaly_score !== null && record.anomaly_score !== undefined && (
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400 font-mono">Visual Anomaly Score</span>
                  <span className="font-mono font-bold text-white">
                    {record.anomaly_score.toFixed(3)}
                    <span className="text-slate-500 font-normal"> / Thresh: {record.anomaly_threshold?.toFixed(2) || '0.32'}</span>
                  </span>
                </div>
                <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
                  <div
                    className={`h-full rounded-full transition-all ${
                      record.anomaly_score >= (record.anomaly_threshold || 0.32)
                        ? 'bg-rose-500'
                        : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(100, record.anomaly_score * 100)}%` }}
                  />
                </div>
              </div>
            )}

            {record.reference_similarity_score !== null && record.reference_similarity_score !== undefined && (
              <div className="flex justify-between items-center text-xs pt-1 border-t border-slate-800/60">
                <span className="text-slate-400 font-mono">Golden Reference Similarity:</span>
                <span className="font-mono text-cyan-400 font-semibold">
                  {(record.reference_similarity_score * 100).toFixed(1)}% match
                </span>
              </div>
            )}

            <div className="space-y-2 pt-2">
              <span className="text-[11px] font-mono text-slate-400 uppercase">
                Detected Defect Entities ({record.detected_defects.length})
              </span>
              {record.detected_defects.length > 0 ? (
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {record.detected_defects.map((def) => (
                    <div
                      key={def.id}
                      className="bg-slate-950 border border-slate-800/80 p-2.5 rounded-lg text-xs space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-rose-300 font-mono uppercase">{def.type}</span>
                        <span className={`text-[10px] uppercase font-mono px-1.5 py-0.5 rounded ${
                          def.severity === 'high' ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-amber-950 text-amber-300'
                        }`}>
                          {def.severity} severity
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400">{def.description}</p>
                      <div className="text-[10px] font-mono text-slate-500">
                        Confidence: {(def.confidence * 100).toFixed(0)}%
                        {def.location && ` • Box: (${def.location.x}, ${def.location.y})`}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800 text-center text-xs text-emerald-400 font-mono">
                  ✓ Zero surface fractures, scratches, or voids identified.
                </div>
              )}
            </div>
          </div>

          {/* Checkpoints Breakdown */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-3">
            <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider border-b border-slate-800 pb-2">
              Inspection Checkpoints Breakdown
            </h3>
            <div className="space-y-2 text-xs">
              {record.checks_executed.map((c, i) => (
                <div key={i} className="flex items-start justify-between p-2 rounded bg-slate-950/60 border border-slate-800/60">
                  <div className="space-y-0.5 max-w-[260px]">
                    <div className="font-semibold text-white">{c.check_name}</div>
                    <div className="text-[11px] text-slate-400">{c.explanation}</div>
                  </div>
                  <StatusBadge status={c.status} size="sm" />
                </div>
              ))}
            </div>
          </div>

          {/* Disclaimers */}
          {record.limitations && record.limitations.length > 0 && (
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 space-y-2 text-xs">
              <div className="flex items-center space-x-1.5 text-slate-400 font-mono">
                <Info className="w-3.5 h-3.5 text-cyan-400" />
                <span className="uppercase text-[11px] font-bold">Optical Limitations & Disclaimers</span>
              </div>
              <ul className="space-y-1 text-[11px] text-slate-500 list-disc list-inside">
                {record.limitations.map((lim, idx) => (
                  <li key={idx}>{lim}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
