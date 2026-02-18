# Design Document: Fintech Premium UI Redesign

## Overview

This design document outlines the comprehensive approach to transforming the mutual fund screener into a premium fintech product through visual redesign. The application currently has functional responsive layouts but lacks the visual polish and professional appearance expected of premium fintech products. This redesign focuses on implementing a cohesive dark theme, enhancing visual hierarchy, improving contrast and readability, and creating a polished, modern interface that matches industry leaders like Groww, Zerodha, and INDmoney.

The redesign addresses:
1. Premium dark theme with proper color palette (#0B1220 page, #111827 cards)
2. High contrast text for readability (#E5E7EB primary, #9CA3AF secondary)
3. Professional typography system (Inter for body, Manrope for headings)
4. Enhanced card design with depth and shadows
5. Chart visual improvements with dark backgrounds
6. Consistent spacing and layout system
7. Polished interactive elements with smooth transitions
8. Mobile and desktop optimizations

## Architecture

### Design System Structure

The design system is organized into layers:

```
Design System
├── Foundation Layer
│   ├── Color Tokens
│   ├── Typography Tokens
│   ├── Spacing Tokens
│   └── Shadow Tokens
├── Component Layer
│   ├── Card Components
│   ├── Button Components
│   ├── Input Components
│   ├── Navigation Components
│   └── Chart Components
└── Page Layer
    ├── Fund Detail Page
    ├── Category Rankings Page
    └── Holdings Page
```

### Technology Stack

- **Framework**: Next.js 14 with App Router
- **Styling**: Tailwind CSS + CSS Custom Properties
- **Charts**: Recharts library
- **Fonts**: Inter (body), Manrope (headings)
- **Icons**: SVG-based icon system

### File Structure

```
frontend-next/
├── app/
│   ├── globals.css (Design tokens and base styles)
│   ├── fund/[fund_key]/
│   │   ├── page.tsx
│   │   ├── FundDetailClient.tsx (Enhanced with premium theme)
│   │   ├── NAVChart.tsx (Dark background)
│   │   ├── ScoreRadarChart.tsx (Dark background)
│   │   └── SectorPieChart.tsx (Dark background)
│   ├── category/[slug]/
│   │   ├── page.tsx
│   │   └── CategoryClient.tsx (Enhanced table and cards)
│   └── holdings/
│       └── HoldingsClient.tsx (Enhanced table)
└── Components/
    └── CategoryNav.tsx (Enhanced navigation)
```

## Components and Interfaces

### 1. Design Token System

**Color Palette**:
```css
/* Primary Colors */
--bg-page: #0B1220;           /* Page background */
--bg-card: #111827;           /* Card surface */
--bg-card-hover: #1F2937;     /* Card hover state */
--bg-input: #0F172A;          /* Input background */

/* Border Colors */
--border-default: #1E293B;    /* Default borders */
--border-subtle: #334155;     /* Subtle borders */

/* Text Colors */
--text-primary: #E5E7EB;      /* Primary text */
--text-secondary: #9CA3AF;    /* Secondary text */
--text-muted: #6B7280;        /* Muted text */

/* Accent Colors */
--accent-green: #10b981;      /* Primary accent, positive values */
--accent-blue: #3B82F6;       /* Links, info */
--accent-amber: #F59E0B;      /* Warning, average scores */
--accent-red: #EF4444;        /* Negative values, errors */
--accent-purple: #8B5CF6;     /* Additional data series */

/* Score Colors */
--score-excellent: #10b981;   /* 80+ */
--score-good: #4ADE80;        /* 60-79 */
--score-average: #F59E0B;     /* 40-59 */
--score-poor: #EF4444;        /* <40 */
```

**Typography Scale**:
```css
/* Font Families */
--font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
--font-heading: 'Manrope', 'Inter', sans-serif;
--font-mono: 'SF Mono', 'Consolas', 'Monaco', monospace;

/* Font Sizes */
--text-xs: 11px;
--text-sm: 12px;
--text-base: 14px;
--text-md: 16px;
--text-lg: 18px;
--text-xl: 20px;
--text-2xl: 24px;
--text-3xl: 28px;
--text-4xl: 32px;
--text-5xl: 36px;

/* Font Weights */
--weight-normal: 400;
--weight-medium: 500;
--weight-semibold: 600;
--weight-bold: 700;
--weight-extrabold: 800;
```

**Spacing Scale** (8px base unit):
```css
--space-1: 8px;
--space-2: 16px;
--space-3: 24px;
--space-4: 32px;
--space-5: 40px;
--space-6: 48px;
--space-8: 64px;
```

**Shadow System**:
```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.6);
```

**Border Radius**:
```css
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
--radius-xl: 20px;
```

### 2. Card Component System

**Base Card Component**:
```typescript
interface CardProps {
  children: React.ReactNode;
  padding?: 'sm' | 'md' | 'lg';
  hover?: boolean;
  className?: string;
}

// Styling
{
  backgroundColor: 'var(--bg-card)',
  border: '1px solid var(--border-default)',
  borderRadius: 'var(--radius-lg)',
  boxShadow: 'var(--shadow-md)',
  padding: 'var(--space-2)', // Mobile
  padding: 'var(--space-3)', // Desktop
  transition: 'all 0.2s ease',
}

// Hover state (if interactive)
{
  boxShadow: 'var(--shadow-lg)',
  transform: 'translateY(-2px)',
  borderColor: 'var(--border-subtle)',
}
```

**Score Card Component**:
```typescript
interface ScoreCardProps {
  label: string;
  value: number | null;
  type: 'score' | 'percentage' | 'decimal';
}

// Layout
<div className="score-card">
  <div className="score-label">{label}</div>
  <div className="score-value" style={{ color: getScoreColor(value) }}>
    {formatValue(value, type)}
  </div>
</div>

// Styling
.score-card {
  background: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-md);
  padding: var(--space-2);
  text-align: center;
}

.score-label {
  font-size: var(--text-xs);
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: var(--weight-semibold);
  margin-bottom: 8px;
}

.score-value {
  font-size: var(--text-3xl);
  font-weight: var(--weight-extrabold);
  font-family: var(--font-mono);
}
```

### 3. Chart Components

**NAV Chart Configuration**:
```typescript
interface NAVChartProps {
  data: Array<{ date: string; nav: number }>;
  height?: number;
}

// Recharts Configuration
<ResponsiveContainer width="100%" height={height || 400}>
  <LineChart data={data}>
    <CartesianGrid 
      strokeDasharray="3 3" 
      stroke="var(--border-default)" 
      opacity={0.3}
    />
    <XAxis 
      dataKey="date" 
      stroke="var(--text-secondary)"
      style={{ fontSize: 12 }}
    />
    <YAxis 
      stroke="var(--text-secondary)"
      style={{ fontSize: 12 }}
    />
    <Tooltip 
      contentStyle={{
        backgroundColor: 'var(--bg-card-hover)',
        border: '1px solid var(--border-default)',
        borderRadius: 'var(--radius-md)',
        color: 'var(--text-primary)',
      }}
    />
    <Line 
      type="monotone" 
      dataKey="nav" 
      stroke="var(--accent-green)" 
      strokeWidth={2}
      dot={false}
    />
  </LineChart>
</ResponsiveContainer>

// Container Styling
{
  backgroundColor: 'var(--bg-card)',
  border: '1px solid var(--border-default)',
  borderRadius: 'var(--radius-lg)',
  padding: 'var(--space-3)',
  boxShadow: 'var(--shadow-md)',
}
```

**Radar Chart Configuration**:
```typescript
interface RadarChartProps {
  data: Array<{ subject: string; value: number }>;
}

// Recharts Configuration
<ResponsiveContainer width="100%" height={350}>
  <RadarChart data={data}>
    <PolarGrid 
      stroke="var(--border-default)" 
      opacity={0.3}
    />
    <PolarAngleAxis 
      dataKey="subject" 
      stroke="var(--text-secondary)"
      style={{ fontSize: 12 }}
    />
    <PolarRadiusAxis 
      stroke="var(--text-secondary)"
      style={{ fontSize: 11 }}
    />
    <Radar 
      dataKey="value" 
      stroke="var(--accent-green)" 
      fill="var(--accent-green)" 
      fillOpacity={0.3}
      strokeWidth={2}
    />
  </RadarChart>
</ResponsiveContainer>
```

**Sector Pie Chart Configuration**:
```typescript
interface SectorPieChartProps {
  data: Array<{ name: string; value: number }>;
}

// Color Palette for Sectors
const SECTOR_COLORS = [
  'var(--accent-green)',
  'var(--accent-blue)',
  'var(--accent-amber)',
  'var(--accent-purple)',
  '#06B6D4', // Cyan
  '#EC4899', // Pink
  '#F97316', // Orange
];

// Recharts Configuration
<ResponsiveContainer width="100%" height={350}>
  <PieChart>
    <Pie
      data={data}
      cx="50%"
      cy="50%"
      labelLine={false}
      label={renderCustomLabel}
      outerRadius={120}
      fill="var(--accent-green)"
      dataKey="value"
    >
      {data.map((entry, index) => (
        <Cell 
          key={`cell-${index}`} 
          fill={SECTOR_COLORS[index % SECTOR_COLORS.length]} 
        />
      ))}
    </Pie>
    <Tooltip 
      contentStyle={{
        backgroundColor: 'var(--bg-card-hover)',
        border: '1px solid var(--border-default)',
        borderRadius: 'var(--radius-md)',
        color: 'var(--text-primary)',
      }}
    />
    <Legend 
      wrapperStyle={{
        fontSize: 12,
        color: 'var(--text-secondary)',
      }}
    />
  </PieChart>
</ResponsiveContainer>
```

### 4. Button Component System

**Primary Button**:
```typescript
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
}

// Primary Button Styling
{
  backgroundColor: 'var(--accent-green)',
  color: '#FFFFFF',
  border: 'none',
  borderRadius: 'var(--radius-md)',
  padding: '12px 24px',
  fontSize: 'var(--text-base)',
  fontWeight: 'var(--weight-semibold)',
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  minHeight: '44px',
}

// Hover State
{
  backgroundColor: '#059669', // Darker green
  transform: 'translateY(-2px)',
  boxShadow: 'var(--shadow-md)',
}

// Active State
{
  transform: 'translateY(0)',
  boxShadow: 'var(--shadow-sm)',
}
```

**Secondary Button**:
```typescript
// Secondary Button Styling
{
  backgroundColor: 'transparent',
  color: 'var(--accent-green)',
  border: '1px solid var(--accent-green)',
  borderRadius: 'var(--radius-md)',
  padding: '12px 24px',
  fontSize: 'var(--text-base)',
  fontWeight: 'var(--weight-semibold)',
  cursor: 'pointer',
  transition: 'all 0.2s ease',
}

// Hover State
{
  backgroundColor: 'var(--accent-green)',
  color: '#FFFFFF',
}
```

### 5. Input Component System

**Text Input**:
```typescript
interface InputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: 'text' | 'search' | 'number';
}

// Input Styling
{
  width: '100%',
  backgroundColor: 'var(--bg-input)',
  border: '1px solid var(--border-default)',
  borderRadius: 'var(--radius-md)',
  padding: '12px 16px',
  fontSize: 'var(--text-base)',
  color: 'var(--text-primary)',
  outline: 'none',
  transition: 'all 0.2s ease',
}

// Focus State
{
  borderColor: 'var(--accent-green)',
  boxShadow: '0 0 0 3px rgba(16, 185, 129, 0.1)',
}

// Placeholder Styling
::placeholder {
  color: 'var(--text-muted)',
}
```

**Select Dropdown**:
```typescript
interface SelectProps {
  value: string;
  onChange: (value: string) => void;
  options: Array<{ value: string; label: string }>;
}

// Select Styling
{
  width: '100%',
  backgroundColor: 'var(--bg-input)',
  border: '1px solid var(--border-default)',
  borderRadius: 'var(--radius-md)',
  padding: '12px 16px',
  fontSize: 'var(--text-base)',
  color: 'var(--text-primary)',
  cursor: 'pointer',
  outline: 'none',
  transition: 'all 0.2s ease',
}
```

### 6. Navigation Component

**Category Navigation Pills**:
```typescript
interface NavPillProps {
  label: string;
  href: string;
  isActive: boolean;
}

// Inactive Pill Styling
{
  display: 'inline-flex',
  alignItems: 'center',
  padding: '12px 20px',
  backgroundColor: 'var(--bg-card)',
  border: '1px solid var(--border-default)',
  borderRadius: 'var(--radius-md)',
  color: 'var(--text-secondary)',
  fontSize: 'var(--text-base)',
  fontWeight: 'var(--weight-medium)',
  textDecoration: 'none',
  transition: 'all 0.2s ease',
  whiteSpace: 'nowrap',
  minHeight: '44px',
}

// Active Pill Styling
{
  backgroundColor: 'var(--accent-green)',
  borderColor: 'var(--accent-green)',
  color: '#FFFFFF',
  fontWeight: 'var(--weight-semibold)',
}

// Hover State (Inactive)
{
  backgroundColor: 'var(--bg-card-hover)',
  borderColor: 'var(--border-subtle)',
  color: 'var(--text-primary)',
}

// Mobile: Horizontal Scroll Container
{
  display: 'flex',
  overflowX: 'auto',
  gap: 'var(--space-1)',
  padding: 'var(--space-1) 0',
  scrollbarWidth: 'none',
  msOverflowStyle: 'none',
}
```

### 7. Table Component (Desktop)

**Enhanced Table Styling**:
```typescript
// Table Container
{
  backgroundColor: 'var(--bg-card)',
  border: '1px solid var(--border-default)',
  borderRadius: 'var(--radius-lg)',
  overflow: 'hidden',
  boxShadow: 'var(--shadow-md)',
}

// Table Header
{
  backgroundColor: '#0F172A',
  position: 'sticky',
  top: 0,
  zIndex: 10,
}

// Table Header Cell
{
  padding: '12px 16px',
  fontSize: 'var(--text-xs)',
  fontWeight: 'var(--weight-bold)',
  color: 'var(--text-muted)',
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  textAlign: 'center',
  borderBottom: '1px solid var(--border-default)',
  cursor: 'pointer',
  userSelect: 'none',
  transition: 'all 0.15s ease',
}

// Active Sort Header
{
  color: 'var(--accent-green)',
}

// Table Row
{
  borderBottom: '1px solid var(--border-default)',
  transition: 'background-color 0.2s ease',
}

// Table Row Hover
{
  backgroundColor: 'var(--bg-card-hover)',
}

// Table Cell
{
  padding: '14px 16px',
  fontSize: 'var(--text-sm)',
  color: 'var(--text-primary)',
}

// Numeric Cell
{
  fontFamily: 'var(--font-mono)',
  fontVariantNumeric: 'tabular-nums',
  textAlign: 'center',
}

// Fund Name Link
{
  color: 'var(--accent-green)',
  fontWeight: 'var(--weight-semibold)',
  textDecoration: 'none',
  transition: 'color 0.15s ease',
}

// Fund Name Link Hover
{
  color: '#34D399', // Lighter green
}
```

### 8. Mobile Card Component (Fund List)

**Fund Card Layout**:
```typescript
interface FundCardProps {
  rank: number;
  fundName: string;
  amc: string;
  score: number;
  cagr3y: number;
  cagr5y: number;
  sharpe: number;
  aum: number;
  fundKey: string;
}

// Card Container
{
  backgroundColor: 'var(--bg-card)',
  border: '1px solid var(--border-default)',
  borderRadius: 'var(--radius-md)',
  padding: 'var(--space-2)',
  boxShadow: 'var(--shadow-md)',
  marginBottom: 'var(--space-2)',
  transition: 'all 0.2s ease',
}

// Card Active State (Touch)
{
  transform: 'scale(0.98)',
}

// Layout Structure
<div className="fund-card">
  {/* Top Row: Score Badge + Fund Info */}
  <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
    {/* Score Badge */}
    <div className="score-badge">
      <div className="score-value">{score}</div>
      <div className="score-label">Score</div>
    </div>
    
    {/* Fund Info */}
    <div style={{ flex: 1 }}>
      <div className="rank">Rank #{rank}</div>
      <Link href={`/fund/${fundKey}`} className="fund-name">
        {fundName}
      </Link>
      <div className="amc-name">{amc}</div>
    </div>
  </div>
  
  {/* Metrics Grid */}
  <div className="metrics-grid">
    <MetricItem label="3Y CAGR" value={cagr3y} type="percentage" />
    <MetricItem label="5Y CAGR" value={cagr5y} type="percentage" />
    <MetricItem label="Sharpe" value={sharpe} type="decimal" />
    <MetricItem label="AUM (₹ Cr)" value={aum} type="number" />
  </div>
</div>

// Metrics Grid Styling
{
  display: 'grid',
  gridTemplateColumns: '1fr 1fr',
  gap: 'var(--space-2)',
}
```

## Data Models

### Design Token Model

```typescript
interface DesignTokens {
  colors: {
    background: {
      page: string;
      card: string;
      cardHover: string;
      input: string;
    };
    border: {
      default: string;
      subtle: string;
    };
    text: {
      primary: string;
      secondary: string;
      muted: string;
    };
    accent: {
      green: string;
      blue: string;
      amber: string;
      red: string;
      purple: string;
    };
    score: {
      excellent: string;
      good: string;
      average: string;
      poor: string;
    };
  };
  typography: {
    fontFamily: {
      body: string;
      heading: string;
      mono: string;
    };
    fontSize: {
      xs: string;
      sm: string;
      base: string;
      md: string;
      lg: string;
      xl: string;
      '2xl': string;
      '3xl': string;
      '4xl': string;
      '5xl': string;
    };
    fontWeight: {
      normal: number;
      medium: number;
      semibold: number;
      bold: number;
      extrabold: number;
    };
  };
  spacing: {
    1: string;
    2: string;
    3: string;
    4: string;
    5: string;
    6: string;
    8: string;
  };
  shadow: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
  borderRadius: {
    sm: string;
    md: string;
    lg: string;
    xl: string;
  };
}
```

### Component Props Models

```typescript
// Card Component
interface CardComponentProps {
  children: React.ReactNode;
  padding?: 'sm' | 'md' | 'lg';
  hover?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

// Score Card
interface ScoreCardProps {
  label: string;
  value: number | null;
  type: 'score' | 'percentage' | 'decimal' | 'number';
  colorScheme?: 'score' | 'return' | 'neutral';
}

// Chart Container
interface ChartContainerProps {
  title?: string;
  children: React.ReactNode;
  height?: number;
  className?: string;
}

// Button
interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  className?: string;
}

// Input
interface InputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: 'text' | 'search' | 'number';
  disabled?: boolean;
  className?: string;
}

// Navigation Pill
interface NavPillProps {
  label: string;
  href: string;
  isActive: boolean;
  onClick?: () => void;
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*


### Correctness Properties

Based on the prework analysis, the following properties validate the visual design requirements:

**Property 1: Score Color Mapping**
*For any* score value displayed in a Score_Card, the color should be #10b981 for scores >= 80, #4ADE80 for scores 60-79, #F59E0B for scores 40-59, and #EF4444 for scores < 40
**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

**Property 2: Text Contrast Requirements**
*For any* text element, if it is primary text it should have minimum contrast ratio of 7:1 against its background, and if it is secondary text it should have minimum contrast ratio of 4.5:1 against its background
**Validates: Requirements 2.3, 2.4**

**Property 3: Tabular Numbers for Numeric Values**
*For any* numeric value display, the font-variant-numeric CSS property should be set to 'tabular-nums' to ensure proper alignment
**Validates: Requirements 2.5**

**Property 4: Typography Hierarchy**
*For any* page title element, the font size should be between 28-32px with font weight 700, and for any section heading, the font size should be between 18-20px with font weight 600
**Validates: Requirements 3.3, 3.4**

**Property 5: Metric Label Styling**
*For any* metric label element, the font size should be 11-12px, text-transform should be uppercase, and letter-spacing should be 0.05em
**Validates: Requirements 3.5**

**Property 6: Card Component Consistency**
*For any* Card_Component, it should have background color #111827, border-radius 16px, box-shadow applied, and 1px border with color #1E293B
**Validates: Requirements 4.1, 4.2, 4.3, 4.4**

**Property 7: Interactive Card Hover Effect**
*For any* interactive Card_Component, when hovered, it should apply an elevation effect with increased shadow and transform translateY(-2px)
**Validates: Requirements 4.5**

**Property 8: Chart Grid and Label Styling**
*For any* chart with grid lines, the grid lines should use color #1E293B with reduced opacity, and text labels should use color #9CA3AF
**Validates: Requirements 5.4, 5.5**

**Property 9: Overall Score Prominence**
*For any* overall score display, it should be rendered with font size 32-36px and font weight 800
**Validates: Requirements 6.5**

**Property 10: Table Row Hover Effect**
*For any* table row in the Category_Rankings_Page, when hovered, it should apply background color #1F2937
**Validates: Requirements 8.3**

**Property 11: Fund Name Link Styling**
*For any* fund name link in tables, it should use color #10b981 with a hover effect that changes the color
**Validates: Requirements 8.5**

**Property 12: Holdings Name Styling**
*For any* holding name display, it should use color #E5E7EB with font weight 600
**Validates: Requirements 9.2**

**Property 13: Allocation Percentage Coloring**
*For any* percentage allocation value, if the value is above 5% it should use color #10b981, otherwise it should use color #9CA3AF
**Validates: Requirements 9.3, 9.4**

**Property 14: Section Spacing Consistency**
*For any* major page section, the spacing between sections should be 32px on mobile viewports and 48px on desktop viewports
**Validates: Requirements 10.3**

**Property 15: Grid Gap Consistency**
*For any* card grid layout, the gap between cards should be 16px on mobile viewports and 24px on desktop viewports
**Validates: Requirements 10.4**

**Property 16: Card Padding Responsiveness**
*For any* Card_Component, the padding should be 16px on mobile viewports and 20-24px on desktop viewports
**Validates: Requirements 10.5**

**Property 17: Primary Button Styling**
*For any* primary button, it should have background color #10b981 and text color #FFFFFF
**Validates: Requirements 11.1**

**Property 18: Button Hover Transition**
*For any* button, when hovered, the transition should complete within 200ms and apply translateY(-2px) transform
**Validates: Requirements 11.2, 11.3**

**Property 19: Input Field Styling**
*For any* input field, it should have background color #0F172A and border color #1E293B
**Validates: Requirements 11.4**

**Property 20: Input Focus State**
*For any* input field, when focused, it should apply border color #10b981 with a subtle glow effect
**Validates: Requirements 11.5**

**Property 21: Navigation Pill Styling**
*For any* navigation pill, if inactive it should have background #111827, if active it should have background #10b981 with white text, and all pills should have 12px border radius and 12px horizontal padding
**Validates: Requirements 12.1, 12.2, 12.4**

**Property 22: Navigation Pill Hover**
*For any* inactive navigation pill, when hovered, it should apply background color #1F2937
**Validates: Requirements 12.3**

**Property 23: Chart Primary Data Color**
*For any* primary data series in charts, it should use color #10b981
**Validates: Requirements 13.1**

**Property 24: Chart Color Palette Consistency**
*For any* chart with multiple data series, it should use the consistent color palette: #10b981, #3B82F6, #F59E0B, #EF4444, #8B5CF6
**Validates: Requirements 13.2**

**Property 25: Chart Value Coloring**
*For any* value displayed in charts, if positive it should use color #10b981, if negative it should use color #EF4444
**Validates: Requirements 13.3, 13.4**

**Property 26: Chart Tooltip Styling**
*For any* chart tooltip, it should have background color #1F2937 and text color #E5E7EB
**Validates: Requirements 13.5**

**Property 27: Icon Size Consistency**
*For any* icon, it should use consistent sizing: 16px for inline, 20px for buttons, 24px for headers
**Validates: Requirements 15.1**

**Property 28: Icon Color States**
*For any* icon, if inactive it should use color #9CA3AF, if active or success state it should use color #10b981
**Validates: Requirements 15.2, 15.3**

**Property 29: Button Icon Spacing**
*For any* icon displayed in a button, there should be 8px spacing between the icon and text
**Validates: Requirements 15.4**

**Property 30: Icon Format**
*For any* icon, it should be in SVG format for crisp rendering
**Validates: Requirements 15.5**

**Property 31: Mobile Touch Target Size**
*For any* interactive element on mobile viewports (width < 768px), the minimum touch target size should be 44px
**Validates: Requirements 16.1**

**Property 32: Mobile Card Styling**
*For any* card on mobile viewports, it should have 16px padding and 12px border radius
**Validates: Requirements 16.2**

**Property 33: Mobile Chart Height**
*For any* chart on mobile viewports, it should be fully responsive with height between 300-350px
**Validates: Requirements 16.4**

**Property 34: Mobile Font Size Adjustment**
*For any* text element on mobile viewports (width < 768px), the font size should be increased by 1-2px compared to the base size
**Validates: Requirements 16.5**

**Property 35: Desktop Card Padding**
*For any* card on desktop viewports (width >= 768px), it should have 24px padding
**Validates: Requirements 17.2**

**Property 36: Desktop Chart Height**
*For any* chart on desktop viewports, it should have height between 400-450px
**Validates: Requirements 17.4**

**Property 37: ARIA Label Presence**
*For any* interactive element, it should include appropriate ARIA labels for accessibility
**Validates: Requirements 18.2**

**Property 38: Chart Text Alternatives**
*For any* chart component, it should provide text alternatives for screen readers
**Validates: Requirements 18.3**

**Property 39: Keyboard Accessibility**
*For any* interactive element, it should be accessible via keyboard navigation
**Validates: Requirements 18.4**

**Property 40: Focus Indicator Styling**
*For any* focusable element, when focused, it should display a focus indicator with color #10b981 and 2px outline
**Validates: Requirements 18.5**

**Property 41: Animation Performance**
*For any* animation, it should use CSS transforms to ensure smooth 60fps performance
**Validates: Requirements 19.2**

## Error Handling

### Visual Fallbacks

**Missing Data Handling**:
- When score values are null or undefined, display "—" instead of empty space
- When chart data is empty, display empty state message
- When images fail to load, show placeholder with appropriate background color

**Color Fallback**:
```typescript
function getScoreColor(score: number | null | undefined): string {
  if (score == null) return 'var(--text-muted)'; // Fallback for missing data
  if (score >= 80) return 'var(--score-excellent)';
  if (score >= 60) return 'var(--score-good)';
  if (score >= 40) return 'var(--score-average)';
  return 'var(--score-poor)';
}
```

**Font Loading Fallback**:
```css
/* Use font-display: swap for graceful fallback */
@font-face {
  font-family: 'Inter';
  font-display: swap;
  src: url('/fonts/inter.woff2') format('woff2');
}

@font-face {
  font-family: 'Manrope';
  font-display: swap;
  src: url('/fonts/manrope.woff2') format('woff2');
}
```

### Responsive Breakpoint Handling

**Viewport Detection**:
```typescript
function useViewport() {
  const [viewport, setViewport] = useState<'mobile' | 'tablet' | 'desktop'>('desktop');
  
  useEffect(() => {
    function handleResize() {
      const width = window.innerWidth;
      if (width < 768) setViewport('mobile');
      else if (width < 1024) setViewport('tablet');
      else setViewport('desktop');
    }
    
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  
  return viewport;
}
```

### Chart Rendering Errors

**Chart Error Boundary**:
```typescript
class ChartErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="chart-error-state">
          <p>Unable to load chart</p>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Loading States

**Skeleton Loader Component**:
```typescript
function SkeletonLoader({ width, height, className }: {
  width?: string;
  height?: string;
  className?: string;
}) {
  return (
    <div 
      className={`skeleton ${className}`}
      style={{
        width: width || '100%',
        height: height || '20px',
        backgroundColor: 'var(--bg-card)',
        borderRadius: 'var(--radius-md)',
        animation: 'skeleton-loading 1.5s ease-in-out infinite',
      }}
    />
  );
}

// CSS Animation
@keyframes skeleton-loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
```

### Empty States

**Empty State Component**:
```typescript
function EmptyState({ 
  title, 
  message, 
  icon 
}: {
  title: string;
  message: string;
  icon?: React.ReactNode;
}) {
  return (
    <div className="empty-state">
      {icon && <div className="empty-state-icon">{icon}</div>}
      <h3 style={{ color: 'var(--text-primary)' }}>{title}</h3>
      <p style={{ color: 'var(--text-muted)' }}>{message}</p>
    </div>
  );
}

// Styling
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-6);
  text-align: center;
  background-color: var(--bg-card);
  border: 1px solid var(--border-default);
  border-radius: var(--radius-lg);
}
```

## Testing Strategy

### Dual Testing Approach

The testing strategy combines unit tests for specific examples and edge cases with property-based tests for universal properties across all inputs.

**Unit Tests**: Focus on specific examples, edge cases, and integration points
- Verify specific color values for design tokens
- Test individual component rendering
- Validate responsive breakpoint behavior
- Check accessibility attributes
- Test error states and loading states

**Property Tests**: Focus on universal properties that hold for all inputs
- Verify color mapping rules across all score values
- Test contrast ratios for all text/background combinations
- Validate spacing consistency across all components
- Check hover effects for all interactive elements
- Verify responsive behavior across viewport ranges

### Testing Tools

**Unit Testing**:
- Framework: Jest + React Testing Library
- Component testing: @testing-library/react
- DOM queries: @testing-library/dom
- User interactions: @testing-library/user-event

**Property-Based Testing**:
- Library: fast-check (JavaScript/TypeScript property-based testing)
- Configuration: Minimum 100 iterations per property test
- Each property test references its design document property

**Visual Regression Testing**:
- Tool: Percy or Chromatic
- Test key pages at multiple breakpoints
- Verify color accuracy and visual consistency

**Accessibility Testing**:
- Tool: axe-core + jest-axe
- Verify ARIA labels and semantic HTML
- Test keyboard navigation
- Check color contrast ratios

### Test Organization

```
frontend-next/
├── __tests__/
│   ├── unit/
│   │   ├── components/
│   │   │   ├── Card.test.tsx
│   │   │   ├── Button.test.tsx
│   │   │   ├── Input.test.tsx
│   │   │   └── NavPill.test.tsx
│   │   ├── pages/
│   │   │   ├── FundDetail.test.tsx
│   │   │   ├── CategoryRankings.test.tsx
│   │   │   └── Holdings.test.tsx
│   │   └── utils/
│   │       ├── colorUtils.test.ts
│   │       └── formatters.test.ts
│   ├── property/
│   │   ├── scoreColorMapping.property.test.ts
│   │   ├── textContrast.property.test.ts
│   │   ├── cardStyling.property.test.ts
│   │   ├── spacing.property.test.ts
│   │   └── accessibility.property.test.ts
│   └── integration/
│       ├── fundDetailFlow.test.tsx
│       └── categoryBrowsing.test.tsx
```

### Property Test Examples

**Property Test for Score Color Mapping**:
```typescript
import fc from 'fast-check';
import { getScoreColor } from '@/lib/colorUtils';

describe('Property: Score Color Mapping', () => {
  it('Feature: fintech-premium-ui-redesign, Property 1: For any score value, color should match the defined ranges', () => {
    fc.assert(
      fc.property(
        fc.oneof(
          fc.constant(null),
          fc.float({ min: 0, max: 100 })
        ),
        (score) => {
          const color = getScoreColor(score);
          
          if (score == null) {
            expect(color).toBe('#6B7280');
          } else if (score >= 80) {
            expect(color).toBe('#10b981');
          } else if (score >= 60) {
            expect(color).toBe('#4ADE80');
          } else if (score >= 40) {
            expect(color).toBe('#F59E0B');
          } else {
            expect(color).toBe('#EF4444');
          }
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

**Property Test for Card Styling Consistency**:
```typescript
import fc from 'fast-check';
import { render } from '@testing-library/react';
import { Card } from '@/components/Card';

describe('Property: Card Component Consistency', () => {
  it('Feature: fintech-premium-ui-redesign, Property 6: All cards should have consistent styling', () => {
    fc.assert(
      fc.property(
        fc.record({
          children: fc.string(),
          padding: fc.constantFrom('sm', 'md', 'lg'),
          hover: fc.boolean(),
        }),
        (props) => {
          const { container } = render(<Card {...props}>{props.children}</Card>);
          const card = container.firstChild as HTMLElement;
          
          const styles = window.getComputedStyle(card);
          
          expect(styles.backgroundColor).toBe('rgb(17, 24, 39)'); // #111827
          expect(styles.borderRadius).toBe('16px');
          expect(styles.borderWidth).toBe('1px');
          expect(styles.borderColor).toBe('rgb(30, 41, 59)'); // #1E293B
          expect(styles.boxShadow).toBeTruthy();
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

**Property Test for Touch Target Size**:
```typescript
import fc from 'fast-check';
import { render } from '@testing-library/react';
import { Button } from '@/components/Button';

describe('Property: Mobile Touch Target Size', () => {
  it('Feature: fintech-premium-ui-redesign, Property 31: All interactive elements on mobile should have minimum 44px touch target', () => {
    // Set mobile viewport
    global.innerWidth = 375;
    
    fc.assert(
      fc.property(
        fc.record({
          children: fc.string(),
          variant: fc.constantFrom('primary', 'secondary', 'ghost'),
        }),
        (props) => {
          const { container } = render(<Button {...props}>{props.children}</Button>);
          const button = container.firstChild as HTMLElement;
          
          const styles = window.getComputedStyle(button);
          const height = parseInt(styles.minHeight);
          
          expect(height).toBeGreaterThanOrEqual(44);
        }
      ),
      { numRuns: 100 }
    );
  });
});
```

### Unit Test Examples

**Unit Test for Design Tokens**:
```typescript
describe('Design Tokens', () => {
  it('should define correct page background color', () => {
    const root = document.documentElement;
    const bgPage = getComputedStyle(root).getPropertyValue('--bg-page').trim();
    expect(bgPage).toBe('#0B1220');
  });
  
  it('should define correct card background color', () => {
    const root = document.documentElement;
    const bgCard = getComputedStyle(root).getPropertyValue('--bg-card').trim();
    expect(bgCard).toBe('#111827');
  });
  
  it('should define correct primary text color', () => {
    const root = document.documentElement;
    const textPrimary = getComputedStyle(root).getPropertyValue('--text-primary').trim();
    expect(textPrimary).toBe('#E5E7EB');
  });
});
```

**Unit Test for Chart Background**:
```typescript
import { render } from '@testing-library/react';
import { NAVChart } from '@/app/fund/[fund_key]/NAVChart';

describe('NAVChart', () => {
  it('should render with dark background color #111827', () => {
    const mockData = [
      { date: '2024-01-01', nav: 100 },
      { date: '2024-01-02', nav: 105 },
    ];
    
    const { container } = render(<NAVChart data={mockData} />);
    const chartContainer = container.querySelector('.chart-container');
    
    const styles = window.getComputedStyle(chartContainer!);
    expect(styles.backgroundColor).toBe('rgb(17, 24, 39)'); // #111827
  });
});
```

**Unit Test for Responsive Behavior**:
```typescript
import { render } from '@testing-library/react';
import { CategoryClient } from '@/app/category/[slug]/CategoryClient';

describe('CategoryClient Responsive Behavior', () => {
  it('should display table on desktop viewport', () => {
    global.innerWidth = 1024;
    
    const { container } = render(
      <CategoryClient initialRows={mockRows} categoryName="Large Cap" />
    );
    
    const table = container.querySelector('.desktop-table');
    const cards = container.querySelector('.mobile-cards');
    
    expect(table).toBeVisible();
    expect(cards).not.toBeVisible();
  });
  
  it('should display cards on mobile viewport', () => {
    global.innerWidth = 375;
    
    const { container } = render(
      <CategoryClient initialRows={mockRows} categoryName="Large Cap" />
    );
    
    const table = container.querySelector('.desktop-table');
    const cards = container.querySelector('.mobile-cards');
    
    expect(table).not.toBeVisible();
    expect(cards).toBeVisible();
  });
});
```

### Accessibility Testing

**Accessibility Unit Tests**:
```typescript
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { FundDetailClient } from '@/app/fund/[fund_key]/FundDetailClient';

expect.extend(toHaveNoViolations);

describe('Accessibility', () => {
  it('should have no accessibility violations on Fund Detail page', async () => {
    const { container } = render(
      <FundDetailClient fundDetail={mockFundDetail} navData={mockNavData} />
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  it('should have proper ARIA labels on interactive elements', () => {
    const { getByRole } = render(<Button>View Details</Button>);
    const button = getByRole('button', { name: /view details/i });
    expect(button).toBeInTheDocument();
  });
  
  it('should maintain focus indicators', () => {
    const { getByRole } = render(<Input placeholder="Search funds" />);
    const input = getByRole('textbox');
    
    input.focus();
    const styles = window.getComputedStyle(input);
    
    expect(styles.outlineColor).toBe('rgb(16, 185, 129)'); // #10b981
    expect(styles.outlineWidth).toBe('2px');
  });
});
```

### Performance Testing

**Performance Benchmarks**:
```typescript
describe('Performance', () => {
  it('should render large fund list within performance budget', () => {
    const largeDataset = generateMockFunds(1000);
    
    const startTime = performance.now();
    render(<CategoryClient initialRows={largeDataset} categoryName="Large Cap" />);
    const endTime = performance.now();
    
    const renderTime = endTime - startTime;
    expect(renderTime).toBeLessThan(1000); // Should render in less than 1 second
  });
  
  it('should lazy load chart components', async () => {
    const { findByTestId } = render(<FundDetailClient fundDetail={mockFundDetail} />);
    
    // Chart should not be in DOM initially
    expect(screen.queryByTestId('nav-chart')).not.toBeInTheDocument();
    
    // Chart should load when scrolled into view
    const chart = await findByTestId('nav-chart');
    expect(chart).toBeInTheDocument();
  });
});
```

### Test Coverage Goals

- **Unit Test Coverage**: Minimum 80% code coverage
- **Property Test Coverage**: All correctness properties implemented
- **Visual Regression**: Key pages tested at 3 breakpoints (mobile, tablet, desktop)
- **Accessibility**: Zero axe violations on all pages
- **Performance**: All pages render within 1 second on 3G connection

### Continuous Integration

**CI Pipeline**:
1. Run unit tests on every commit
2. Run property tests on every pull request
3. Run visual regression tests on staging deployment
4. Run accessibility tests before production deployment
5. Monitor performance metrics in production

**Test Commands**:
```bash
# Run all tests
npm test

# Run unit tests only
npm run test:unit

# Run property tests only
npm run test:property

# Run with coverage
npm run test:coverage

# Run accessibility tests
npm run test:a11y

# Run visual regression tests
npm run test:visual
```
