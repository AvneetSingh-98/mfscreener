# Mutual Fund Screener - Implementation Tasks

## Phase 1: Backend API Development

### 1.1 Setup FastAPI Project Structure
- [ ] 1.1.1 Create API router structure in `backend/api/`
- [ ] 1.1.2 Add Pydantic response models for all endpoints
- [ ] 1.1.3 Configure CORS middleware for frontend origin
- [ ] 1.1.4 Add error handling middleware

### 1.2 Implement Core API Endpoints
- [ ] 1.2.1 `GET /api/scores/{category}` - Fetch normalized scores by category
  - Query normalized_*_scores collections
  - Join with fund_master for scheme details
  - Filter by min_history_years
  - Return structured JSON with sub-scores
- [ ] 1.2.2 `GET /api/funds/master` - Fetch all fund master data
  - Query fund_master collection
  - Return scheme_code, fund_key, scheme_name, amc, category, benchmark
- [ ] 1.2.3 `GET /api/funds/{fund_key}/detail` - Fetch complete fund details
  - Join normalized scores, portfolio_holdings_v2, qual_sector_concentration, qualitative_fund_attributes
  - Include raw metrics from score_* collections
  - Return comprehensive fund profile
- [ ] 1.2.4 `GET /api/funds/{fund_key}/nav` - Fetch NAV history with benchmark
  - Query nav_history for fund
  - Query benchmark_nav for corresponding benchmark
  - Support date range filtering (start_date, end_date)
  - Return aligned time series data
- [ ] 1.2.5 `GET /api/weights/defaults` - Fetch default weight profiles
  - Return hardcoded balanced, aggressive, conservative presets
- [ ] 1.2.6 `GET /api/categories` - Fetch available categories
  - Return list of 9 categories

### 1.3 API Testing & Validation
- [ ] 1.3.1 Test all endpoints with Postman/Thunder Client
- [ ] 1.3.2 Verify response schemas match Pydantic models
- [ ] 1.3.3 Test error cases (invalid fund_key, missing data)
- [ ] 1.3.4 Verify CORS headers in responses

---

## Phase 2: Frontend Project Setup

### 2.1 Initialize Next.js Project
- [ ] 2.1.1 Create Next.js 14+ project in `frontend-next/` with TypeScript
- [ ] 2.1.2 Configure TailwindCSS with custom theme (Midnight Fintech)
- [ ] 2.1.3 Install dependencies:
  - zustand (state management)
  - @tanstack/react-query (data fetching)
  - chart.js + react-chartjs-2 (charts)
  - lucide-react (icons)
  - react-hook-form + zod (forms)
  - date-fns (date utilities)
- [ ] 2.1.4 Setup project structure:
  ```
  app/
  ├── layout.tsx
  ├── page.tsx
  ├── screener/
  │   ├── page.tsx
  │   └── [fundKey]/page.tsx
  components/
  ├── ui/ (shadcn components)
  ├── screener/
  └── fund-detail/
  lib/
  ├── api-client.ts
  ├── score-calculator.ts
  ├── weight-validator.ts
  └── utils.ts
  hooks/
  ├── use-scores.ts
  ├── use-fund-detail.ts
  └── use-nav-history.ts
  stores/
  └── app-store.ts
  types/
  └── index.ts
  ```

### 2.2 Configure Development Environment
- [ ] 2.2.1 Create `.env.local` with API URL
- [ ] 2.2.2 Configure `next.config.js` (CORS, images)
- [ ] 2.2.3 Setup ESLint and Prettier
- [ ] 2.2.4 Add custom fonts (Manrope, IBM Plex Sans, JetBrains Mono)

### 2.3 Setup Tailwind Theme
- [ ] 2.3.1 Configure custom colors (background, primary, accent, text, score)
- [ ] 2.3.2 Configure custom fonts
- [ ] 2.3.3 Add custom utility classes (card-base, btn-primary, input-base)
- [ ] 2.3.4 Test dark theme rendering

---

## Phase 3: Core Infrastructure

### 3.1 API Client Layer
- [ ] 3.1.1 Create `lib/api-client.ts` with all API functions
- [ ] 3.1.2 Add error handling and retry logic
- [ ] 3.1.3 Add TypeScript types for all responses

### 3.2 State Management
- [ ] 3.2.1 Create Zustand store (`stores/app-store.ts`)
  - selectedCategory
  - minHistoryYears
  - searchQuery
  - weights (5 categories)
  - weightPreset
  - Actions (setters, resetWeights)
- [ ] 3.2.2 Add persistence (localStorage) for weights

