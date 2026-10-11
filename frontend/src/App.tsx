import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { NewInspectionPage } from './pages/NewInspectionPage';
import { InspectionResultsPage } from './pages/InspectionResultsPage';
import { ProductRegistrationPage } from './pages/ProductRegistrationPage';
import { InspectionHistoryPage } from './pages/InspectionHistoryPage';
import { ModelStatusPage } from './pages/ModelStatusPage';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [activeInspectionId, setActiveInspectionId] = useState<string | null>(null);
  const [systemStatus, setSystemStatus] = useState<'connected' | 'error' | 'checking'>('checking');

  // Verify backend connectivity
  const checkHealth = async () => {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        setSystemStatus('connected');
      } else {
        setSystemStatus('error');
      }
    } catch {
      setSystemStatus('error');
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 20000);
    return () => clearInterval(interval);
  }, []);

  const handleNavigate = (tab: string, inspectionId?: string) => {
    if (inspectionId) {
      setActiveInspectionId(inspectionId);
      setCurrentTab('results');
    } else {
      setCurrentTab(tab);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleInspectionComplete = (inspectionId: string) => {
    setActiveInspectionId(inspectionId);
    setCurrentTab('results');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 flex flex-col industrial-grid">
      {/* Top Navbar */}
      <Navbar
        currentTab={currentTab}
        onTabChange={(tab) => handleNavigate(tab)}
        systemStatus={systemStatus}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 sm:pt-8">
        {currentTab === 'dashboard' && (
          <DashboardPage onNavigate={handleNavigate} />
        )}

        {currentTab === 'inspect' && (
          <NewInspectionPage
            onInspectionComplete={handleInspectionComplete}
            onNavigateToProducts={() => handleNavigate('products')}
          />
        )}

        {currentTab === 'results' && activeInspectionId && (
          <InspectionResultsPage
            inspectionId={activeInspectionId}
            onBack={() => handleNavigate('dashboard')}
            onInspectAgain={() => handleNavigate('inspect')}
          />
        )}

        {currentTab === 'products' && (
          <ProductRegistrationPage
            onStartInspection={(_productId) => {
              handleNavigate('inspect');
            }}
          />
        )}

        {currentTab === 'history' && (
          <InspectionHistoryPage
            onSelectInspection={(id) => handleNavigate('results', id)}
          />
        )}

        {currentTab === 'model' && (
          <ModelStatusPage />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-6 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 font-mono">
          <div>
            <span className="text-slate-300 font-bold">InspectAI System</span> // Universal AI Manufacturing Quality Metrology
          </div>
          <div className="flex items-center space-x-4">
            <span>FastAPI • PyTorch ResNet18 • OpenCV • SQLite</span>
            <span>Local Offline Architecture</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
