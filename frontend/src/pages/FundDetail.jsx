import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { ArrowLeft, TrendingUp } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FundDetail = ({ user }) => {
  const { fundId } = useParams();
  const navigate = useNavigate();
  const [fundData, setFundData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFundDetail();
  }, [fundId]);

  const fetchFundDetail = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/funds/${fundId}`);
      setFundData(response.data);
    } catch (error) {
      toast.error('Failed to fetch fund details');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-slate-400">Loading fund details...</div>
      </div>
    );
  }

  if (!fundData || !fundData.fund) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center">
        <div className="text-slate-400">Fund not found</div>
      </div>
    );
  }

  const { fund, nav_history, metrics, score } = fundData;

  const chartData = nav_history?.slice().reverse().map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
    nav: item.nav
  })) || [];

  return (
    <div className="min-h-screen bg-slate-950">
      <nav data-testid="fund-detail-nav" className="bg-slate-950/70 backdrop-blur-xl border-b border-white/10">
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

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div data-testid="fund-header" className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-heading font-bold tracking-tight text-white mb-2">
            {fund.name}
          </h1>
          <p className="text-slate-400">{fund.amc} • {fund.category} • Benchmark: {fund.benchmark}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 mb-6">
          <div className="md:col-span-3 bg-slate-900/50 border border-white/5 rounded-xl p-6">
            <div className="text-sm text-slate-500 mb-2">Overall Score</div>
            <div className="text-5xl font-mono font-bold text-blue-600 mb-4">
              {score?.final_score_default ? score.final_score_default.toFixed(1) : 'N/A'}
            </div>
            <div className="text-xs text-slate-500">Out of 100</div>
          </div>

          <div className="md:col-span-9 bg-slate-900/50 border border-white/5 rounded-xl p-6">
            <div className="text-lg font-heading font-semibold text-white mb-4">Bucket Scores</div>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {score?.bucket_scores && Object.entries(score.bucket_scores).map(([key, value]) => (
                <div key={key}>
                  <div className="text-xs text-slate-500 mb-1">{key}</div>
                  <div className="text-2xl font-mono font-semibold text-slate-300">
                    {typeof value === 'number' ? value.toFixed(1) : 'N/A'}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div data-testid="nav-chart" className="bg-slate-900/50 border border-white/5 rounded-xl p-6 mb-6">
          <div className="text-lg font-heading font-semibold text-white mb-4">NAV History (5 Years)</div>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" />
                <XAxis 
                  dataKey="date" 
                  stroke="#94A3B8"
                  style={{ fontSize: '12px' }}
                />
                <YAxis 
                  stroke="#94A3B8"
                  style={{ fontSize: '12px' }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1E293B', 
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    borderRadius: '8px',
                    color: '#F8FAFC'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="nav" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center py-12 text-slate-400">No NAV history available</div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div data-testid="metrics-panel" className="bg-slate-900/50 border border-white/5 rounded-xl p-6">
            <div className="text-lg font-heading font-semibold text-white mb-4">Risk Metrics</div>
            <div className="space-y-3">
              {metrics?.raw && (
                <>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Std Deviation (1Y)</span>
                    <span className="font-mono text-slate-200">
                      {metrics.raw.std_dev_1y ? `${(metrics.raw.std_dev_1y * 100).toFixed(2)}%` : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Max Drawdown</span>
                    <span className="font-mono text-rose-500">
                      {metrics.raw.max_drawdown ? `${(metrics.raw.max_drawdown * 100).toFixed(2)}%` : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Beta</span>
                    <span className="font-mono text-slate-200">
                      {metrics.raw.beta ? metrics.raw.beta.toFixed(2) : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Sharpe Ratio</span>
                    <span className="font-mono text-emerald-500">
                      {metrics.raw.sharpe ? metrics.raw.sharpe.toFixed(2) : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Sortino Ratio</span>
                    <span className="font-mono text-emerald-500">
                      {metrics.raw.sortino ? metrics.raw.sortino.toFixed(2) : 'N/A'}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>

          <div data-testid="returns-panel" className="bg-slate-900/50 border border-white/5 rounded-xl p-6">
            <div className="text-lg font-heading font-semibold text-white mb-4">Returns</div>
            <div className="space-y-3">
              {metrics?.raw && (
                <>
                  <div className="flex justify-between">
                    <span className="text-slate-400">1 Year</span>
                    <span className="font-mono text-slate-200">
                      {metrics.raw.return_1y ? `${(metrics.raw.return_1y * 100).toFixed(2)}%` : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">3 Year</span>
                    <span className="font-mono text-slate-200">
                      {metrics.raw.return_3y ? `${(metrics.raw.return_3y * 100).toFixed(2)}%` : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">5 Year</span>
                    <span className="font-mono text-slate-200">
                      {metrics.raw.return_5y ? `${(metrics.raw.return_5y * 100).toFixed(2)}%` : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Information Ratio</span>
                    <span className="font-mono text-emerald-500">
                      {metrics.raw.information_ratio ? metrics.raw.information_ratio.toFixed(2) : 'N/A'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Treynor Ratio</span>
                    <span className="font-mono text-emerald-500">
                      {metrics.raw.treynor ? metrics.raw.treynor.toFixed(2) : 'N/A'}
                    </span>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FundDetail;
