# Mutual Fund Screener - Frontend Requirements

## 1. Project Overview

Build a production-grade, explainable mutual fund screener frontend using Next.js that consumes normalized scoring data from MongoDB and provides dynamic, user-customizable ranking with full transparency.

### Core Principles
- **Data Consumer Only**: Frontend never re-normalizes or re-ranks. Backend data is immutable.
- **Explainability First**: Every score must be traceable to its components.
- **Dynamic Weighting**: Users can adjust category weights; overall score computed client-side.
- **Performance**: SSR for SEO, client-side filtering for speed (max 50 funds per category).

---

## 2. User Stories

### 2.1 Category Selection & Browsing
**As an investor**, I want to:
- Select a fund category (Large Cap, Mid Cap, Small Cap, Flexi Cap, Multi Cap, Value, ELSS, Contra, Focused)
- See up to 50 ranked funds in that category
- Filter by minimum history (3Y or 5Y)
- Search funds by name or AMC
- Sort by any column (Rank, Score, Returns, Risk, etc.)

**Acceptance Criteria:**
- Category selector displays all 9 categories
- Default view shows Large Cap with 3Y minimum history
- Search is instant (client-side)
- Sorting updates rank numbers dynamically
- Loading states for data fetching

### 2.2 Dynamic Weight Customization
**As an investor**, I want to:
- Choose from preset weight profiles (Balanced, Aggressive, Conservative)
- Manually adjust weights using sliders
- See overall scores recalculate instantly
- Ensure weights always sum to 100%
- Save my custom weight profile (future)

**Acceptance Criteria:**
- Three preset buttons: Balanced (default), Aggressive, Conservative
- Five sliders: Consistency, Recent Performance, Risk, Valuation, Portfolio Quality
- Slider changes trigger immediate score recalculation
- Sum validation: if total ≠ 100%, show warning
- Scores update without API calls (client-side computation)

### 2.3 Fund Detail View
**As an investor**, I want to:
- Click a fund to see detailed breakdown
- View score decomposition (how each sub-score contributes)
- See NAV history chart with benchmark overlay
- View portfolio holdings (top stocks, sector allocation)
- See portfolio valuation metrics (PE, PB, ROE)
- Understand risk metrics (volatility, drawdown, beta)

**Acceptance Criteria:**
- Score breakdown shows: Overall → 5 main categories → sub-parameters
- NAV chart displays fund vs benchmark with date range selector
- Portfolio table shows top 10 holdings with weights
- Sector allocation pie/bar chart
- All metrics display with proper formatting (%, decimals)
- Missing data shows as "—" not "0" or "N/A"

### 2.4 Explainability & Transparency
**As an investor**, I want to:
- Understand what each score means
- See the range for each metric (0-100, 25-75, 30-75)
- Know which metrics are percentile-based vs penalty-based
- Access tooltips explaining each parameter

**Acceptance Criteria:**
- Hover tooltips on all metric labels
- Color coding: Green (good), Yellow (neutral), Red (poor)
- Score ranges displayed contextually
- "How is this calculated?" expandable sections

---

## 3. Functional Requirements

### 3.1 API Endpoints (Backend - FastAPI)

