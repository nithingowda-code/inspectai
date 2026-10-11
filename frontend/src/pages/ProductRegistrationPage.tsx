import React, { useState, useEffect, useRef } from 'react';
import { 
  Layers, 
  Plus, 
  Trash2, 
  Edit3, 
  Check, 
  AlertCircle, 
  Scan, 
  X 
} from 'lucide-react';
import type { Product } from '../types';
import { 
  fetchProducts, 
  createProduct, 
  updateProduct, 
  deleteProduct, 
  uploadReferenceImage, 
  deleteReferenceImage,
  getImageUrl 
} from '../services/api';

interface ProductRegistrationPageProps {
  onStartInspection: (productId: string) => void;
}

export const ProductRegistrationPage: React.FC<ProductRegistrationPageProps> = ({
  onStartInspection
}) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Modal / Form state
  const [showModal, setShowModal] = useState<boolean>(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  // Form inputs
  const [name, setName] = useState<string>('');
  const [category, setCategory] = useState<string>('Aerospace');
  const [customCategory, setCustomCategory] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [expectedLength, setExpectedLength] = useState<string>('100.0');
  const [expectedWidth, setExpectedWidth] = useState<string>('50.0');
  const [expectedThickness, setExpectedThickness] = useState<string>('');
  const [unit, setUnit] = useState<string>('mm');
  const [posTol, setPosTol] = useState<string>('2.0');
  const [negTol, setNegTol] = useState<string>('2.0');
  const [calibFactor, setCalibFactor] = useState<string>('10.0');

  // Reference Upload state for active product
  const [uploadingForProductId, setUploadingForProductId] = useState<string | null>(null);
  const refFileInputRef = useRef<HTMLInputElement>(null);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await fetchProducts();
      setProducts(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const openCreateModal = () => {
    setEditingProduct(null);
    setName('');
    setCategory('Aerospace');
    setCustomCategory('');
    setDescription('');
    setExpectedLength('100.0');
    setExpectedWidth('50.0');
    setExpectedThickness('');
    setUnit('mm');
    setPosTol('2.0');
    setNegTol('2.0');
    setCalibFactor('10.0');
    setShowModal(true);
  };

  const openEditModal = (p: Product) => {
    setEditingProduct(p);
    setName(p.name);
    setCategory(p.category);
    setDescription(p.description || '');
    setExpectedLength(String(p.expected_length));
    setExpectedWidth(String(p.expected_width));
    setExpectedThickness(p.expected_thickness ? String(p.expected_thickness) : '');
    setUnit(p.unit);
    setPosTol(String(p.pos_tolerance));
    setNegTol(String(p.neg_tolerance));
    setCalibFactor(String(p.calibration_factor));
    setShowModal(true);
  };

  const handleSaveProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const targetCategory = category === 'Custom' ? customCategory.trim() : category;
    if (!name.trim() || !targetCategory) {
      setError('Product name and category are required.');
      return;
    }

    try {
      const payload = {
        name: name.trim(),
        category: targetCategory,
        description: description.trim() || undefined,
        expected_length: parseFloat(expectedLength) || 100.0,
        expected_width: parseFloat(expectedWidth) || 50.0,
        expected_thickness: expectedThickness ? parseFloat(expectedThickness) : undefined,
        unit,
        pos_tolerance: parseFloat(posTol) || 2.0,
        neg_tolerance: parseFloat(negTol) || 2.0,
        calibration_factor: parseFloat(calibFactor) || 10.0,
      };

      if (editingProduct) {
        await updateProduct(editingProduct.id, payload);
        setSuccessMsg(`Product "${name}" updated successfully.`);
      } else {
        await createProduct(payload);
        setSuccessMsg(`New product "${name}" registered successfully.`);
      }

      setShowModal(false);
      await loadProducts();
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: any) {
      setError(err.message || 'Failed to save product specification.');
    }
  };

  const handleDeleteProduct = async (productId: string, productName: string) => {
    if (!window.confirm(`Are you sure you want to delete product "${productName}" and its reference banks?`)) {
      return;
    }
    try {
      await deleteProduct(productId);
      setSuccessMsg(`Product "${productName}" deleted.`);
      await loadProducts();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to delete product.');
    }
  };

  const handleTriggerRefUpload = (productId: string) => {
    setUploadingForProductId(productId);
    refFileInputRef.current?.click();
  };

  const handleRefFileSelected = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0 || !uploadingForProductId) return;
    const file = e.target.files[0];
    try {
      await uploadReferenceImage(uploadingForProductId, file);
      setSuccessMsg(`Uploaded golden reference "${file.name}". Embedding bank updated.`);
      await loadProducts();
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: any) {
      setError(err.message || 'Failed to upload reference image');
    } finally {
      setUploadingForProductId(null);
      if (refFileInputRef.current) refFileInputRef.current.value = '';
    }
  };

  const handleDeleteRef = async (productId: string, refId: string) => {
    if (!window.confirm('Delete this reference image and update feature bank?')) return;
    try {
      await deleteReferenceImage(productId, refId);
      await loadProducts();
    } catch (err: any) {
      setError(err.message || 'Failed to delete reference');
    }
  };

  const standardCategories = ['Aerospace', 'Electronics', 'Mechanical', 'Metal', 'Plastic', 'Textile', 'Custom'];

  return (
    <div className="space-y-8 pb-16">
      <input
        ref={refFileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleRefFileSelected}
      />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white font-mono flex items-center space-x-2">
            <Layers className="w-6 h-6 text-cyan-400" />
            <span>PRODUCT REGISTRATION & REFERENCE BANKS</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Register new manufactured components, establish expected dimensions and tolerances, and upload golden reference baselines.
          </p>
        </div>
        <button
          onClick={openCreateModal}
          className="flex items-center space-x-2 px-4 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-lg text-sm transition-all shadow-lg shadow-cyan-500/20 self-start md:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Register New Product</span>
        </button>
      </div>

      {successMsg && (
        <div className="bg-emerald-950/40 border border-emerald-800/80 rounded-xl p-3.5 flex items-center space-x-2 text-emerald-300 text-xs">
          <Check className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}
      {error && (
        <div className="bg-rose-950/40 border border-rose-800/80 rounded-xl p-3.5 flex items-center space-x-2 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((p) => (
          <div
            key={p.id}
            className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 flex flex-col justify-between hover:border-slate-700 transition-all space-y-4 shadow-sm"
          >
            <div>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="font-bold text-white text-base leading-snug">{p.name}</h3>
                  <span className="inline-block mt-1 text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                    {p.category}
                  </span>
                </div>
                <div className="flex items-center space-x-1 shrink-0">
                  <button
                    onClick={() => openEditModal(p)}
                    className="p-1.5 text-slate-400 hover:text-white rounded hover:bg-slate-800"
                    title="Edit Specification"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleDeleteProduct(p.id, p.name)}
                    className="p-1.5 text-slate-400 hover:text-rose-400 rounded hover:bg-slate-800"
                    title="Delete Product"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {p.description && (
                <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
                  {p.description}
                </p>
              )}

              <div className="mt-4 bg-slate-950/80 rounded-lg p-3 border border-slate-800/80 space-y-2 text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400 font-mono">Expected Length:</span>
                  <span className="font-mono font-semibold text-white">{p.expected_length} {p.unit}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400 font-mono">Expected Width:</span>
                  <span className="font-mono font-semibold text-white">{p.expected_width} {p.unit}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400 font-mono">Permitted Tolerance:</span>
                  <span className="font-mono text-emerald-400">-{p.neg_tolerance} / +{p.pos_tolerance} {p.unit}</span>
                </div>
                <div className="flex justify-between items-center pt-1 border-t border-slate-800">
                  <span className="text-slate-500 font-mono">Scale Factor:</span>
                  <span className="font-mono text-slate-300">{p.calibration_factor} px/{p.unit}</span>
                </div>
              </div>

              <div className="mt-4 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-400">Golden Reference Samples ({p.references.length})</span>
                  <button
                    onClick={() => handleTriggerRefUpload(p.id)}
                    className="text-cyan-400 hover:text-cyan-300 flex items-center space-x-1"
                  >
                    <Plus className="w-3 h-3" />
                    <span>Add Ref</span>
                  </button>
                </div>

                {p.references.length > 0 ? (
                  <div className="grid grid-cols-4 gap-2">
                    {p.references.map((r) => (
                      <div key={r.id} className="relative group rounded border border-slate-800 overflow-hidden bg-black/40 h-16">
                        <img
                          src={getImageUrl(r.file_path)}
                          alt={r.filename}
                          className="w-full h-full object-cover"
                        />
                        <button
                          onClick={() => handleDeleteRef(p.id, r.id)}
                          className="absolute inset-0 bg-black/70 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-rose-400"
                          title="Remove reference"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-3 border border-dashed border-slate-800 rounded text-slate-500 text-[11px]">
                    No golden reference images uploaded.
                  </div>
                )}
              </div>
            </div>

            <button
              onClick={() => onStartInspection(p.id)}
              className="w-full mt-2 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-cyan-500/50 text-cyan-400 hover:text-white rounded-lg text-xs font-mono font-semibold flex items-center justify-center space-x-2 transition-colors"
            >
              <Scan className="w-3.5 h-3.5" />
              <span>Inspect Specimen For This Profile</span>
            </button>
          </div>
        ))}
      </div>

      {products.length === 0 && !loading && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center space-y-3 max-w-lg mx-auto">
          <Layers className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">No Registered Products Found</h3>
          <p className="text-xs text-slate-400">
            Define target product dimensions, measurement tolerances, and reference samples to begin automated verification.
          </p>
          <button
            onClick={openCreateModal}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-medium"
          >
            Register First Product
          </button>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-xl w-full p-6 space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white font-mono flex items-center space-x-2">
                <Layers className="w-5 h-5 text-cyan-400" />
                <span>{editingProduct ? 'EDIT PRODUCT PROFILE' : 'REGISTER NEW PRODUCT'}</span>
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveProduct} className="space-y-4">
              <div>
                <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                  Product Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Precision Titanium Bracket M4"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                    Category *
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
                  >
                    {standardCategories.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                    Measurement Unit
                  </label>
                  <select
                    value={unit}
                    onChange={(e) => setUnit(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
                  >
                    <option value="mm">Millimeters (mm)</option>
                    <option value="cm">Centimeters (cm)</option>
                    <option value="in">Inches (in)</option>
                  </select>
                </div>
              </div>

              {category === 'Custom' && (
                <div>
                  <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                    Custom Category Name *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Automotive Hydraulics"
                    value={customCategory}
                    onChange={(e) => setCustomCategory(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                  Description / Component Notes
                </label>
                <textarea
                  rows={2}
                  placeholder="Engine mount component specs, critical surfaces..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                    Expected Length ({unit}) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={expectedLength}
                    onChange={(e) => setExpectedLength(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                    Expected Width ({unit}) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={expectedWidth}
                    onChange={(e) => setExpectedWidth(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                    Positive Tolerance (+{unit}) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={posTol}
                    onChange={(e) => setPosTol(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                    Negative Tolerance (-{unit}) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={negTol}
                    onChange={(e) => setNegTol(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                  Optical Calibration Factor (pixels/{unit}) *
                </label>
                <input
                  type="number"
                  step="0.1"
                  required
                  value={calibFactor}
                  onChange={(e) => setCalibFactor(e.target.value)}
                  className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white font-mono"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  Calculated from camera distance and optics (e.g. 5.0 px/mm means 500 pixels = 100mm).
                </p>
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-lg text-xs font-mono uppercase"
                >
                  {editingProduct ? 'Update Specification' : 'Register Specification'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
