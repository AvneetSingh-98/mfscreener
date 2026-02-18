# Mutual Fund Screener - Frontend Design Document

## 1. Architecture Overview

### 1.1 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Next.js Frontend                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Pages      │  │  Components  │  │    Stores    │      │
│  │  (Routes)    │  │   (UI/UX)    │  │   (State)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                  │                  │              │
│         └──────────────────┴──────────────────┘              │
│                           │                                  │
│                    ┌──────▼──────┐                          │
│                    │  API Client  │                          │
│                    └──────┬──────┘                          │
└───────────────────────────┼─────────────────────────────────┘
                            │ HTTP/REST
                    ┌───────▼────────┐
                    │  FastAPI       │
                    │  Backend       │
                    └───────┬────────┘
                            │
                    ┌───────▼────────┐
                    │   MongoDB      │
                    │  (Read-Only)   │
                    └────────────────┘
```

### 1.2 Technology Stack

**Frontend:**
- **Framework**: Next.js 14+ (App Router, TypeScript)
- **Styling**: TailwindCSS + shadcn/ui components
- **State Management**: Zustand (lightweight, performant)
- **Data Fetching**: TanStack Query (caching, revalidation)
- **Charts**: Chart.js + react-chartjs-2
- **Forms**: React Hook Form + Zod validation
- **Icons**: Lucide React

**Backend:**
- **Framework**: FastAPI (Python 3.10+)
- **Database**: MongoDB (motor async driver)
- **Validation**: Pydantic models
- **CORS**: Enabled for frontend origin

---

## 2. Data Flow & State Management

### 2.1 Data Flow Diagram

```
User Action (Select Category)
        ↓
Frontend State Update (Zustand)
        ↓
API Request (TanStack Query)
        ↓
FastAPI Endpoint
        ↓
MongoDB Query (normalized_*_scores)
        ↓
Response (JSON)
        ↓
TanStack Query Cache
        ↓
Frontend State Update
        ↓
Component Re-render
        ↓
User Sees Ranked Funds
```

### 2.2 State Management Strategy

**Global State (Zustand):**
```typescript
interface AppState {
  // Category & Filters
  selectedCategory: string;
  minHistoryYears: number;
  searchQuery: string;
  
  // Weights
  weights: {
    consistency: number;
    recent_performance: number;
    risk: number;
    valuation: number;
    portfolio_quality: number;
  };
  weightPreset: 'balanced' | 'aggressive' | 'conservative' | 'custom';
  
  // Actions
  setCategory: (category: string) => void;
  setMinHistory: (years: number) => void;
  setSearchQuery: (query: string) => void;
  setWeights: (weights: Partial<Weights>) => void;
  setWeightPreset: (preset: string) => void;
  resetWeights: () => void;
}
```

**Server State (TanStack Query):**
- Cached API responses
- Automatic revalidation
- Loading/error states
- Optimistic updates

---

## 3. Component Architecture

### 3.1 Page Structure

```
app/
├── layout.tsx                 # Root layout (fonts, providers)
├── page.tsx                   # Landing/Home page
├── screener/
│   ├── page.tsx              # Main screener page
│   └── [fundKey]/
│       └── page.tsx          # Fund detail page
└── api/                      # API route handlers (if needed)
```

### 3.2 Component Hierarchy

```
ScreenerPage
├── CategorySelector
├── FilterBar
│   ├── MinHistoryToggle
│   ├── SearchInput
│   └── WeightCustomizer
│       ├── PresetButtons
│       └── WeightSliders
├── FundTable
│   ├── TableHeader (sortable)
│   └── FundRow (clickable)
└── LoadingState / ErrorState

FundDetailPage
├── FundHeader
│   ├── FundName
│   ├── AMC
│   └── Category
├── ScoreBreakdown
│   ├── OverallScoreCard
│   ├── MainScoreCards (5)
│   └── SubScoreAccordion
├── NAVChart
│   ├── ChartControls (date range)
│   └── Chart (fund + benchmark)
├── PortfolioSection
│   ├── PortfolioMetrics (PE, PB, ROE)
│   ├── HoldingsTable (top 10)
│   └── SectorChart (pie/bar)
└── RiskMetricsSection
```

### 3.3 Key Components Design

#### 3.3.1 CategorySelector
```typescript
interface CategorySelectorProps {
  categories: string[];
  selected: string;
  onChange: (category: string) => void;
}

