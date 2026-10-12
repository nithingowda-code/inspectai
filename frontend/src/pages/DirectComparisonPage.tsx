import React, { useState, useRef } from 'react';
import {
  Upload,
  GitCompare,
  AlertCircle,
  RefreshCw,
  X,
  Ruler,
  Sparkles,
  Info
} from 'lucide-react';
import { runComparison, type ComparisonResult } from '../services/api';

interface DirectComparisonPageProps {
  onComparisonComplete: (result: ComparisonResult) => void;
}

interface ImageSlot {
  file: File | null;
  previewUrl: string | null;
  isDragging: boolean;
}

const SLOT_DEFAULTS: ImageSlot = { file: null, previewUrl: null, isDragging: false };

export const DirectComparisonPage: React.FC<DirectComparisonPageProps> = ({
  onComparisonComplete,
}) => {
  const [referenceSlot, setReferenceSlot] = useState<ImageSlot>({ ...SLOT_DEFAULTS });
  const [inspectionSlot, setInspectionSlot] = useState<ImageSlot>({ ...SLOT_DEFAULTS });

  // Dimensional specifications form
  const [expectedLength, setExpectedLength] = useState<string>('120');
  const [expectedWidth, setExpectedWidth] = useState<string>('60');
  const [unit, setUnit] = useState<string>('mm');
  const [posTolerance, setPosTolerance] = useState<string>('2.0');
  const [negTolerance, setNegTolerance] = useState<string>('2.0');
  const [scaleMethod, setScaleMethod] = useState<'same_setup' | 'marker' | 'relative_only'>('same_setup');
  const [sameCameraConfirmed, setSameCameraConfirmed] = useState<boolean>(true);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentStage, setCurrentStage] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const refInputRef = useRef<HTMLInputElement>(null);
  const inspInputRef = useRef<HTMLInputElement>(null);

  const setSlot = (
    which: 'reference' | 'inspection',
    patch: Partial<ImageSlot>
  ) => {
    if (which === 'reference') setReferenceSlot((s) => ({ ...s, ...patch }));
    else setInspectionSlot((s) => ({ ...s, ...patch }));
  };

  const handleFileSelect = (which: 'reference' | 'inspection', file: File) => {
    if (!file.type.startsWith('image/')) {
      setErrorMsg('Please upload a valid image file (JPEG, PNG, WEBP, BMP).');
      return;
    }
    setErrorMsg(null);
    const url = URL.createObjectURL(file);
    setSlot(which, { file, previewUrl: url });
  };

  const clearSlot = (which: 'reference' | 'inspection') => {
    setSlot(which, { file: null, previewUrl: null });
  };

  const handleDrop = (which: 'reference' | 'inspection') => (e: React.DragEvent) => {
    e.preventDefault();
    setSlot(which, { isDragging: false });
    if (e.dataTransfer.files?.length > 0) {
      handleFileSelect(which, e.dataTransfer.files[0]);
    }
  };

  // Sample quick loaders from /data/samples
  const loadSamplePair = async (sampleBase: string, _name?: string) => {
    setErrorMsg(null);
    try {
      const refRes = await fetch(`/data/samples/${sampleBase}_pass.jpg`);
      const inspRes = await fetch(`/data/samples/${sampleBase}_scratch_defect.jpg`);

      if (!refRes.ok || !inspRes.ok) {
        throw new Error('Sample images could not be loaded from server.');
      }

      const refBlob = await refRes.blob();
      const inspBlob = await inspRes.blob();

      const refFile = new File([refBlob], `${sampleBase}_reference_pass.jpg`, { type: 'image/jpeg' });
      const inspFile = new File([inspBlob], `${sampleBase}_test_scratch.jpg`, { type: 'image/jpeg' });

      setSlot('reference', { file: refFile, previewUrl: URL.createObjectURL(refFile) });
      setSlot('inspection', { file: inspFile, previewUrl: URL.createObjectURL(inspFile) });

      if (sampleBase === 'aerospace_bracket') {
        setExpectedLength('120');
        setExpectedWidth('60');
        setUnit('mm');
      } else if (sampleBase === 'polymer_bushing') {
        setExpectedLength('50');
        setExpectedWidth('50');
        setUnit('mm');
      } else if (sampleBase === 'smt_pcb') {
        setExpectedLength('80');
        setExpectedWidth('45');
        setUnit('mm');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to load sample pair.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!referenceSlot.file || !inspectionSlot.file) {
      setErrorMsg('Please upload both an Ideal Reference image and a Test Inspection image.');
      return;
    }

    if (scaleMethod === 'same_setup' && !sameCameraConfirmed) {
      setErrorMsg('Please confirm that both photos share the same camera distance and angle, or switch to Relative-Only mode.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);

    // Progressive stage simulation
    setCurrentStage('1/5: Validating image exposures & sharpness...');
    const stageTimer1 = setTimeout(() => setCurrentStage('2/5: Segmenting manufactured object silhouettes...'), 400);
    const stageTimer2 = setTimeout(() => setCurrentStage('3/5: SIFT & Contour spatial registration...'), 900);
    const stageTimer3 = setTimeout(() => setCurrentStage('4/5: Multimodal SSIM & Deep Feature anomaly analysis...'), 1400);
    const stageTimer4 = setTimeout(() => setCurrentStage('5/5: Computing dimensions & generating visual diffs...'), 1900);

    try {
      const expL = expectedLength ? parseFloat(expectedLength) : undefined;
      const expW = expectedWidth ? parseFloat(expectedWidth) : undefined;
      const posT = posTolerance ? parseFloat(posTolerance) : undefined;
      const negT = negTolerance ? parseFloat(negTolerance) : undefined;

      const result = await runComparison({
        referenceFile: referenceSlot.file,
        inspectionFile: inspectionSlot.file,
        expectedLength: expL,
        expectedWidth: expW,
        posTolerance: posT,
        negTolerance: negT,
        unit,
        scaleMethod
      });

      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);
      clearTimeout(stageTimer3);
      clearTimeout(stageTimer4);

      onComparisonComplete(result);
    } catch (err: any) {
      clearTimeout(stageTimer1);
      clearTimeout(stageTimer2);
      clearTimeout(stageTimer3);
      clearTimeout(stageTimer4);
      setErrorMsg(err.message || 'Comparison failed. Please verify image inputs.');
      setIsSubmitting(false);
    }
  };

  const UploadZone: React.FC<{
    which: 'reference' | 'inspection';
    label: string;
    sublabel: string;
    accentColor: string;
    slot: ImageSlot;
    inputRef: React.RefObject<HTMLInputElement | null>;
  }> = ({ which, label, sublabel, accentColor, slot, inputRef }) => (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <label className="text-sm font-semibold text-white font-mono uppercase tracking-wider flex items-center space-x-2">
          <span
            className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold text-slate-950 ${accentColor}`}
          >
            {which === 'reference' ? 'A' : 'B'}
          </span>
          <span>{label}</span>
        </label>
        {slot.file && (
          <button
            type="button"
            onClick={() => clearSlot(which)}
            className="text-xs text-slate-400 hover:text-rose-400 flex items-center space-x-1 transition-colors"
          >
            <X className="w-3.5 h-3.5" />
            <span>Clear</span>
          </button>
        )}
      </div>

      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => {
          if (e.target.files?.length) handleFileSelect(which, e.target.files[0]);
        }}
      />

      <div
        onClick={() => !slot.file && inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setSlot(which, { isDragging: true });
        }}
        onDragLeave={() => setSlot(which, { isDragging: false })}
        onDrop={handleDrop(which)}
        className={`relative rounded-xl border-2 transition-all duration-200 overflow-hidden ${
          slot.file
            ? 'border-slate-750 bg-slate-900/60'
            : slot.isDragging
            ? 'border-cyan-400 bg-cyan-950/20 cursor-copy'
            : 'border-dashed border-slate-700 hover:border-slate-500 bg-slate-900/40 hover:bg-slate-900/60 cursor-pointer'
        }`}
        style={{ minHeight: '260px' }}
      >
        {slot.previewUrl ? (
          <div className="relative group w-full h-full min-h-[260px] flex items-center justify-center bg-slate-950/80 p-3">
            <img
              src={slot.previewUrl}
              alt={label}
              className="max-h-56 max-w-full object-contain rounded-lg border border-slate-800 shadow-lg"
            />
            <div className="absolute inset-0 bg-slate-950/70 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center space-x-3">
              <button
                type="button"
                onClick={() => inputRef.current?.click()}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded text-xs font-mono border border-slate-600 transition-colors"
              >
                Change Image
              </button>
              <button
                type="button"
                onClick={() => clearSlot(which)}
                className="px-3 py-1.5 bg-rose-950/80 hover:bg-rose-900 text-rose-300 rounded text-xs font-mono border border-rose-800 transition-colors"
              >
                Remove
              </button>
            </div>
            {slot.file && (
              <div className="absolute bottom-2 left-2 right-2 flex justify-between items-center text-[11px] font-mono text-slate-400 bg-slate-950/80 px-2 py-1 rounded border border-slate-800">
                <span className="truncate max-w-[180px]">{slot.file.name}</span>
                <span>{(slot.file.size / 1024).toFixed(0)} KB</span>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center p-8 text-center min-h-[260px] space-y-3">
            <div
              className={`w-14 h-14 rounded-2xl flex items-center justify-center transition-colors ${
                slot.isDragging
                  ? 'bg-cyan-500/20 text-cyan-400'
                  : 'bg-slate-800/80 text-slate-400 group-hover:text-slate-300'
              }`}
            >
              <Upload className="w-7 h-7" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-200">
                Drag &amp; drop {label.toLowerCase()} image here
              </p>
              <p className="text-xs text-slate-400 mt-1">{sublabel}</p>
            </div>
            <span className="inline-block text-[11px] font-mono text-slate-400 bg-slate-800/60 px-2.5 py-1 rounded border border-slate-700/60">
              or browse from device
            </span>
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-16">
      {/* Hero Title */}
      <div className="border-b border-slate-800 pb-6 flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-cyan-400 text-xs font-mono uppercase tracking-widest mb-1.5">
            <GitCompare className="w-4 h-4" />
            <span>Universal Optical Comparator</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
            Quick Compare: Two-Image Quality Inspection
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-2xl">
            Upload an <strong className="text-emerald-400">Image A (Ideal / Golden Version)</strong> with expected dimensions, and an <strong className="text-amber-400">Image B (Test / Manufactured Object)</strong>. InspectAI registers, subtracts silhouettes, computes pixel SSIM, and extracts deep feature difference heatmaps in seconds.
          </p>
        </div>

        {/* Quick Sample Presets */}
        <div className="flex flex-wrap items-center gap-2 bg-slate-900/60 p-2 rounded-xl border border-slate-800">
          <span className="text-[11px] font-mono text-slate-400 px-1 flex items-center space-x-1">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Quick Samples:</span>
          </span>
          <button
            type="button"
            onClick={() => loadSamplePair('aerospace_bracket', 'Aerospace Bracket')}
            className="text-xs px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded font-mono border border-slate-700 transition-colors"
          >
            Bracket
          </button>
          <button
            type="button"
            onClick={() => loadSamplePair('polymer_bushing', 'Polymer Bushing')}
            className="text-xs px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded font-mono border border-slate-700 transition-colors"
          >
            Bushing
          </button>
          <button
            type="button"
            onClick={() => loadSamplePair('smt_pcb', 'SMT PCB')}
            className="text-xs px-2.5 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded font-mono border border-slate-700 transition-colors"
          >
            PCB
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Two Upload Zones */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <UploadZone
            which="reference"
            label="Image A: Ideal / Golden Object"
            sublabel="Unblemished reference specimen with known target dimensions"
            accentColor="bg-emerald-400"
            slot={referenceSlot}
            inputRef={refInputRef}
          />
          <UploadZone
            which="inspection"
            label="Image B: Test / Manufactured Object"
            sublabel="Manufactured object that may have defects, cracks, missing material, or warping"
            accentColor="bg-cyan-400"
            slot={inspectionSlot}
            inputRef={inspInputRef}
          />
        </div>

        {/* Ideal Object Dimensions & Metrology Calibration Panel */}
        <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center space-x-2 text-sm font-semibold text-white font-mono uppercase tracking-wider">
              <Ruler className="w-4 h-4 text-cyan-400" />
              <span>Dimensional Metrology &amp; Scale Calibration</span>
            </div>
            <span className="text-[11px] font-mono text-slate-400">Optical 2D Metrology</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-mono text-slate-300 uppercase mb-1">
                Ideal Length
              </label>
              <div className="relative">
                <input
                  type="number"
                  step="0.01"
                  value={expectedLength}
                  onChange={(e) => setExpectedLength(e.target.value)}
                  placeholder="e.g. 120"
                  className="w-full bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-cyan-500 focus:outline-none"
                />
                <span className="absolute right-3 top-2 text-xs font-mono text-slate-500">{unit}</span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 uppercase mb-1">
                Ideal Width
              </label>
              <div className="relative">
                <input
                  type="number"
                  step="0.01"
                  value={expectedWidth}
                  onChange={(e) => setExpectedWidth(e.target.value)}
                  placeholder="e.g. 60"
                  className="w-full bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-cyan-500 focus:outline-none"
                />
                <span className="absolute right-3 top-2 text-xs font-mono text-slate-500">{unit}</span>
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 uppercase mb-1">
                Tolerance (±)
              </label>
              <div className="flex space-x-2">
                <input
                  type="number"
                  step="0.1"
                  value={posTolerance}
                  onChange={(e) => {
                    setPosTolerance(e.target.value);
                    setNegTolerance(e.target.value);
                  }}
                  placeholder="2.0"
                  className="w-full bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-cyan-500 focus:outline-none"
                />
                <select
                  value={unit}
                  onChange={(e) => setUnit(e.target.value)}
                  className="bg-slate-950 border border-slate-750 rounded-lg px-2 text-xs text-white font-mono focus:border-cyan-500 focus:outline-none"
                >
                  <option value="mm">mm</option>
                  <option value="cm">cm</option>
                  <option value="in">in</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 uppercase mb-1">
                Scale Method
              </label>
              <select
                value={scaleMethod}
                onChange={(e) => setScaleMethod(e.target.value as any)}
                className="w-full bg-slate-950 border border-slate-750 rounded-lg px-3 py-2 text-sm text-white font-mono focus:border-cyan-500 focus:outline-none"
              >
                <option value="same_setup">Derived from Ideal Image (Same camera)</option>
                <option value="marker">Known-size Marker / Gauge</option>
                <option value="relative_only">Relative-only Mode (Percentage %)</option>
              </select>
            </div>
          </div>

          {scaleMethod === 'same_setup' && (
            <div className="flex items-start space-x-3 bg-slate-950/60 p-3 rounded-lg border border-slate-800 text-xs">
              <input
                type="checkbox"
                id="same_setup_check"
                checked={sameCameraConfirmed}
                onChange={(e) => setSameCameraConfirmed(e.target.checked)}
                className="mt-0.5 rounded border-slate-700 text-cyan-500 focus:ring-0"
              />
              <label htmlFor="same_setup_check" className="text-slate-300 cursor-pointer">
                <strong>Physical Assumption Confirmation:</strong> I confirm both photos were captured with the same camera model, sensor distance, and orthogonal perspective angle. The pixel-to-unit scale will be calibrated using Image A's physical dimensions.
              </label>
            </div>
          )}

          {scaleMethod === 'relative_only' && (
            <div className="flex items-center space-x-2 bg-amber-950/20 border border-amber-800/40 p-3 rounded-lg text-xs text-amber-300">
              <Info className="w-4 h-4 shrink-0" />
              <span>Uncalibrated mode active: Dimensions will be reported strictly as relative percentages (%) without claiming absolute physical units.</span>
            </div>
          )}
        </div>

        {/* Error message */}
        {errorMsg && (
          <div className="flex items-start space-x-3 bg-rose-950/40 border border-rose-800 rounded-xl p-4 text-rose-300 text-sm">
            <AlertCircle className="w-5 h-5 shrink-0 mt-0.5 text-rose-400" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Progress Display */}
        {isSubmitting && (
          <div className="bg-slate-900 border border-cyan-800/50 rounded-xl p-5 space-y-3 shadow-xl shadow-cyan-950/30">
            <div className="flex items-center justify-between text-xs font-mono">
              <span className="text-cyan-400 flex items-center space-x-2">
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Running 6-Stage Universal CV Inspection Engine...</span>
              </span>
              <span className="text-slate-400">{currentStage}</span>
            </div>
            <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
              <div className="bg-gradient-to-r from-cyan-500 to-emerald-400 h-2 rounded-full animate-pulse w-4/5" />
            </div>
          </div>
        )}

        {/* Submit Action */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          <p className="text-xs text-slate-500 font-mono">
            {referenceSlot.file && inspectionSlot.file
              ? '✓ Both reference and test images loaded. Ready to inspect.'
              : 'Waiting for both reference and inspection images...'}
          </p>

          <button
            type="submit"
            disabled={isSubmitting || !referenceSlot.file || !inspectionSlot.file}
            className={`w-full sm:w-auto px-8 py-3.5 rounded-xl font-bold font-mono text-sm uppercase tracking-wider flex items-center justify-center space-x-3 shadow-lg transition-all ${
              isSubmitting || !referenceSlot.file || !inspectionSlot.file
                ? 'bg-slate-800 text-slate-500 border border-slate-700/50 cursor-not-allowed'
                : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-cyan-500/20 hover:shadow-cyan-500/30 active:scale-[0.99]'
            }`}
          >
            {isSubmitting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Comparing Objects...</span>
              </>
            ) : (
              <>
                <GitCompare className="w-4 h-4" />
                <span>Run Quick Inspection</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
