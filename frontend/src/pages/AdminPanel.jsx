import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { ArrowLeft, TrendingUp, RefreshCw, Upload } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminPanel = ({ user }) => {
  const navigate = useNavigate();
  const [computing, setComputing] = useState(false);
  const [minHistoryYears, setMinHistoryYears] = useState(3);
  const [result, setResult] = useState(null);

  const handleRecompute = async () => {
    setComputing(true);
    setResult(null);
    try {
      const response = await axios.post(`${API}/admin/recompute`, null, {
        params: { min_history_years: minHistoryYears }
      });
      setResult(response.data);
      toast.success('Recompute completed successfully');
    } catch (error) {
      toast.error('Failed to trigger recompute');
      console.error(error);
    } finally {
      setComputing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950">
      <nav data-testid="admin-nav" className="bg-slate-950/70 backdrop-blur-xl border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <button
              data-testid="back-btn"
              onClick={() => navigate('/dashboard')}
              className="flex items-center text-slate-400 hover:text-white transition-colors"
            >
              <ArrowLeft className="h-5 w-5 mr-2" />
              Back to Dashboard
            </button>
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-heading font-bold tracking-tight text-white">FundScreener</span>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div data-testid="admin-header" className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-heading font-bold tracking-tight text-white mb-2">
            Admin Panel
          </h1>
          <p className="text-slate-400">Manage fund data, trigger recomputation, and upload factsheets</p>
        </div>

        <div className="space-y-6">
          <div data-testid="recompute-section" className="bg-slate-900/50 border border-white/5 rounded-xl p-6">
            <div className="flex items-center mb-4">
              <RefreshCw className="h-6 w-6 text-blue-600 mr-2" />
              <h2 className="text-xl font-heading font-semibold text-white">Recompute Metrics & Scores</h2>
            </div>
            <p className="text-slate-400 mb-6">
              Trigger a full recomputation of raw metrics, percentiles, and final scores for all eligible funds.
            </p>

            <div className="mb-4">
              <label className="text-sm text-slate-400 mb-2 block">Minimum History (Years)</label>
              <Select value={minHistoryYears.toString()} onValueChange={(val) => setMinHistoryYears(parseInt(val))}>
                <SelectTrigger data-testid="history-select" className="bg-slate-950 border-slate-800 text-slate-200 w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-800">
                  <SelectItem value="3">3 Years</SelectItem>
                  <SelectItem value="5">5 Years</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <button
              data-testid="recompute-btn"
              onClick={handleRecompute}
              disabled={computing}
              className="bg-blue-600 hover:bg-blue-500 text-white rounded-md px-6 py-3 font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              <RefreshCw className={`h-5 w-5 mr-2 ${computing ? 'animate-spin' : ''}`} />
              {computing ? 'Computing...' : 'Trigger Recompute'}
            </button>

            {result && (
              <div data-testid="recompute-result" className="mt-6 bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-4">
                <p className="text-sm text-emerald-400 mb-2">
                  <strong>Success!</strong> {result.message}
                </p>
                <p className="text-xs text-emerald-400">
                  Computed: {result.computed_funds} / Total Eligible: {result.total_eligible}
                </p>
              </div>
            )}
          </div>

          <div data-testid="upload-section" className="bg-slate-900/50 border border-white/5 rounded-xl p-6">
            <div className="flex items-center mb-4">
              <Upload className="h-6 w-6 text-amber-500 mr-2" />
              <h2 className="text-xl font-heading font-semibold text-white">Upload Factsheet</h2>
            </div>
            <p className="text-slate-400 mb-6">
              Upload monthly factsheets to update portfolio snapshots (Coming soon).
            </p>
            <button
              data-testid="upload-btn"
              disabled
              className="bg-slate-800 text-slate-500 rounded-md px-6 py-3 font-medium cursor-not-allowed"
            >
              Upload Feature Coming Soon
            </button>
          </div>

          <div className="bg-slate-900/30 border border-white/5 rounded-xl p-6">
            <h3 className="text-lg font-heading font-semibold text-white mb-4">About Recompute</h3>
            <div className="space-y-3 text-sm text-slate-400">
              <p><strong className="text-slate-300">Step 1:</strong> Calculates raw metrics (returns, volatility, ratios) for all eligible funds.</p>
              <p><strong className="text-slate-300">Step 2:</strong> Computes percentile rankings within each category.</p>
              <p><strong className="text-slate-300">Step 3:</strong> Generates final scores using default weights and caches results.</p>
              <p className="text-xs text-amber-500 mt-4">
                ⚠️ This operation may take several minutes depending on the number of funds and NAV data points.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