#### 3.1.1 Get Normalized Scores by Category
```
GET /api/scores/{category}
Query Params: min_history_years (optional, default=3)
Response: {
  "funds": [
    {
      "scheme_code": "123456",
      "fund_key": "HDFC_LARGE_CAP",
      "category": "Large Cap",
      "normalized_sub_scores": {
        "returns": {
          "cagr_1y": 72.4,
          "cagr_3y": 68.2,
          "cagr_5y": 70.1,
          "return_3m": 65.0,
          "return_6m": 67.5
        },
        "consistency": {
          "rolling_3y": 61.2,
          "rolling_5y": 63.5,
          "iqr_3y": 58.0,
          "iqr_5y": 60.0
        },
        "risk": {
          "volatility": 58.9,
          "max_drawdown": 55.2,
          "beta_3y": 60.1
        },
        "risk_adjusted": {
          "sharpe_3y": 66.1,
          "sortino_3y": 68.3,
          "information_ratio_3y": 64.5
        },
        "portfolio_quality": {
          "stock_count_score": 70.3,
          "top_10_concentration_score": 65.0,
          "sector_hhi_score": 68.0,
          "turnover_score": 72.0
        },
        "valuation": {
          "portfolio_pe_score": 49.5,
          "portfolio_pb_score": 52.0,
          "portfolio_roe_score": 55.0
        }
      },
      "meta": {
        "universe_size": 33,
        "normalized_at": "2026-01-17T10:30:00Z"
      }
    }
  ],
  "total": 33
}
```

#### 3.1.2 Get Fund Master Data
```
GET /api/funds/master
Response: {
  "funds": [
    {
      "scheme_code": "123456",
      "fund_key": "HDFC_LARGE_CAP",
      "scheme_name": "HDFC Large Cap Fund - Growth",
      "amc": "HDFC Mutual Fund",
      "category": "Large Cap",
      "asset_class": "Equity",
      "benchmark": "NIFTY 100"
    }
  ]
}
```

#### 3.1.3 Get Fund Detail
```
GET /api/funds/{fund_key}/detail
Response: {
  "fund_info": { /* from fund_master */ },
  "normalized_scores": { /* from normalized_*_scores */ },
  "raw_metrics": { /* from score_* collections */ },
  "portfolio": {
    "holdings": [
      {
        "isin": "INE040A01034",
        "company": "HDFC Bank Limited",
        "sector": "Banks",
        "weight": 9.08
      }
    ],
    "top_10_weight": 43.78,
    "equity_stock_count": 71,
    "portfolio_valuation": {
      "portfolio_pe": 27.79,
      "portfolio_pb": 4.02,
      "portfolio_roe": 17.58,
      "pe_coverage_pct": 97.84,
      "pb_coverage_pct": 97.96,
      "roe_coverage_pct": 95.47
    }
  },
  "sector_concentration": {
    "sector_weights": {
      "banks": 26.38,
      "it": 8.84,
      "petroleum_products": 8.15,
      /* ... */
    },
    "top_sector_pct": 26.38,
    "top_3_sector_pct": 43.37
  },
  "qualitative_attributes": {
    "fund_manager": ["Manager Name"],
    "monthly_avg_aum_cr": 54667.03,
    "portfolio_turnover": 0.31,
    "ter_direct_pct": 0.67
  }
}
```

#### 3.1.4 Get NAV History
```
GET /api/funds/{fund_key}/nav
Query Params: start_date, end_date (optional)
Response: {
  "fund_nav": [
    { "date": "2025-01-01", "nav": 123.45 },
    { "date": "2025-01-02", "nav": 124.12 }
  ],
  "benchmark_nav": [
    { "date": "2025-01-01", "value": 18500.00 },
    { "date": "2025-01-02", "value": 18650.00 }
  ],
  "benchmark_name": "NIFTY 100"
}
```

#### 3.1.5 Get Default Weights
```
GET /api/weights/defaults
Response: {
  "balanced": {
    "consistency": 25,
    "recent_performance": 20,
    "risk": 20,
    "valuation": 15,
    "portfolio_quality": 20
  },
  "aggressive": {
    "consistency": 15,
    "recent_performance": 35,
    "risk": 10,
    "valuation": 15,
    "portfolio_quality": 25
  },
  "conservative": {
    "consistency": 35,
    "recent_performance": 10,
    "risk": 25,
    "valuation": 20,
    "portfolio_quality": 10
  }
}
```

#### 3.1.6 Get Categories List
```
GET /api/categories
Response: {
  "categories": [
    "Large Cap",
    "Mid Cap",
    "Small Cap",
    "Flexi Cap",
    "Multi Cap",
    "Value",
    "ELSS",
    "Contra",
    "Focused"
  ]
}
```