### 3.3 TanStack Query Setup
- [ ] 3.3.1 Create QueryClient provider in root layout
- [ ] 3.3.2 Create custom hooks:
  - `useScores(category, minHistory)`
  - `useFundMaster()`
  - `useFundDetail(fundKey)`
  - `useNAVHistory(fundKey, dateRange)`
  - `useDefaultWeights()`
  - `useCategories()`
- [ ] 3.3.3 Configure caching and stale time

### 3.4 Score Calculation Logic
- [ ] 3.4.1 Implement `calculateOverallScore(subScores, weights)`
- [ ] 3.4.2 Implement `rankFunds(funds, weights)`
- [ ] 3.4.3 Implement `validateWeights(weights)`
- [ ] 3.4.4 Implement `normalizeWeights(weights)`
- [ ] 3.4.5 Add unit tests for all calculation functions

### 3.5 Utility Functions
- [ ] 3.5.1 Create `formatScore(score)` - handles null/undefined
- [ ] 3.5.2 Create `formatPercentage(value)` - formats as %
- [ ] 3.5.3 Create `formatCurrency(value)` - formats AUM
- [ ] 3.5.4 Create `getScoreColor(score)` - returns color class
- [ ] 3.5.5 Create `getDateRange(range)` - converts range to dates

---

## Phase 4: Screener Page Components

### 4.1 Category Selector
- [ ] 4.1.1 Create `CategorySelector` component
- [ ] 4.1.2 Fetch categories from API
- [ ] 4.1.3 Render as horizontal tabs (mobile) or grid (desktop)
- [ ] 4.1.4 Highlight selected category
- [ ] 4.1.5 Update global state on selection

### 4.2 Filter Bar
- [ ] 4.2.1 Create `FilterBar` component
- [ ] 4.2.2 Add `MinHistoryToggle` (3Y / 5Y buttons)
- [ ] 4.2.3 Add `SearchInput` with icon
- [ ] 4.2.4 Connect to global state
- [ ] 4.2.5 Add responsive layout

### 4.3 Weight Customizer
- [ ] 4.3.1 Create `WeightCustomizer` component
- [ ] 4.3.2 Add 3 preset buttons (Balanced, Aggressive, Conservative)
- [ ] 4.3.3 Create `WeightSlider` component (5 sliders)
- [ ] 4.3.4 Implement real-time sum validation
- [ ] 4.3.5 Add visual feedback (sum indicator, error message)
- [ ] 4.3.6 Debounce weight changes (100ms)
- [ ] 4.3.7 Add "Reset to Default" button

### 4.4 Fund Table
- [ ] 4.4.1 Create `FundTable` component
- [ ] 4.4.2 Create `TableHeader` with sortable columns
- [ ] 4.4.3 Create `FundRow` component
- [ ] 4.4.4 Implement client-side sorting
- [ ] 4.4.5 Implement client-side filtering (search)
- [ ] 4.4.6 Calculate and display ranks
- [ ] 4.4.7 Add hover effects and click navigation
- [ ] 4.4.8 Make responsive (horizontal scroll on mobile)
- [ ] 4.4.9 Add loading skeleton
- [ ] 4.4.10 Add empty state

### 4.5 Screener Page Integration
- [ ] 4.5.1 Create `app/screener/page.tsx`
- [ ] 4.5.2 Integrate all components
- [ ] 4.5.3 Fetch scores data with TanStack Query
- [ ] 4.5.4 Compute overall scores and ranks
- [ ] 4.5.5 Handle loading and error states
- [ ] 4.5.6 Add page metadata (title, description)

---

## Phase 5: Fund Detail Page Components

### 5.1 Fund Header
- [ ] 5.1.1 Create `FundHeader` component
- [ ] 5.1.2 Display fund name, AMC, category
- [ ] 5.1.3 Add back button to screener
- [ ] 5.1.4 Add breadcrumb navigation

### 5.2 Score Breakdown
- [ ] 5.2.1 Create `OverallScoreCard` component (large, center)
- [ ] 5.2.2 Create `MainScoreCard` component (5 cards in grid)
- [ ] 5.2.3 Create `SubScoreAccordion` component (expandable)
- [ ] 5.2.4 Add color coding (green/yellow/red)
- [ ] 5.2.5 Add tooltips for each metric
- [ ] 5.2.6 Display score ranges contextually

### 5.3 NAV Chart
- [ ] 5.3.1 Create `NAVChart` component using Chart.js
- [ ] 5.3.2 Implement dual Y-axis (fund NAV, benchmark value)
- [ ] 5.3.3 Add date range selector (1M, 3M, 6M, 1Y, 3Y, 5Y, All)
- [ ] 5.3.4 Fetch NAV data based on selected range
- [ ] 5.3.5 Add custom tooltip showing both values
- [ ] 5.3.6 Style for dark theme
- [ ] 5.3.7 Make responsive

