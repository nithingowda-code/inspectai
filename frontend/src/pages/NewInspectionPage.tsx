import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, 
  Scan, 
  Sliders, 
  AlertCircle, 
  Check, 
  Zap, 
  Ruler, 
  Eye, 
  FileCheck, 
  RefreshCw 
} from 'lucide-react';
import type { Product } from '../types';
import { fetchProducts, runInspection } from '../services/api';

interface NewInspectionPageProps {
  onInspectionComplete: (inspectionId: string) => void;
  onNavigateToProducts: () => void;
}

export const NewInspectionPage: React.FC<NewInspectionPageProps> = ({
  onInspectionComplete,
  onNavigateToProducts,
}) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<string>('');
  const [mode, setMode] = useState<string>('combined');

  // Image upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);

  // Advanced metrology overrides
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);
  const [customCalib, setCustomCalib] = useState<string>('');
  const [customLength, setCustomLength] = useState<string>('');
  const [customWidth, setCustomWidth] = useState<string>('');
  const [customTol, setCustomTol] = useState<string>('');

  // Execution state
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchProducts()
      .then((prods) => {
        setProducts(prods);
        if (prods.length > 0) {
          setSelectedProductId(prods[0].id);
        }
      })
      .catch((err) => console.error('Failed to load products:', err));
  }, []);

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setErrorMsg('Please upload a valid image file (JPEG, PNG, WEBP, BMP).');
      return;
    }
    setErrorMsg(null);
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  // Helper to load sample test images directly from server
  const loadSampleImage = async (samplePath: string, sampleProductId?: string) => {
    try {
      setErrorMsg(null);
      const res = await fetch(samplePath);
      if (!res.ok) throw new Error('Sample image file not found on server');
      const blob = await res.blob();
      const filename = samplePath.split('/').pop() || 'sample.jpg';
      const file = new File([blob], filename, { type: 'image/jpeg' });
      handleFileSelect(file);
      if (sampleProductId) {
        setSelectedProductId(sampleProductId);
      }
    } catch (err: any) {
      setErrorMsg(`Failed to load sample: ${err.message}`);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setErrorMsg('Please upload or select an inspection target image.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (selectedProductId) {
        formData.append('product_id', selectedProductId);
      }
      formData.append('mode', mode);

      if (customCalib) formData.append('calibration_factor', customCalib);
      if (customLength) formData.append('custom_expected_length', customLength);
      if (customWidth) formData.append('custom_expected_width', customWidth);
      if (customTol) formData.append('custom_tolerance', customTol);

      const record = await runInspection(formData);
      onInspectionComplete(record.id);
    } catch (err: any) {
      setErrorMsg(err.message || 'Inspection execution failed. Please verify input parameters.');
      setIsSubmitting(false);
    }
  };

  const activeProduct = products.find((p) => p.id === selectedProductId);

  const modes = [
    {
      id: 'combined',
      title: 'Combined Quality Audit',
      desc: 'All-inclusive: Optical Metrology + Surface Flaw Detection + Reference Comparison',
      icon: Zap,
    },
    {
      id: 'dimensional',
      title: 'Dimensional Metrology',
      desc: 'Sub-pixel contour boundary calculation, rotated length/width, and tolerance delta',
      icon: Ruler,
    },
    {
      id: 'defect',
      title: 'Surface Defect Analysis',
      desc: 'ResNet18 patch features + morphological detection for cracks, scratches, and voids',
      icon: Eye,
    },
    {
      id: 'reference',
      title: 'Golden Reference Comparison',
      desc: 'Visual feature cosine distance against product approved baseline bank',
      icon: FileCheck,
    },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-16">
      {/* Page Header */}
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-2xl font-bold tracking-tight text-white font-mono flex items-center space-x-2">
          <Scan className="w-6 h-6 text-cyan-400" />
          <span>INITIALIZE QUALITY INSPECTION</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Upload manufacturing component imagery for automated optical metrology and visual defect validation.
        </p>
      </div>

      {errorMsg && (
        <div className="bg-rose-950/50 border border-rose-800/80 rounded-xl p-4 flex items-start space-x-3 text-rose-300 text-sm">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-semibold text-rose-200">Execution Error: </span>
            {errorMsg}
          </div>
        </div>
      )}

      {/* Quick Test Demo Samples Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
            <span>Quick Test Samples (Instant Simulation)</span>
          </span>
          <span className="text-[11px] text-slate-500">Click to prefill image & profile</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {(() => {
            const bracketId = products.find(p => p.name.toLowerCase().includes('bracket'))?.id;
            const pcbId = products.find(p => p.name.toLowerCase().includes('pcb'))?.id;
            const bushingId = products.find(p => p.name.toLowerCase().includes('bushing'))?.id;
            return (
              <>
                <button
                  type="button"
                  onClick={() => loadSampleImage('/data/samples/aerospace_bracket_pass.jpg', bracketId)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-emerald-500/50 text-xs text-emerald-300 flex items-center space-x-1.5 transition-colors"
                >
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span>Titanium Bracket [Pass Sample]</span>
                </button>
                <button
                  type="button"
                  onClick={() => loadSampleImage('/data/samples/aerospace_bracket_scratch_defect.jpg', bracketId)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-rose-500/50 text-xs text-rose-300 flex items-center space-x-1.5 transition-colors"
                >
                  <span className="w-2 h-2 rounded-full bg-rose-500" />
                  <span>Titanium Bracket [Scratch Defect]</span>
                </button>
                <button
                  type="button"
                  onClick={() => loadSampleImage('/data/samples/aerospace_bracket_dimension_fail.jpg', bracketId)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-rose-500/50 text-xs text-rose-300 flex items-center space-x-1.5 transition-colors"
                >
                  <span className="w-2 h-2 rounded-full bg-rose-500" />
                  <span>Titanium Bracket [Dimension Over-Tol]</span>
                </button>
                <button
                  type="button"
                  onClick={() => loadSampleImage('/data/samples/smt_pcb_pass.jpg', pcbId)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-slate-300 flex items-center space-x-1.5 transition-colors"
                >
                  <span>SMT PCB Assembly [Normal]</span>
                </button>
                <button
                  type="button"
                  onClick={() => loadSampleImage('/data/samples/polymer_bushing_pass.jpg', bushingId)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-slate-300 flex items-center space-x-1.5 transition-colors"
                >
                  <span>Bearing Bushing [Normal]</span>
                </button>
              </>
            );
          })()}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Image Upload Area (7 columns) */}
          <div className="lg:col-span-7 space-y-4">
            <label className="block text-sm font-semibold text-white font-mono uppercase tracking-wider">
              1. Inspection Target Image
            </label>

            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all min-h-[320px] flex flex-col items-center justify-center ${
                isDragging
                  ? 'border-cyan-400 bg-cyan-950/20'
                  : previewUrl
                  ? 'border-slate-700 bg-slate-900/60'
                  : 'border-slate-700 hover:border-slate-600 bg-slate-900/40'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files.length > 0) {
                    handleFileSelect(e.target.files[0]);
                  }
                }}
              />

              {previewUrl ? (
                <div className="space-y-4 w-full">
                  <div className="relative max-h-72 w-full overflow-hidden rounded-lg border border-slate-700 bg-black/40 flex items-center justify-center">
                    <img
                      src={previewUrl}
                      alt="Inspection target preview"
                      className="max-h-72 object-contain"
                    />
                    {isSubmitting && (
                      <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm flex flex-col items-center justify-center space-y-3">
                        <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
                        <span className="text-cyan-400 font-mono text-xs font-bold tracking-wider animate-pulse">
                          EXECUTING METROLOGY & ANOMALY SCAN...
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-400 px-2 font-mono">
                    <span className="truncate max-w-[240px] text-white">{selectedFile?.name}</span>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        fileInputRef.current?.click();
                      }}
                      className="text-cyan-400 hover:text-cyan-300"
                    >
                      Replace Image
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3 text-slate-400">
                  <div className="w-14 h-14 rounded-full bg-slate-800 text-cyan-400 border border-slate-700 flex items-center justify-center mx-auto">
                    <Upload className="w-6 h-6" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">Drag and drop inspection image here</p>
                    <p className="text-xs text-slate-500 mt-1">Supports high-res JPEG, PNG, WEBP, BMP</p>
                  </div>
                  <button
                    type="button"
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white rounded-lg text-xs font-medium"
                  >
                    Browse Files
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Profile & Parameters (5 columns) */}
          <div className="lg:col-span-5 space-y-6">
            {/* Product Profile Selection */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="block text-sm font-semibold text-white font-mono uppercase tracking-wider">
                  2. Product Specification
                </label>
                <button
                  type="button"
                  onClick={onNavigateToProducts}
                  className="text-xs text-cyan-400 hover:text-cyan-300"
                >
                  + Add Product
                </button>
              </div>

              <select
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 focus:border-cyan-500 rounded-lg text-sm text-white focus:outline-none"
              >
                <option value="">-- Generic Unregistered Specimen --</option>
                {products.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.category})
                  </option>
                ))}
              </select>

              {activeProduct && (
                <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-3 text-xs space-y-1.5 text-slate-300">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Design Size:</span>
                    <span className="font-mono font-medium text-white">
                      {activeProduct.expected_length} × {activeProduct.expected_width} {activeProduct.unit}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Tolerances:</span>
                    <span className="font-mono text-emerald-400">
                      -{activeProduct.neg_tolerance} / +{activeProduct.pos_tolerance} {activeProduct.unit}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Golden Reference:</span>
                    <span className="font-mono text-cyan-400">
                      {activeProduct.references.length} indexed sample(s)
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Mode Selection */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-white font-mono uppercase tracking-wider">
                3. Inspection Mode
              </label>

              <div className="space-y-2">
                {modes.map((m) => {
                  const Icon = m.icon;
                  const isSelected = mode === m.id;
                  return (
                    <div
                      key={m.id}
                      onClick={() => setMode(m.id)}
                      className={`p-3 rounded-xl border cursor-pointer transition-all flex items-start space-x-3 ${
                        isSelected
                          ? 'border-cyan-500 bg-cyan-950/20 text-white shadow-sm shadow-cyan-950'
                          : 'border-slate-800 bg-slate-900/60 text-slate-300 hover:border-slate-700'
                      }`}
                    >
                      <div className={`p-2 rounded-lg mt-0.5 ${
                        isSelected ? 'bg-cyan-500 text-slate-950' : 'bg-slate-800 text-slate-400'
                      }`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold font-mono uppercase tracking-wider">
                            {m.title}
                          </span>
                          {isSelected && <Check className="w-3.5 h-3.5 text-cyan-400" />}
                        </div>
                        <p className="text-[11px] text-slate-400 mt-0.5">{m.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Advanced Overrides Toggle */}
            <div className="pt-2 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center space-x-2 text-xs font-mono text-slate-400 hover:text-cyan-400"
              >
                <Sliders className="w-3.5 h-3.5" />
                <span>{showAdvanced ? 'Hide Advanced Metrology Overrides' : 'Advanced Metrology Overrides'}</span>
              </button>

              {showAdvanced && (
                <div className="mt-3 bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">
                      Scale Calibration Factor (pixels per unit):
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      placeholder={activeProduct ? String(activeProduct.calibration_factor) : '10.0'}
                      value={customCalib}
                      onChange={(e) => setCustomCalib(e.target.value)}
                      className="w-full px-3 py-1.5 bg-slate-950 border border-slate-700 rounded text-white"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-slate-400 mb-1">Override Length:</label>
                      <input
                        type="number"
                        step="0.1"
                        placeholder="e.g. 100.0"
                        value={customLength}
                        onChange={(e) => setCustomLength(e.target.value)}
                        className="w-full px-3 py-1.5 bg-slate-950 border border-slate-700 rounded text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 mb-1">Override Width:</label>
                      <input
                        type="number"
                        step="0.1"
                        placeholder="e.g. 50.0"
                        value={customWidth}
                        onChange={(e) => setCustomWidth(e.target.value)}
                        className="w-full px-3 py-1.5 bg-slate-950 border border-slate-700 rounded text-white"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">Tolerance Margin (±):</label>
                    <input
                      type="number"
                      step="0.1"
                      placeholder="e.g. 2.0"
                      value={customTol}
                      onChange={(e) => setCustomTol(e.target.value)}
                      className="w-full px-3 py-1.5 bg-slate-950 border border-slate-700 rounded text-white"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Submit Action */}
        <div className="border-t border-slate-800 pt-6 flex items-center justify-end space-x-4">
          <button
            type="submit"
            disabled={isSubmitting || !selectedFile}
            className={`flex items-center space-x-2 px-8 py-3.5 rounded-xl font-bold text-sm tracking-wide font-mono uppercase transition-all shadow-lg ${
              isSubmitting || !selectedFile
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-cyan-500/20 hover:shadow-cyan-500/30'
            }`}
          >
            {isSubmitting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin text-slate-950" />
                <span>INSPECTING SPECIMEN...</span>
              </>
            ) : (
              <>
                <Scan className="w-4 h-4" />
                <span>EXECUTE QUALITY AUDIT</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