### 3.2 Frontend Score Calculation Logic

**Overall Score Formula:**
```javascript
overallScore = (
  (consistency_weight / 100) * avg(consistency_sub_scores) +
  (recent_performance_weight / 100) * avg(recent_performance_sub_scores) +
  (risk_weight / 100) * avg(risk_sub_scores) +
  (risk_adjusted_weight / 100) * avg(risk_adjusted_sub_scores) +
  (portfolio_quality_weight / 100) * avg(portfolio_quality_sub_scores) +
  (valuation_weight / 100) * avg(valuation_sub_scores)
)
```

**Rules:**
- All sub-scores are pre-normalized (0-100, 25-75, or 30-75)
- Frontend only computes weighted averages
- Rank = sort by overallScore descending
- Ties: use scheme_code alphabetically

### 3.3 Data Display Rules

| Metric Type | Range | Display Format | Missing Data |
|-------------|-------|----------------|--------------|
| Percentile-based | 0-100 | `72.4` | `—` |
| Banded (AUM, stock count) | 25-75 | `65.0` | `—` |
| Penalty (Top-10, sector) | 30-75 | `58.5` | `—` |
| Returns | Any | `12.17%` | `—` |
| Ratios (Sharpe, Beta) | Any | `1.06` | `—` |
| Percentages (Volatility) | Any | `15.07%` | `—` |

**Color Coding:**
- **Green**: Score ≥ 70
- **Yellow**: Score 40-69
- **Red**: Score < 40
- **Gray**: Missing data

---

## 4. Non-Functional Requirements

### 4.1 Performance
- Initial page load: < 2s
- Score recalculation on weight change: < 100ms
- Client-side filtering/sorting: < 50ms
- Chart rendering: < 500ms

### 4.2 Responsiveness
- Mobile-first design
- Breakpoints: 640px (sm), 768px (md), 1024px (lg), 1280px (xl)
- Touch-friendly sliders and buttons

### 4.3 Accessibility
- WCAG AA compliance
- Keyboard navigation
- Screen reader support
- Focus indicators

### 4.4 Browser Support
- Chrome/Edge (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)

---

## 5. Out of Scope (Future Enhancements)

- User authentication (login/signup)
- Watchlist functionality
- Portfolio overlap comparison
- Fund comparison (side-by-side)
- Export to PDF/Excel
- Email alerts
- Historical score tracking
- Qualitative overlays (fund house quality, manager tenure)

---

## 6. Technical Constraints

### 6.1 Backend
- FastAPI (Python 3.10+)
- MongoDB (existing collections, read-only)
- No backend logic changes
- CORS enabled for frontend

### 6.2 Frontend
- Next.js 14+ (App Router)
- TypeScript
- TailwindCSS
- Chart.js for visualizations
- State management: Zustand or Context API
- Data fetching: Native fetch with SWR or TanStack Query

### 6.3 Deployment
- Frontend: Vercel or similar
- Backend: Existing infrastructure (no changes)

---

## 7. Success Metrics

- User can rank funds in < 5 clicks
- Weight customization feels instant (< 100ms)
- All scores are explainable (tooltips, breakdowns)
- Zero data inconsistencies (frontend matches backend)
- Mobile usable (50%+ traffic expected)

---

## 8. Glossary

- **Normalized Score**: 0-100 scale, category-relative percentile
- **Sub-Score**: Component metric (e.g., 1Y CAGR, Sharpe Ratio)
- **Main Score**: Weighted average of sub-scores (e.g., Consistency, Risk)
- **Overall Score**: Weighted average of main scores
- **Fund Key**: Unique identifier (e.g., `HDFC_LARGE_CAP`)
- **Scheme Code**: AMFI scheme code (e.g., `119551`)
