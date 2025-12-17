import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'sonner';
import { TrendingUp, Filter, LogOut, Settings, Shield, Search } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = ({ user }) => {
  const navigate = useNavigate();
  const [funds, setFunds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('all');
  const [minHistoryYears, setMinHistoryYears] = useState(3);
  const [categories, setCategories] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    fetchCategories();
    fetchFunds();
  }, [category, minHistoryYears]);

  const fetchCategories = async () => {
    try {
      const response = await axios.get(`${API}/categories`);
      setCategories(response.data.categories);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchFunds = async () => {
    setLoading(true);
    try {
      const params = {
        min_history_years: minHistoryYears,
        limit: 100
      };
      if (category !== 'all') {
        params.category = category;
      }

      const response = await axios.get(`${API}/funds`, { params });
      setFunds(response.data.funds);
    } catch (error) {
      toast.error('Failed to fetch funds');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await axios.post(`${API}/auth/logout`);
      navigate('/login');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const filteredFunds = funds.filter(fund => 
    fund.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    fund.amc.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-950">
      <nav data-testid="dashboard-nav" className="bg-slate-950/70 backdrop-blur-xl border-b border-white/10 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <TrendingUp className="h-8 w-8 text-blue-600" />
              <span className="ml-2 text-xl font-heading font-bold tracking-tight text-white">FundScreener</span>
            </div>
            <div className="flex items-center gap-4">
              <button
                data-testid="preferences-btn"
                onClick={() => navigate('/preferences')}
                className="text-slate-400 hover:text-white transition-colors"
                title="Preferences"
              >
                <Settings className="h-5 w-5" />
              </button>
              <button
                data-testid="admin-btn"
                onClick={() => navigate('/admin')}
                className="text-slate-400 hover:text-white transition-colors"
                title="Admin Panel"
              >
                <Shield className="h-5 w-5" />
              </button>
              <button
                data-testid="logout-btn"
                onClick={handleLogout}
                className="text-slate-400 hover:text-white transition-colors"
                title="Logout"
              >
                <LogOut className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-heading font-bold tracking-tight text-white mb-2">
            Fund Explorer
          </h1>
          <p className="text-slate-400">Welcome back, {user?.name}</p>
        </div>

        <div data-testid="fund-filters" className="bg-slate-900/50 border border-white/5 rounded-xl p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
            <div className="md:col-span-5">
              <label className="text-sm text-slate-400 mb-2 block">Search Funds</label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-500" />
                <Input
                  data-testid="search-input"
                  type="text"
                  placeholder="Search by name or AMC..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10 bg-slate-950 border-slate-800 text-slate-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="md:col-span-3">
              <label className="text-sm text-slate-400 mb-2 block">Category</label>
              <Select value={category} onValueChange={setCategory}>
                <SelectTrigger data-testid="category-filter" className="bg-slate-950 border-slate-800 text-slate-200">
                  <SelectValue placeholder="All Categories" />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-800 z-50">
                  <SelectItem value="all">All Categories</SelectItem>
                  {categories.map(cat => (
                    <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="md:col-span-2">
              <label className="text-sm text-slate-400 mb-2 block">Track Record</label>
              <Select value={minHistoryYears.toString()} onValueChange={(val) => setMinHistoryYears(parseInt(val))}>
                <SelectTrigger data-testid="history-filter" className="bg-slate-950 border-slate-800 text-slate-200">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-slate-900 border-slate-800 z-50">
                  <SelectItem value="3">3+ Years</SelectItem>
                  <SelectItem value="5">5+ Years</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="md:col-span-2 flex items-end">
              <button
                data-testid="apply-filters-btn"
                onClick={fetchFunds}
                className="w-full bg-blue-600 hover:bg-blue-500 text-white rounded-md px-4 py-2 font-medium transition-all"
              >
                Apply
              </button>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="text-slate-400">Loading funds...</div>
          </div>
        ) : (
          <div data-testid="funds-list" className="space-y-4">
            {filteredFunds.length === 0 ? (
              <div className="text-center py-12 text-slate-400">
                No funds found matching your criteria
              </div>
            ) : (
              filteredFunds.map(fund => (
                <div
                  key={fund.fund_id}
                  data-testid={`fund-card-${fund.fund_id}`}
                  onClick={() => navigate(`/funds/${fund.fund_id}`)}
                  className="bg-slate-900/50 border border-white/5 rounded-xl p-6 hover:bg-slate-800/50 hover:border-blue-500/30 transition-all cursor-pointer"
                >
                  <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
                    <div className="md:col-span-5">
                      <h3 className="text-lg font-heading font-semibold text-white mb-1">{fund.name}</h3>
                      <p className="text-sm text-slate-400">{fund.amc} • {fund.category}</p>
                    </div>

                    <div className="md:col-span-2">
                      <div className="text-sm text-slate-500 mb-1">Overall Score</div>
                      <div className="text-2xl font-mono font-semibold text-blue-600">
                        {fund.score ? fund.score.toFixed(1) : 'N/A'}
                      </div>
                    </div>

                    <div className="md:col-span-5">
                      <div className="grid grid-cols-3 gap-2 text-sm">
                        <div>
                          <div className="text-slate-500 text-xs mb-1">Consistency</div>
                          <div className="font-mono text-slate-300">
                            {fund.bucket_scores?.Consistency ? fund.bucket_scores.Consistency.toFixed(1) : '-'}
                          </div>
                        </div>
                        <div>
                          <div className="text-slate-500 text-xs mb-1">Performance</div>
                          <div className="font-mono text-slate-300">
                            {fund.bucket_scores?.Performance ? fund.bucket_scores.Performance.toFixed(1) : '-'}
                          </div>
                        </div>
                        <div>
                          <div className="text-slate-500 text-xs mb-1">Volatility</div>
                          <div className="font-mono text-slate-300">
                            {fund.bucket_scores?.Volatility ? fund.bucket_scores.Volatility.toFixed(1) : '-'}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
