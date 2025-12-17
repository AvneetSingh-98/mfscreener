import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { ArrowLeft, TrendingUp, Save } from 'lucide-react';
import { Slider } from '@/components/ui/slider';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DEFAULT_WEIGHTS = {
  consistency: 30,
  volatility: 20,
  performance: 15,
  portfolio_quality: 20,
  valuation: 15
};

const Preferences = ({ user }) => {
  const navigate = useNavigate();
  const [weights, setWeights] = useState(DEFAULT_WEIGHTS);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (user?.preferences?.default_weights) {
      setWeights(user.preferences.default_weights);
    }
  }, [user]);

  const handleWeightChange = (key, value) => {
    setWeights(prev => ({
      ...prev,
      [key]: value[0]
    }));
  };

  const totalWeight = Object.values(weights).reduce((sum, val) => sum + val, 0);

  const handleSave = async () => {
    if (totalWeight !== 100) {
      toast.error('Total weights must equal 100');
      return;
    }

    setSaving(true);
    try {
      await axios.put(`${API}/user/preferences`, {
        default_weights: weights,
        saved_weights: [],
        min_history_years: 3
      });
      toast.success('Preferences saved successfully');
    } catch (error) {
      toast.error('Failed to save preferences');
      console.error(error);
    } finally {
      setSaving(false);
    }
  };

  const handleReset = () => {
    setWeights(DEFAULT_WEIGHTS);
    toast.success('Weights reset to defaults');
  };

  return (
    <div className="min-h-screen bg-slate-950">
      <nav data-testid="preferences-nav" className="bg-slate-950/70 backdrop-blur-xl border-b border-white/10">
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
        <div data-testid="preferences-header" className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-heading font-bold tracking-tight text-white mb-2">
            Scoring Preferences
          </h1>
          <p className="text-slate-400">Customize the weight of each scoring bucket to match your investment philosophy</p>
        </div>

        <div className="bg-slate-900/50 border border-white/5 rounded-xl p-6 mb-6">
          <div className="flex justify-between items-center mb-6">
            <div className="text-lg font-heading font-semibold text-white">Total Weight</div>
            <div className={`text-3xl font-mono font-bold ${
              totalWeight === 100 ? 'text-emerald-500' : 'text-rose-500'
            }`}>
              {totalWeight}
            </div>
          </div>

          {totalWeight !== 100 && (
            <div className="bg-rose-500/10 border border-rose-500/30 rounded-lg p-3 mb-6">
              <p className="text-sm text-rose-400">Total weights must equal 100. Currently: {totalWeight}</p>
            </div>
          )}

          <div data-testid="weight-sliders" className="space-y-6">
            {Object.entries(weights).map(([key, value]) => (
              <div key={key}>
                <div className="flex justify-between items-center mb-3">
                  <label className="text-slate-300 font-medium capitalize">
                    {key.replace('_', ' ')}
                  </label>
                  <span className="text-2xl font-mono font-semibold text-blue-600">
                    {value}
                  </span>
                </div>
                <Slider
                  data-testid={`slider-${key}`}
                  value={[value]}
                  onValueChange={(val) => handleWeightChange(key, val)}
                  max={50}
                  min={0}
                  step={1}
                  className="py-2"
                />
              </div>
            ))}
          </div>
        </div>

        <div className="flex gap-4">
          <button
            data-testid="save-btn"
            onClick={handleSave}
            disabled={saving || totalWeight !== 100}
            className="flex-1 bg-blue-600 hover:bg-blue-500 text-white rounded-md px-6 py-3 font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            <Save className="h-5 w-5 mr-2" />
            {saving ? 'Saving...' : 'Save Preferences'}
          </button>
          <button
            data-testid="reset-btn"
            onClick={handleReset}
            className="bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-md px-6 py-3 font-medium transition-all"
          >
            Reset to Defaults
          </button>
        </div>

        <div className="mt-8 bg-slate-900/30 border border-white/5 rounded-xl p-6">
          <h3 className="text-lg font-heading font-semibold text-white mb-4">About Scoring Buckets</h3>
          <div className="space-y-3 text-sm text-slate-400">
            <p><strong className="text-slate-300">Consistency:</strong> Measures rolling returns, hit ratio, Sharpe, Sortino, Information Ratio, and Treynor ratios.</p>
            <p><strong className="text-slate-300">Volatility:</strong> Evaluates standard deviation, max drawdown, beta, and volatility skew.</p>
            <p><strong className="text-slate-300">Performance:</strong> Tracks 1-year, 3-year, and 5-year returns vs category.</p>
            <p><strong className="text-slate-300">Portfolio Quality:</strong> Considers AUM, number of stocks, concentration, turnover ratio, and fund manager stability.</p>
            <p><strong className="text-slate-300">Valuation:</strong> Analyzes P/E and P/B ratios relative to category median.</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Preferences;
