import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, TrendingUp, Filter, Sliders, BarChart3 } from 'lucide-react';

const LandingPage = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-slate-950">
      <div 
        className="relative min-h-screen bg-cover bg-center"
        style={{
          backgroundImage: 'linear-gradient(to bottom, rgba(2, 6, 23, 0.9), rgba(2, 6, 23, 0.95)), url(https://images.unsplash.com/photo-1763854021223-098e818cd783?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NDQ2NDN8MHwxfHNlYXJjaHwyfHxtb2Rlcm4lMjBmaW5hbmNpYWwlMjBkaXN0cmljdCUyMHNreWxpbmUlMjBibHVlJTIwaG91cnxlbnwwfHx8fDE3NjU1MjMzNjB8MA&ixlib=rb-4.1.0&q=85)'
        }}
      >
        <nav data-testid="landing-nav" className="bg-slate-950/70 backdrop-blur-xl border-b border-white/10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center">
                <TrendingUp className="h-8 w-8 text-blue-600" />
                <span className="ml-2 text-xl font-heading font-bold tracking-tight text-white">FundScreener</span>
              </div>
              <button
                data-testid="get-started-btn"
                onClick={() => navigate('/login')}
                className="bg-blue-600 hover:bg-blue-500 text-white rounded-md px-6 py-2.5 font-medium transition-all shadow-[0_0_15px_rgba(59,130,246,0.3)] hover:shadow-[0_0_25px_rgba(59,130,246,0.5)]"
              >
                Get Started
              </button>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-heading font-bold tracking-tight text-white mb-6">
              Data-Driven Mutual Fund
              <br />
              <span className="text-blue-600">Screening & Analysis</span>
            </h1>
            <p className="text-base sm:text-lg text-slate-400 max-w-3xl mx-auto mb-8">
              100-point scoring model across 5 key metrics. Customize weights, compare funds, and make informed investment decisions.
            </p>
            <button
              data-testid="hero-cta-btn"
              onClick={() => navigate('/login')}
              className="inline-flex items-center bg-blue-600 hover:bg-blue-500 text-white rounded-md px-8 py-3 font-medium text-lg transition-all shadow-[0_0_20px_rgba(59,130,246,0.4)] hover:shadow-[0_0_30px_rgba(59,130,246,0.6)]"
            >
              Start Screening
              <ArrowRight className="ml-2 h-5 w-5" />
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <h2 className="text-3xl sm:text-4xl font-heading font-bold tracking-tight text-white text-center mb-16">
          Key Features
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8">
          <div className="md:col-span-4 bg-slate-900/50 border border-white/5 rounded-xl p-6 hover:border-blue-500/30 transition-colors duration-300">
            <div className="bg-blue-600/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <BarChart3 className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="text-xl font-heading font-semibold text-white mb-3">100-Point Scoring</h3>
            <p className="text-slate-400">
              Comprehensive evaluation across Consistency, Volatility, Performance, Portfolio Quality, and Valuation.
            </p>
          </div>

          <div className="md:col-span-4 bg-slate-900/50 border border-white/5 rounded-xl p-6 hover:border-blue-500/30 transition-colors duration-300">
            <div className="bg-emerald-500/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <Sliders className="h-6 w-6 text-emerald-500" />
            </div>
            <h3 className="text-xl font-heading font-semibold text-white mb-3">Custom Weights</h3>
            <p className="text-slate-400">
              Adjust scoring weights to match your investment philosophy and save custom profiles.
            </p>
          </div>

          <div className="md:col-span-4 bg-slate-900/50 border border-white/5 rounded-xl p-6 hover:border-blue-500/30 transition-colors duration-300">
            <div className="bg-amber-500/10 w-12 h-12 rounded-lg flex items-center justify-center mb-4">
              <Filter className="h-6 w-6 text-amber-500" />
            </div>
            <h3 className="text-xl font-heading font-semibold text-white mb-3">Advanced Filters</h3>
            <p className="text-slate-400">
              Filter by category, track record (3yr/5yr), and sort by custom scores in real-time.
            </p>
          </div>
        </div>
      </div>

      <footer className="bg-slate-900/50 border-t border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-slate-400 text-sm">
            <p>© 2025 FundScreener. Built with data-driven insights.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