### 5.4 Portfolio Section
- [ ] 5.4.1 Create `PortfolioMetrics` component (PE, PB, ROE cards)
- [ ] 5.4.2 Create `HoldingsTable` component (top 10 stocks)
- [ ] 5.4.3 Create `SectorChart` component (pie or bar chart)
- [ ] 5.4.4 Display top_10_weight and equity_stock_count
- [ ] 5.4.5 Add coverage percentages for valuation metrics

### 5.5 Risk Metrics Section
- [ ] 5.5.1 Create `RiskMetricsSection` component
- [ ] 5.5.2 Display volatility, max drawdown, beta
- [ ] 5.5.3 Display Sharpe, Sortino, Information Ratio
- [ ] 5.5.4 Add explanatory tooltips

### 5.6 Performance Metrics Section
- [ ] 5.6.1 Create `PerformanceMetrics` component
- [ ] 5.6.2 Display 1Y, 3Y, 5Y CAGR
- [ ] 5.6.3 Display 3M, 6M returns
- [ ] 5.6.4 Add comparison with benchmark (if available)

### 5.7 Fund Detail Page Integration
- [ ] 5.7.1 Create `app/screener/[fundKey]/page.tsx`
- [ ] 5.7.2 Fetch fund detail data with TanStack Query
- [ ] 5.7.3 Integrate all components
- [ ] 5.7.4 Handle loading and error states
- [ ] 5.7.5 Add page metadata (dynamic title, description)

---

## Phase 6: Landing Page

### 6.1 Hero Section
- [ ] 6.1.1 Create hero section with headline and CTA
- [ ] 6.1.2 Add background image (Unsplash)
- [ ] 6.1.3 Add "Get Started" button → /screener

### 6.2 Features Section
- [ ] 6.2.1 Create features grid (3-4 key features)
- [ ] 6.2.2 Add icons and descriptions
- [ ] 6.2.3 Highlight explainability, customization, data-driven

### 6.3 How It Works Section
- [ ] 6.3.1 Create step-by-step explanation
- [ ] 6.3.2 Add visuals/icons for each step

### 6.4 Footer
- [ ] 6.4.1 Create footer with links (About, Contact, Privacy)
- [ ] 6.4.2 Add disclaimer text

---

## Phase 7: UI Polish & Responsiveness

### 7.1 Mobile Optimization
- [ ] 7.1.1 Test all pages on mobile (375px, 414px)
- [ ] 7.1.2 Optimize table for horizontal scroll
- [ ] 7.1.3 Optimize charts for small screens
- [ ] 7.1.4 Test touch interactions (sliders, buttons)

### 7.2 Tablet Optimization
- [ ] 7.2.1 Test all pages on tablet (768px, 1024px)
- [ ] 7.2.2 Adjust grid layouts for tablet
- [ ] 7.2.3 Test landscape and portrait modes

### 7.3 Desktop Optimization
- [ ] 7.3.1 Test all pages on desktop (1280px, 1920px)
- [ ] 7.3.2 Optimize for large screens (max-width constraints)
- [ ] 7.3.3 Test hover states and interactions

### 7.4 Accessibility
- [ ] 7.4.1 Add ARIA labels to all interactive elements
- [ ] 7.4.2 Test keyboard navigation (Tab, Enter, Escape)
- [ ] 7.4.3 Add focus indicators (ring-2 ring-blue-500)
- [ ] 7.4.4 Test with screen reader (NVDA/JAWS)
- [ ] 7.4.5 Verify color contrast (WCAG AA)

### 7.5 Loading States
- [ ] 7.5.1 Add skeleton loaders for tables
- [ ] 7.5.2 Add skeleton loaders for charts
- [ ] 7.5.3 Add skeleton loaders for cards
- [ ] 7.5.4 Add spinner for button actions

### 7.6 Error States
- [ ] 7.6.1 Create `ErrorState` component
- [ ] 7.6.2 Add retry functionality
- [ ] 7.6.3 Add user-friendly error messages
- [ ] 7.6.4 Test all error scenarios

### 7.7 Empty States
- [ ] 7.7.1 Create `EmptyState` component
- [ ] 7.7.2 Add for "No funds found"
- [ ] 7.7.3 Add for "No search results"
- [ ] 7.7.4 Add helpful messages and actions

---

## Phase 8: Testing

### 8.1 Unit Tests
- [ ] 8.1.1 Test `calculateOverallScore` function
- [ ] 8.1.2 Test `rankFunds` function
- [ ] 8.1.3 Test `validateWeights` function
- [ ] 8.1.4 Test `normalizeWeights` function
- [ ] 8.1.5 Test utility functions (formatScore, formatPercentage, etc.)

