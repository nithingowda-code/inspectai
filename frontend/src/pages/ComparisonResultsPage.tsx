import React, { useState } from 'react';
import {
  ArrowLeft,
  GitCompare,
  AlertTriangle,
  CheckCircle,
  Activity,
  RefreshCw,
  Download,
  BookmarkPlus,
  Ruler,
  ShieldAlert,
  Sliders,
  Check,
  X
} from 'lucide-react';
import { saveProductFromComparison, type ComparisonResult } from '../services/api';

interface ComparisonResultsPageProps {
  result: ComparisonResult;
  onBack: () => void;
  onCompareAgain: () => void;
}

type ViewMode = 'sidebyside' | 'heatmap' | 'overlay' | 'annotated' | 'reference' | 'inspection';

export const ComparisonResultsPage: React.FC<ComparisonResultsPageProps> = ({
  result,
  onBack,
  onCompareAgain,
}) => {
  const [view, setView] = useState<ViewMode>(
    result.sidebyside_image_url
      ? 'sidebyside'
      : result.heatmap_image_url
      ? 'heatmap'
      : 'reference'
  );

  // Save as Product state
  const [isSavingProduct, setIsSavingProduct] = useState(false);
  const [showSaveModal, setShowSaveModal] = useState(false);
  const [productName, setProductName] = useState('');
  const [productCategory, setProductCategory] = useState('Mechanical');
  const [productSavedSuccess, setProductSavedSuccess] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const overallStatus = result.overall_status || result.status || 'REVIEW';
  const explanation = result.overall_explanation || result.explanation || 'Inspection completed.';
  const diffIndex = result.difference_index !== undefined ? result.difference_index : (result.anomaly_score ? (result.anomaly_score * 100).toFixed(1) : '—');
  const simIndex = result.similarity_index !== undefined ? result.similarity_index : (result.similarity_score ? (result.similarity_score * 100).toFixed(1) : '—');

  const statusColors = {
    PASS: 'bg-emerald-950/40 border-emerald-800 text-emerald-200',
    FAIL: 'bg-rose-950/40 border-rose-800 text-rose-200',
    REVIEW: 'bg-amber-950/40 border-amber-800 text-amber-200',
  }[overallStatus] || 'bg-slate-900 border-slate-700 text-slate-200';

  const currentImageUrl: string | null = {
    sidebyside: result.sidebyside_image_url,
    heatmap: result.heatmap_image_url,
    overlay: result.overlay_image_url,
    annotated: result.annotated_image_url,
    reference: result.reference_image_url,
    inspection: result.inspection_image_url,
  }[view];

  const viewOptions: { id: ViewMode; label: string; available: boolean }[] = [
    { id: 'sidebyside', label: 'Side-by-Side Composite', available: Boolean(result.sidebyside_image_url) },
    { id: 'heatmap', label: 'Difference Heatmap', available: Boolean(result.heatmap_image_url) },
    { id: 'overlay', label: 'Silhouette Overlay', available: Boolean(result.overlay_image_url) },
    { id: 'annotated', label: 'Annotated Defects', available: Boolean(result.annotated_image_url) },
    { id: 'reference', label: 'Ideal Reference', available: Boolean(result.reference_image_url) },
    { id: 'inspection', label: 'Test Inspection', available: Boolean(result.inspection_image_url) },
  ];

  const detectedRegions = result.detected_regions || result.detected_changes || [];

  const handleDownloadPdf = () => {
    if (result.inspection_id) {
      window.open(`/api/inspections/${result.inspection_id}/report`, '_blank');
    } else {
      alert('Report PDF will be available after saving.');
    }
  };

  const handleSaveProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!productName.trim()) return;

    setIsSavingProduct(true);
    setSaveError(null);
    try {
      const formData = new FormData();
      formData.append('comparison_id', result.comparison_id);
      formData.append('name', productName.trim());
      formData.append('category', productCategory);
      if (result.dimensions?.expected_length) {
        formData.append('expected_length', String(result.dimensions.expected_length));
      }
      if (result.dimensions?.expected_width) {
        formData.append('expected_width', String(result.dimensions.expected_width));
      }
      if (result.dimensions?.unit) {
        formData.append('unit', result.dimensions.unit);
      }

      await saveProductFromComparison(formData);
      setProductSavedSuccess(true);
      setTimeout(() => setShowSaveModal(false), 1800);
    } catch (err: any) {
      setSaveError(err.message || 'Failed to save product.');
    } finally {
      setIsSavingProduct(false);
    }
  };

  return (
    <div className="space-y-8 pb-16 max-w-6xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="p-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg text-slate-300 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <GitCompare className="w-5 h-5 text-cyan-400" />
              <span className="text-xl font-bold font-mono text-white">
                QUICK COMPARE REPORT //&nbsp;
                <span className="text-cyan-400">{result.comparison_id.toUpperCase()}</span>
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Multimodal Visual Anomaly &amp; Optical Metrology Inspection
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {result.inspection_id && (
            <button
              onClick={handleDownloadPdf}
              className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-mono flex items-center space-x-2 transition-colors"
            >
              <Download className="w-4 h-4 text-cyan-400" />
              <span>Download PDF</span>
            </button>
          )}

          <button
            onClick={() => setShowSaveModal(true)}
            className="px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-mono flex items-center space-x-2 transition-colors"
          >
            <BookmarkPlus className="w-4 h-4 text-emerald-400" />
            <span>Save as Product</span>
          </button>

          <button
            onClick={onCompareAgain}
            className="px-3.5 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-lg text-xs font-mono flex items-center space-x-2 shadow-lg transition-all"
          >
            <RefreshCw className="w-4 h-4" />
            <span>New Comparison</span>
          </button>
        </div>
      </div>

      {/* Decision Banner */}
      <div className={`border rounded-xl p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 shadow-xl ${statusColors}`}>
        <div className="flex items-start space-x-4">
          <div className="mt-0.5">
            {overallStatus === 'PASS' && <CheckCircle className="w-7 h-7 text-emerald-400" />}
            {overallStatus === 'FAIL' && <AlertTriangle className="w-7 h-7 text-rose-400" />}
            {overallStatus === 'REVIEW' && <Activity className="w-7 h-7 text-amber-400" />}
          </div>
          <div>
            <div className="flex items-center space-x-3">
              <span className="text-xl font-bold font-mono tracking-wider">
                STATUS: {overallStatus}
              </span>
              <span className="text-xs font-mono bg-slate-950/60 px-2.5 py-0.5 rounded border border-current">
                Diff Index: {diffIndex}/100
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
              {explanation}
            </p>
          </div>
        </div>
        <div className="text-right shrink-0">
          <div className="text-2xl font-black font-mono text-cyan-400">
            {simIndex}%
          </div>
          <div className="text-[11px] font-mono text-slate-400">Similarity Index</div>
        </div>
      </div>

      {/* Main Image Viewer with Mode Selector */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl overflow-hidden shadow-2xl">
        {/* View Mode Bar */}
        <div className="flex flex-wrap items-center justify-between p-3 border-b border-slate-800 bg-slate-950/50 gap-2">
          <div className="flex flex-wrap gap-1.5">
            {viewOptions.map((opt) => opt.available && (
              <button
                key={opt.id}
                onClick={() => setView(opt.id)}
                className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-all ${
                  view === opt.id
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/50 font-bold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>

          <span className="text-[11px] font-mono text-slate-500 hidden sm:inline">
            Spatial Alignment: {result.alignment_quality?.method || 'SIFT Homography'}
          </span>
        </div>

        {/* Display Canvas */}
        <div className="p-4 flex items-center justify-center bg-slate-950 min-h-[380px] max-h-[580px] overflow-hidden">
          {currentImageUrl ? (
            <img
              src={currentImageUrl}
              alt={view}
              className="max-h-[540px] max-w-full object-contain rounded-lg border border-slate-800 shadow-2xl"
            />
          ) : (
            <div className="text-center text-slate-500 text-xs font-mono py-16">
              View not available for this run.
            </div>
          )}
        </div>

        {/* Viewer Caption / Legend */}
        <div className="p-3 bg-slate-950/80 border-t border-slate-800 text-xs font-mono text-slate-400 flex flex-wrap items-center justify-between gap-2">
          <div>
            {view === 'sidebyside' && 'Panel 1: Ideal Reference | Panel 2: Aligned Test Object | Panel 3: Master Difference Heatmap'}
            {view === 'heatmap' && 'Master Anomaly Heatmap: Deep ResNet18 patch distance + SSIM + silhouette differences.'}
            {view === 'overlay' && 'Silhouette Overlay: White outline = Ideal; Red/Orange = Missing material; Cyan/Lime = Extra flash.'}
            {view === 'annotated' && 'Numbered bounding boxes highlight detected surface defects and boundary deviations.'}
            {view === 'reference' && 'Original Golden Reference Image (Image A)'}
            {view === 'inspection' && 'Original Test Specimen Image (Image B)'}
          </div>
          {result.alignment_quality && (
            <div className="text-slate-500">
              Inliers: {result.alignment_quality.inliers_count} ({((result.alignment_quality.inlier_ratio || 0) * 100).toFixed(0)}%) | Error: {result.alignment_quality.reprojection_error}px
            </div>
          )}
        </div>
      </div>

      {/* Metrics & Sub-Scores Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {result.sub_scores ? (
          <>
            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl space-y-2">
              <div className="text-xs font-mono text-slate-400 uppercase">Shape Similarity</div>
              <div className="text-2xl font-bold font-mono text-cyan-400">
                {result.sub_scores.shape_similarity}%
              </div>
              <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-cyan-400 h-1.5 rounded-full"
                  style={{ width: `${result.sub_scores.shape_similarity}%` }}
                />
              </div>
              <div className="text-[11px] text-slate-500">Silhouette IoU &amp; Hu Moments</div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl space-y-2">
              <div className="text-xs font-mono text-slate-400 uppercase">Dimension Match</div>
              <div className="text-2xl font-bold font-mono text-emerald-400">
                {result.sub_scores.dimension_match}%
              </div>
              <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-emerald-400 h-1.5 rounded-full"
                  style={{ width: `${result.sub_scores.dimension_match}%` }}
                />
              </div>
              <div className="text-[11px] text-slate-500">Length/Width metrology deviation</div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl space-y-2">
              <div className="text-xs font-mono text-slate-400 uppercase">Surface Integrity</div>
              <div className="text-2xl font-bold font-mono text-amber-400">
                {result.sub_scores.surface_integrity}%
              </div>
              <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-amber-400 h-1.5 rounded-full"
                  style={{ width: `${result.sub_scores.surface_integrity}%` }}
                />
              </div>
              <div className="text-[11px] text-slate-500">SSIM &amp; Lab colour diff</div>
            </div>

            <div className="bg-slate-900/60 border border-slate-800 p-4 rounded-xl space-y-2">
              <div className="text-xs font-mono text-slate-400 uppercase">Deep Features</div>
              <div className="text-2xl font-bold font-mono text-indigo-400">
                {result.sub_scores.deep_feature_similarity}%
              </div>
              <div className="w-full bg-slate-950 rounded-full h-1.5 overflow-hidden">
                <div
                  className="bg-indigo-400 h-1.5 rounded-full"
                  style={{ width: `${result.sub_scores.deep_feature_similarity}%` }}
                />
              </div>
              <div className="text-[11px] text-slate-500">ResNet18 spatial patch distance</div>
            </div>
          </>
        ) : (
          <div className="col-span-4 bg-slate-900/50 p-4 rounded-xl text-center text-xs text-slate-500">
            Sub-scores computed from optical signals.
          </div>
        )}
      </div>

      {/* Dimensional Measurement Table */}
      {result.dimensions && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2 text-sm font-semibold text-white font-mono uppercase tracking-wider">
              <Ruler className="w-4 h-4 text-cyan-400" />
              <span>Dimensional Metrology Verification</span>
            </div>
            <span className="text-xs font-mono text-slate-400">
              Scale Mode: {result.dimensions.scale_method} ({result.dimensions.is_calibrated ? 'Calibrated' : 'Relative Uncalibrated'})
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs font-mono text-left">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2 px-3">Dimension</th>
                  <th className="py-2 px-3">Expected</th>
                  <th className="py-2 px-3">Measured</th>
                  <th className="py-2 px-3">Deviation</th>
                  <th className="py-2 px-3">% Deviation</th>
                  <th className="py-2 px-3">Tolerance Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 text-slate-200">
                <tr>
                  <td className="py-2.5 px-3 font-semibold text-white">Length</td>
                  <td className="py-2.5 px-3">
                    {result.dimensions.expected_length ? `${result.dimensions.expected_length}${result.dimensions.unit}` : '—'}
                  </td>
                  <td className="py-2.5 px-3 font-bold text-cyan-300">
                    {result.dimensions.measured_length ? `${result.dimensions.measured_length}${result.dimensions.unit}` : `${result.dimensions.test_length_px}px`}
                  </td>
                  <td className="py-2.5 px-3">
                    {result.dimensions.length_deviation !== undefined && result.dimensions.length_deviation !== null
                      ? `${result.dimensions.length_deviation > 0 ? '+' : ''}${result.dimensions.length_deviation}${result.dimensions.unit}`
                      : '—'}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className={Math.abs(result.dimensions.length_deviation_pct) > 2.0 ? 'text-amber-400 font-bold' : 'text-slate-300'}>
                      {result.dimensions.length_deviation_pct > 0 ? '+' : ''}{result.dimensions.length_deviation_pct}%
                    </span>
                  </td>
                  <td className="py-2.5 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      result.dimensions.tolerance_status === 'PASS'
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                        : result.dimensions.tolerance_status === 'FAIL'
                        ? 'bg-rose-950 text-rose-400 border border-rose-800'
                        : 'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}>
                      {result.dimensions.tolerance_status}
                    </span>
                  </td>
                </tr>

                <tr>
                  <td className="py-2.5 px-3 font-semibold text-white">Width</td>
                  <td className="py-2.5 px-3">
                    {result.dimensions.expected_width ? `${result.dimensions.expected_width}${result.dimensions.unit}` : '—'}
                  </td>
                  <td className="py-2.5 px-3 font-bold text-cyan-300">
                    {result.dimensions.measured_width ? `${result.dimensions.measured_width}${result.dimensions.unit}` : `${result.dimensions.test_width_px}px`}
                  </td>
                  <td className="py-2.5 px-3">
                    {result.dimensions.width_deviation !== undefined && result.dimensions.width_deviation !== null
                      ? `${result.dimensions.width_deviation > 0 ? '+' : ''}${result.dimensions.width_deviation}${result.dimensions.unit}`
                      : '—'}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className={Math.abs(result.dimensions.width_deviation_pct) > 2.0 ? 'text-amber-400 font-bold' : 'text-slate-300'}>
                      {result.dimensions.width_deviation_pct > 0 ? '+' : ''}{result.dimensions.width_deviation_pct}%
                    </span>
                  </td>
                  <td className="py-2.5 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      result.dimensions.tolerance_status === 'PASS'
                        ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                        : result.dimensions.tolerance_status === 'FAIL'
                        ? 'bg-rose-950 text-rose-400 border border-rose-800'
                        : 'bg-slate-800 text-slate-400 border border-slate-700'
                    }`}>
                      {result.dimensions.tolerance_status}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <p className="text-[11px] text-slate-500 font-mono mt-1">
            {result.dimensions.explanation}
          </p>
        </div>
      )}

      {/* Suspected Differences / Detected Regions */}
      <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center space-x-2 text-sm font-semibold text-white font-mono uppercase tracking-wider">
            <Sliders className="w-4 h-4 text-cyan-400" />
            <span>Suspected Differences &amp; Anomaly Regions ({detectedRegions.length})</span>
          </div>
          <span className="text-xs font-mono text-slate-400">Evidence-based classifications</span>
        </div>

        {detectedRegions.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-xs font-mono text-left">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2 px-3">ID</th>
                  <th className="py-2 px-3">Suspected Classification</th>
                  <th className="py-2 px-3">Severity</th>
                  <th className="py-2 px-3">Location (x, y, w, h)</th>
                  <th className="py-2 px-3">Area (% Obj)</th>
                  <th className="py-2 px-3">Confidence Note</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 text-slate-200">
                {detectedRegions.map((reg) => (
                  <tr key={reg.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 font-bold text-cyan-400">{reg.id}</td>
                    <td className="py-2.5 px-3 font-semibold text-white">
                      {reg.classification || reg.description || reg.type}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] uppercase font-bold ${
                        reg.severity === 'critical' || reg.severity === 'high'
                          ? 'bg-rose-950 text-rose-300 border border-rose-800'
                          : reg.severity === 'medium'
                          ? 'bg-amber-950 text-amber-300 border border-amber-800'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}>
                        {reg.severity}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-400">
                      {reg.location ? `${reg.location.x}, ${reg.location.y} (${reg.location.width}×${reg.location.height})` : '—'}
                    </td>
                    <td className="py-2.5 px-3 text-cyan-300 font-bold">
                      {reg.area_percent_of_object !== undefined ? `${reg.area_percent_of_object}%` : `${reg.area_px}px`}
                    </td>
                    <td className="py-2.5 px-3 text-[11px] text-slate-400 max-w-xs">
                      {reg.confidence_note || `Confidence score: ${(reg.confidence * 100).toFixed(0)}%`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500 font-mono text-xs">
            ✓ No structural or surface anomalies detected above threshold.
          </div>
        )}
      </div>

      {/* Per-Check Execution Table */}
      {result.checks_executed && result.checks_executed.length > 0 && (
        <div className="bg-slate-900/60 border border-slate-800 rounded-xl p-5 space-y-3">
          <div className="flex items-center space-x-2 text-sm font-semibold text-white font-mono uppercase tracking-wider border-b border-slate-800 pb-3">
            <Activity className="w-4 h-4 text-cyan-400" />
            <span>Inspection Engine Routine Verification</span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs font-mono text-left">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="py-2 px-3">Check Routine</th>
                  <th className="py-2 px-3">Executed</th>
                  <th className="py-2 px-3">Status</th>
                  <th className="py-2 px-3">Observed Value</th>
                  <th className="py-2 px-3">Tolerance / Criterion</th>
                  <th className="py-2 px-3">Explanation &amp; Boundary Conditions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50 text-slate-200">
                {result.checks_executed.map((chk, i) => (
                  <tr key={i} className="hover:bg-slate-800/30">
                    <td className="py-2.5 px-3 font-semibold text-white">{chk.check_name}</td>
                    <td className="py-2.5 px-3">
                      {chk.executed ? (
                        <span className="text-emerald-400 font-bold">YES</span>
                      ) : (
                        <span className="text-rose-400 font-bold">NO</span>
                      )}
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        chk.status === 'PASS'
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                          : chk.status === 'FAIL'
                          ? 'bg-rose-950 text-rose-400 border border-rose-800'
                          : 'bg-amber-950 text-amber-300 border border-amber-800'
                      }`}>
                        {chk.status}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-cyan-300">{chk.score_or_value !== undefined ? String(chk.score_or_value) : '—'}</td>
                    <td className="py-2.5 px-3 text-slate-400">{chk.threshold_or_tolerance || '—'}</td>
                    <td className="py-2.5 px-3 text-[11px] text-slate-400 max-w-sm">{chk.explanation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Honest Limitations Panel */}
      <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-5 space-y-2">
        <div className="flex items-center space-x-2 text-xs font-mono uppercase text-amber-400 font-semibold">
          <ShieldAlert className="w-4 h-4" />
          <span>System Scope, Assumptions &amp; Optical Limitations</span>
        </div>
        <ul className="list-disc list-inside text-xs text-slate-400 space-y-1 font-mono">
          <li>Optical 2D inspection assumes orthogonal perspective view with minimal perspective tilt.</li>
          <li>Real-world dimensions are accurate only when camera distance, focal length, and angle are identical between reference and test photos.</li>
          <li>Sub-surface structural defects, internal cracks, and 3D depth geometry cannot be evaluated from single planar images.</li>
          <li>All defect classifications are automated heuristic recommendations and require manual operator verification before scrapping parts.</li>
          {result.limitations?.map((lim, i) => (
            <li key={i}>{lim}</li>
          ))}
        </ul>
      </div>

      {/* Save Product Modal */}
      {showSaveModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-750 rounded-2xl p-6 max-w-md w-full space-y-5 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2 text-white font-mono font-bold text-sm">
                <BookmarkPlus className="w-4 h-4 text-emerald-400" />
                <span>Save Ideal Image as Registered Product</span>
              </div>
              <button
                type="button"
                onClick={() => setShowSaveModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {productSavedSuccess ? (
              <div className="text-center py-6 space-y-2">
                <div className="w-12 h-12 bg-emerald-950 border border-emerald-700 rounded-full flex items-center justify-center mx-auto text-emerald-400">
                  <Check className="w-6 h-6" />
                </div>
                <h4 className="text-white font-bold text-base font-mono">Product Registered Successfully!</h4>
                <p className="text-xs text-slate-400 font-mono">
                  "{productName}" is now saved in the system with its reference golden image.
                </p>
              </div>
            ) : (
              <form onSubmit={handleSaveProduct} className="space-y-4">
                <p className="text-xs text-slate-400">
                  Save the reference image from this comparison to your catalogue so you can inspect future manufactured batches against it anytime.
                </p>

                <div>
                  <label className="block text-xs font-mono text-slate-300 uppercase mb-1">Product Name</label>
                  <input
                    type="text"
                    required
                    value={productName}
                    onChange={(e) => setProductName(e.target.value)}
                    placeholder="e.g. Hex Titanium M10 Bracket"
                    className="w-full bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-cyan-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-mono text-slate-300 uppercase mb-1">Category</label>
                  <select
                    value={productCategory}
                    onChange={(e) => setProductCategory(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-cyan-500 focus:outline-none"
                  >
                    <option value="Mechanical">Mechanical</option>
                    <option value="Aerospace">Aerospace</option>
                    <option value="Electronics">Electronics</option>
                    <option value="Fasteners">Fasteners</option>
                    <option value="Medical">Medical Devices</option>
                    <option value="Automotive">Automotive</option>
                  </select>
                </div>

                {saveError && (
                  <p className="text-xs text-rose-400 font-mono">{saveError}</p>
                )}

                <div className="flex items-center justify-end space-x-3 pt-3">
                  <button
                    type="button"
                    onClick={() => setShowSaveModal(false)}
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs font-mono"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={isSavingProduct || !productName.trim()}
                    className="px-5 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold rounded-lg text-xs font-mono flex items-center space-x-2"
                  >
                    {isSavingProduct ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        <span>Saving...</span>
                      </>
                    ) : (
                      <>
                        <BookmarkPlus className="w-3.5 h-3.5" />
                        <span>Save Product</span>
                      </>
                    )}
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