// UI: Horizontal scrollable tabs (mobile) or grid (desktop)
// Behavior: Click to select, updates global state
```

#### 3.3.2 WeightCustomizer
```typescript
interface WeightCustomizerProps {
  weights: Weights;
  preset: string;
  onWeightChange: (key: string, value: number) => void;
  onPresetChange: (preset: string) => void;
}

// Features:
// - 3 preset buttons (Balanced, Aggressive, Conservative)
// - 5 sliders (0-100 range)
// - Real-time sum validation (must = 100)
// - Debounced score recalculation (100ms)
```

#### 3.3.3 FundTable
```typescript
interface FundTableProps {
  funds: Fund[];
  weights: Weights;
  sortBy: string;
  sortOrder: 'asc' | 'desc';
  onSort: (column: string) => void;
  onFundClick: (fundKey: string) => void;
}

// Columns:
// - Rank (computed client-side)
// - Fund Name (with AMC subtitle)
// - Overall Score (computed)
// - Main Scores (5 columns)
// - Benchmark

// Features:
// - Sortable columns
// - Hover effects
// - Click to navigate to detail
// - Responsive (horizontal scroll on mobile)
```

#### 3.3.4 NAVChart
```typescript
interface NAVChartProps {
  fundNav: { date: string; nav: number }[];
  benchmarkNav: { date: string; value: number }[];
  benchmarkName: string;
}

// Chart Type: Line chart (Chart.js)
// Features:
// - Dual Y-axis (fund NAV, benchmark value)
// - Date range selector (1M, 3M, 6M, 1Y, 3Y, 5Y, All)
// - Tooltip showing both values
// - Responsive
// - Dark theme styling
```

#### 3.3.5 ScoreBreakdown
```typescript
interface ScoreBreakdownProps {
  normalizedScores: NormalizedScores;
  weights: Weights;
}

// Layout:
// - Overall Score (large, center)
// - 5 Main Score Cards (grid)
// - Expandable accordion for sub-scores
// - Color-coded (green/yellow/red)
// - Tooltips explaining each metric
```

---

## 4. API Integration Layer

### 4.1 API Client Setup

```typescript
// lib/api-client.ts
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = {
  getScores: async (category: string, minHistory: number) => {
    const res = await fetch(
      `${API_BASE_URL}/api/scores/${category}?min_history_years=${minHistory}`
    );
    if (!res.ok) throw new Error('Failed to fetch scores');
    return res.json();
  },
  
  getFundMaster: async () => {
    const res = await fetch(`${API_BASE_URL}/api/funds/master`);
    if (!res.ok) throw new Error('Failed to fetch fund master');
    return res.json();
  },
  
  getFundDetail: async (fundKey: string) => {
    const res = await fetch(`${API_BASE_URL}/api/funds/${fundKey}/detail`);
    if (!res.ok) throw new Error('Failed to fetch fund detail');
    return res.json();
  },
  
  getNAVHistory: async (fundKey: string, startDate?: string, endDate?: string) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    const res = await fetch(
      `${API_BASE_URL}/api/funds/${fundKey}/nav?${params.toString()}`
    );
    if (!res.ok) throw new Error('Failed to fetch NAV history');
    return res.json();
  },
  
  getDefaultWeights: async () => {
    const res = await fetch(`${API_BASE_URL}/api/weights/defaults`);
    if (!res.ok) throw new Error('Failed to fetch default weights');
    return res.json();
  },
  
  getCategories: async () => {
    const res = await fetch(`${API_BASE_URL}/api/categories`);
    if (!res.ok) throw new Error('Failed to fetch categories');
    return res.json();
  },
};
```

### 4.2 TanStack Query Hooks

```typescript
// hooks/use-scores.ts
export function useScores(category: string, minHistory: number) {
  return useQuery({
    queryKey: ['scores', category, minHistory],
    queryFn: () => apiClient.getScores(category, minHistory),
    staleTime: 5 * 60 * 1000, // 5 minutes
    cacheTime: 10 * 60 * 1000, // 10 minutes
  });
}