### 8.2 Integration Tests
- [ ] 8.2.1 Test API client functions
- [ ] 8.2.2 Test TanStack Query hooks
- [ ] 8.2.3 Test Zustand store actions

### 8.3 Component Tests
- [ ] 8.3.1 Test CategorySelector rendering and interaction
- [ ] 8.3.2 Test WeightCustomizer slider changes
- [ ] 8.3.3 Test FundTable sorting and filtering
- [ ] 8.3.4 Test NAVChart rendering

### 8.4 E2E Tests (Playwright)
- [ ] 8.4.1 Test category selection flow
- [ ] 8.4.2 Test weight customization flow
- [ ] 8.4.3 Test fund detail navigation
- [ ] 8.4.4 Test sorting and filtering
- [ ] 8.4.5 Test search functionality

---

## Phase 9: Performance Optimization

### 9.1 Code Optimization
- [ ] 9.1.1 Add React.memo to expensive components
- [ ] 9.1.2 Add useMemo for computed values
- [ ] 9.1.3 Add useCallback for event handlers
- [ ] 9.1.4 Implement code splitting (dynamic imports)

### 9.2 Data Optimization
- [ ] 9.2.1 Optimize TanStack Query cache settings
- [ ] 9.2.2 Implement request deduplication
- [ ] 9.2.3 Add pagination (if needed for >50 funds)

### 9.3 Asset Optimization
- [ ] 9.3.1 Optimize images (Next.js Image component)
- [ ] 9.3.2 Lazy load charts
- [ ] 9.3.3 Minimize bundle size (analyze with webpack-bundle-analyzer)

### 9.4 Performance Audit
- [ ] 9.4.1 Run Lighthouse audit (target score > 90)
- [ ] 9.4.2 Measure Core Web Vitals (LCP, FID, CLS)
- [ ] 9.4.3 Optimize based on audit results

---

## Phase 10: Documentation & Deployment

### 10.1 Code Documentation
- [ ] 10.1.1 Add JSDoc comments to all public functions
- [ ] 10.1.2 Create README.md with setup instructions
- [ ] 10.1.3 Create API integration guide
- [ ] 10.1.4 Document environment variables

### 10.2 User Documentation
- [ ] 10.2.1 Add tooltips to all metrics
- [ ] 10.2.2 Create "How It Works" page
- [ ] 10.2.3 Create FAQ section
- [ ] 10.2.4 Add disclaimer and data sources

### 10.3 Deployment Preparation
- [ ] 10.3.1 Configure production environment variables
- [ ] 10.3.2 Test production build locally
- [ ] 10.3.3 Configure CORS for production domain
- [ ] 10.3.4 Setup error monitoring (Sentry)
- [ ] 10.3.5 Setup analytics (optional)

### 10.4 Deployment
- [ ] 10.4.1 Deploy backend to production
- [ ] 10.4.2 Deploy frontend to Vercel
- [ ] 10.4.3 Verify all endpoints working
- [ ] 10.4.4 Test production site end-to-end
- [ ] 10.4.5 Monitor for errors

---

## Phase 11: Post-Launch

### 11.1 Monitoring
- [ ] 11.1.1 Monitor API response times
- [ ] 11.1.2 Monitor error rates
- [ ] 11.1.3 Monitor Core Web Vitals
- [ ] 11.1.4 Monitor user analytics (if enabled)

### 11.2 Bug Fixes
- [ ] 11.2.1 Triage and fix reported bugs
- [ ] 11.2.2 Address performance issues
- [ ] 11.2.3 Fix accessibility issues

### 11.3 Iteration
- [ ] 11.3.1 Gather user feedback
- [ ] 11.3.2 Prioritize feature requests
- [ ] 11.3.3 Plan next iteration

---

## Estimated Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Backend API | 3-4 days | None |
| Phase 2: Frontend Setup | 1 day | None |
| Phase 3: Core Infrastructure | 2 days | Phase 2 |
| Phase 4: Screener Page | 3-4 days | Phase 1, 3 |
| Phase 5: Fund Detail Page | 3-4 days | Phase 1, 3 |
| Phase 6: Landing Page | 1 day | Phase 2 |
| Phase 7: UI Polish | 2-3 days | Phase 4, 5 |
| Phase 8: Testing | 2-3 days | Phase 4, 5, 7 |
| Phase 9: Performance | 1-2 days | Phase 8 |
| Phase 10: Deployment | 1 day | Phase 9 |
| **Total** | **19-27 days** | |

---

## Priority Levels

- **P0 (Critical)**: Must have for MVP
- **P1 (High)**: Important but can be deferred
- **P2 (Medium)**: Nice to have
- **P3 (Low)**: Future enhancement

All tasks above are **P0** unless marked otherwise.