// hooks/use-fund-detail.ts
export function useFundDetail(fundKey: string) {
  return useQuery({
    queryKey: ['fund-detail', fundKey],
    queryFn: () => apiClient.getFundDetail(fundKey),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// hooks/use-nav-history.ts
export function useNAVHistory(fundKey: string, dateRange: string) {
  const { startDate, endDate } = getDateRange(dateRange);
  return useQuery({
    queryKey: ['nav-history', fundKey, dateRange],
    queryFn: () => apiClient.getNAVHistory(fundKey, startDate, endDate),
    staleTime: 60 * 60 * 1000, // 1 hour
  });
}
```

---

## 5. Score Calculation Logic

### 5.1 Client-Side Score Computation

```typescript
// lib/score-calculator.ts

interface NormalizedSubScores {
  returns: {
    cagr_1y: number;
    cagr_3y: number;
    cagr_5y: number;
    return_3m: number;
    return_6m: number;
  };
  consistency: {
    rolling_3y: number;
    rolling_5y: number;
    iqr_3y: number;
    iqr_5y: number;
  };
  risk: {
    volatility: number;
    max_drawdown: number;
    beta_3y: number;
  };
  risk_adjusted: {
    sharpe_3y: number;
    sortino_3y: number;
    information_ratio_3y: number;
  };
  portfolio_quality: {
    stock_count_score: number;
    top_10_concentration_score: number;
    sector_hhi_score: number;
    turnover_score: number;
  };
  valuation: {
    portfolio_pe_score: number;
    portfolio_pb_score: number;
    portfolio_roe_score: number;
  };
}

interface Weights {
  consistency: number;
  recent_performance: number;
  risk: number;
  valuation: number;
  portfolio_quality: number;
}

export function calculateOverallScore(
  subScores: NormalizedSubScores,
  weights: Weights
): number {
  // Calculate main category scores (average of sub-scores)
  const consistencyScore = average(Object.values(subScores.consistency));
  const recentPerformanceScore = average(Object.values(subScores.returns));
  const riskScore = average([
    ...Object.values(subScores.risk),
    ...Object.values(subScores.risk_adjusted)
  ]);
  const portfolioQualityScore = average(Object.values(subScores.portfolio_quality));
  const valuationScore = average(Object.values(subScores.valuation));
  
  // Weighted average
  const overallScore = (
    (weights.consistency / 100) * consistencyScore +
    (weights.recent_performance / 100) * recentPerformanceScore +
    (weights.risk / 100) * riskScore +
    (weights.portfolio_quality / 100) * portfolioQualityScore +
    (weights.valuation / 100) * valuationScore
  );
  
  return Math.round(overallScore * 100) / 100; // Round to 2 decimals
}

function average(values: number[]): number {
  const validValues = values.filter(v => v !== null && v !== undefined && !isNaN(v));
  if (validValues.length === 0) return 0;
  return validValues.reduce((sum, v) => sum + v, 0) / validValues.length;
}

export function rankFunds(
  funds: Fund[],
  weights: Weights
): Fund[] {
  // Calculate overall score for each fund
  const fundsWithScores = funds.map(fund => ({
    ...fund,
    overallScore: calculateOverallScore(fund.normalized_sub_scores, weights),
  }));
  
  // Sort by overall score (descending), then by scheme_code (ascending) for ties
  fundsWithScores.sort((a, b) => {
    if (b.overallScore !== a.overallScore) {
      return b.overallScore - a.overallScore;
    }
    return a.scheme_code.localeCompare(b.scheme_code);
  });
  
  // Assign ranks
  return fundsWithScores.map((fund, index) => ({
    ...fund,
    rank: index + 1,
  }));
}
```

### 5.2 Weight Validation

```typescript
// lib/weight-validator.ts

export function validateWeights(weights: Weights): {
  isValid: boolean;
  sum: number;
  error?: string;
} {
  const sum = Object.values(weights).reduce((acc, val) => acc + val, 0);
  
  if (sum !== 100) {
    return {
      isValid: false,
      sum,
      error: `Weights must sum to 100% (current: ${sum}%)`,
    };
  }
  
  // Check individual weight ranges
  for (const [key, value] of Object.entries(weights)) {
    if (value < 0 || value > 100) {
      return {
        isValid: false,
        sum,
        error: `${key} must be between 0 and 100`,
      };
    }
  }
  
  return { isValid: true, sum };
}

export function normalizeWeights(weights: Weights): Weights {
  const sum = Object.values(weights).reduce((acc, val) => acc + val, 0);
  if (sum === 0) return weights;
  
  const normalized: Weights = {} as Weights;
  for (const [key, value] of Object.entries(weights)) {
    normalized[key as keyof Weights] = Math.round((value / sum) * 100);
  }
  
  // Adjust for rounding errors
  const newSum = Object.values(normalized).reduce((acc, val) => acc + val, 0);
  if (newSum !== 100) {
    const diff = 100 - newSum;
    normalized.consistency += diff; // Add/subtract difference to first weight
  }
  
  return normalized;
}
```

---

## 6. UI/UX Design Specifications

### 6.1 Design System (Tailwind Config)

```typescript
// tailwind.config.ts
export default {
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: '#020617', // slate-950
          paper: '#0F172A',   // slate-900
          elevated: '#1E293B', // slate-800
        },
        primary: {
          DEFAULT: '#3B82F6', // blue-500
          hover: '#2563EB',   // blue-600
        },
        accent: {
          gold: '#F59E0B',    // amber-500
          emerald: '#10B981', // emerald-500
          rose: '#F43F5E',    // rose-500
        },
        text: {
          primary: '#F8FAFC',   // slate-50
          secondary: '#94A3B8', // slate-400
          muted: '#64748B',     // slate-500
        },
        score: {
          high: '#10B981',   // green (≥70)
          medium: '#F59E0B', // yellow (40-69)
          low: '#F43F5E',    // red (<40)
          missing: '#64748B', // gray (null)
        },
      },
      fontFamily: {
        heading: ['Manrope', 'sans-serif'],
        body: ['IBM Plex Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
    },
  },
};
```

### 6.2 Component Styling Guidelines

**Cards:**
```css
.card-base {
  @apply bg-slate-900/50 border border-white/5 rounded-xl p-6;
  @apply hover:border-blue-500/30 transition-colors duration-300;
}

.card-interactive {
  @apply card-base cursor-pointer;
  @apply hover:bg-slate-800/50;
}
```

**Buttons:**
```css
.btn-primary {
  @apply bg-blue-600 hover:bg-blue-500 text-white;
  @apply rounded-md px-6 py-2.5 font-medium;
  @apply transition-all shadow-[0_0_15px_rgba(59,130,246,0.3)];
  @apply hover:shadow-[0_0_25px_rgba(59,130,246,0.5)];
}

.btn-secondary {
  @apply bg-slate-800 hover:bg-slate-700 text-slate-200;
  @apply border border-slate-700 rounded-md px-6 py-2.5 font-medium;
  @apply transition-all;
}
```

**Inputs:**
```css
.input-base {
  @apply bg-slate-950 border border-slate-800 rounded-md px-4 py-2;
  @apply text-slate-200 focus:border-blue-500 focus:ring-1 focus:ring-blue-500;
  @apply outline-none transition-all placeholder:text-slate-600;
}
```

### 6.3 Responsive Breakpoints

| Breakpoint | Width | Usage |
|------------|-------|-------|
| `sm` | 640px | Mobile landscape |
| `md` | 768px | Tablet portrait |
| `lg` | 1024px | Tablet landscape / Small desktop |
| `xl` | 1280px | Desktop |
| `2xl` | 1536px | Large desktop |

**Layout Strategy:**
- Mobile: Single column, stacked cards
- Tablet: 2-column grid for score cards
- Desktop: Full table view, multi-column layouts

---

## 7. Performance Optimization

### 7.1 Code Splitting
- Dynamic imports for heavy components (charts)
- Route-based code splitting (Next.js automatic)
- Lazy load fund detail page components

### 7.2 Data Optimization
- TanStack Query caching (5-10 min stale time)
- Client-side filtering/sorting (no API calls)
- Debounced weight slider updates (100ms)
- Memoized score calculations

### 7.3 Rendering Optimization
```typescript
// Use React.memo for expensive components
export const FundRow = React.memo(({ fund, weights }) => {
  // ...
});

// Use useMemo for computed values
const rankedFunds = useMemo(
  () => rankFunds(funds, weights),
  [funds, weights]
);

// Use useCallback for event handlers
const handleWeightChange = useCallback(
  (key: string, value: number) => {
    setWeights({ ...weights, [key]: value });
  },
  [weights]
);
```

---

## 8. Error Handling & Edge Cases

### 8.1 API Error Handling
```typescript
// Error boundary for API failures
if (error) {
  return (
    <ErrorState
      title="Failed to load funds"
      message={error.message}
      retry={() => refetch()}
    />
  );
}
```

### 8.2 Missing Data Handling
```typescript
function formatScore(score: number | null | undefined): string {
  if (score === null || score === undefined || isNaN(score)) {
    return '—'; // Em dash for missing data
  }
  return score.toFixed(2);
}
```

### 8.3 Edge Cases
- **No funds in category**: Show empty state with message
- **All scores null**: Show "Insufficient data" message
- **Weight sum ≠ 100**: Show validation error, disable ranking
- **Network timeout**: Show retry button
- **Invalid fund key**: Redirect to 404 page

---

## 9. Testing Strategy

### 9.1 Unit Tests
- Score calculation functions
- Weight validation logic
- Data formatting utilities

### 9.2 Integration Tests
- API client functions
- TanStack Query hooks
- Component interactions

### 9.3 E2E Tests (Playwright)
- Category selection flow
- Weight customization flow
- Fund detail navigation
- Sorting and filtering

---

## 10. Deployment & Environment

### 10.1 Environment Variables
```env
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=MF Screener
```

### 10.2 Build Configuration
```json
// next.config.js
module.exports = {
  reactStrictMode: true,
  images: {
    domains: ['images.unsplash.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  },
};
```

### 10.3 Deployment Checklist
- [ ] Environment variables configured
- [ ] API CORS enabled for production domain
- [ ] Build succeeds without errors
- [ ] All tests passing
- [ ] Performance metrics acceptable (Lighthouse score > 90)
- [ ] Mobile responsiveness verified
- [ ] Accessibility audit passed

---

## 11. Security Considerations

### 11.1 API Security
- CORS restricted to frontend domain
- Rate limiting on backend
- Input validation on all API endpoints

### 11.2 Frontend Security
- No sensitive data in client-side code
- XSS protection (React default)
- HTTPS only in production
- Content Security Policy headers

---

## 12. Monitoring & Analytics

### 12.1 Performance Monitoring
- Core Web Vitals tracking
- API response time monitoring
- Error rate tracking

### 12.2 User Analytics (Optional)
- Page views
- Category selection frequency
- Weight customization usage
- Fund detail views

---

## 13. Documentation

### 13.1 Code Documentation
- JSDoc comments for all public functions
- README with setup instructions
- API integration guide

### 13.2 User Documentation
- Tooltips for all metrics
- "How it works" page
- FAQ section

---

## 14. Future Enhancements (Post-MVP)

1. **User Authentication**: Login, saved preferences
2. **Watchlist**: Save favorite funds
3. **Comparison Tool**: Side-by-side fund comparison
4. **Export**: PDF/Excel export
5. **Alerts**: Email notifications for score changes
6. **Historical Tracking**: Score evolution over time
7. **Qualitative Overlays**: Fund house quality, manager tenure
8. **Portfolio Overlap**: Identify overlapping holdings
9. **Advanced Filters**: AUM range, expense ratio, etc.
10. **Mobile App**: React Native version

---

## 15. Acceptance Criteria Summary

### 15.1 Functional
- ✅ All 9 categories selectable
- ✅ Funds ranked by overall score
- ✅ Weight customization works (3 presets + manual)
- ✅ Scores recalculate instantly (<100ms)
- ✅ Fund detail page shows all metrics
- ✅ NAV chart displays fund + benchmark
- ✅ Portfolio holdings and sector allocation visible
- ✅ Sorting and filtering work client-side

### 15.2 Non-Functional
- ✅ Page load < 2s
- ✅ Mobile responsive
- ✅ WCAG AA compliant
- ✅ Works on Chrome, Firefox, Safari (last 2 versions)
- ✅ No console errors
- ✅ Lighthouse score > 90

### 15.3 Data Integrity
- ✅ Frontend scores match backend data
- ✅ No re-normalization or re-ranking
- ✅ Missing data displayed as "—"
- ✅ All scores traceable to components
