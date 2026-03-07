import type { Metadata } from "next";
import FAQ, { FAQItem } from "@/Components/FAQ";

export const metadata: Metadata = {
  title: "Mutual Fund FAQ - Complete Guide to MF Investing in India",
  description: "Comprehensive FAQ covering mutual fund basics, investment strategies, metrics like Sharpe ratio, alpha, rolling returns, and how to choose the best mutual funds in India.",
  keywords: [
    "mutual fund FAQ",
    "mutual fund questions",
    "what is NAV",
    "what is SIP",
    "Sharpe ratio explained",
    "alpha in mutual funds",
    "rolling returns",
    "mutual fund investing guide"
  ]
};

const investmentStyleFAQs: FAQItem[] = [
  {
    question: "What is a Balanced investment style?",
    answer: "Balanced style gives equal weight (25% each) to all five scoring dimensions: Recent Performance, Consistency, Risk, Valuation, and Portfolio Quality. This approach is ideal for most investors as it identifies well-rounded funds that perform consistently across all parameters without over-emphasizing any single aspect. It's the default setting and works well for long-term wealth creation."
  },
  {
    question: "What is an Aggressive investment style?",
    answer: "Aggressive style prioritizes Recent Performance (higher returns) and gives more weight to growth metrics. This approach favors funds with strong recent momentum and higher returns, even if they come with increased volatility. Suitable for investors with high risk tolerance, longer investment horizons (7-10 years), and those seeking maximum capital appreciation. Best for younger investors who can weather market volatility."
  },
  {
    question: "What is a Conservative investment style?",
    answer: "Conservative style emphasizes Consistency and Risk metrics over raw returns. This approach favors funds with stable, predictable performance and lower volatility, even if absolute returns are moderate. Ideal for risk-averse investors, those nearing retirement, or investors with shorter time horizons (3-5 years) who prioritize capital preservation and steady growth over aggressive gains."
  },
  {
    question: "Which investment style should I choose?",
    answer: "Choose based on your risk tolerance and goals: Balanced for most investors seeking overall quality, Aggressive if you're young with high risk appetite and long horizon (10+ years), Conservative if you're risk-averse or nearing financial goals. You can also create a Custom style by adjusting individual weights - for example, increase Consistency weight if you value predictable returns, or increase Valuation weight if you prefer value investing."
  },
  {
    question: "Can I customize the weights myself?",
    answer: "Yes! Our Weight Customizer allows you to create your own custom investment style by adjusting the weight of each dimension (Consistency, Recent Performance, Risk, Valuation, Portfolio Quality). Simply use the sliders to set your preferred weights - they must total 100%. This lets you align the scoring with your personal investment philosophy and priorities."
  },
  {
    question: "How do investment styles affect fund rankings?",
    answer: "Different styles will rank funds differently. For example, a fund with high returns but high volatility will rank higher in Aggressive style but lower in Conservative style. A fund with moderate but consistent returns will rank higher in Conservative/Balanced styles. The style you choose determines which fund characteristics are prioritized in the scoring algorithm."
  }
];

const beginnerFAQs: FAQItem[] = [
  {
    question: "What is a mutual fund?",
    answer: "A mutual fund is an investment vehicle that pools money from multiple investors to invest in a diversified portfolio of stocks, bonds, or other securities. Professional fund managers make investment decisions on behalf of investors. Each investor owns units representing their share of the fund's holdings."
  },
  {
    question: "What is NAV (Net Asset Value)?",
    answer: "NAV is the per-unit market value of a mutual fund. It's calculated by dividing the total value of all securities in the fund's portfolio (minus liabilities) by the total number of outstanding units. NAV is declared daily after market close and is the price at which you buy or sell fund units."
  },
  {
    question: "What is SIP (Systematic Investment Plan)?",
    answer: "SIP is a method of investing a fixed amount regularly (monthly, quarterly) in a mutual fund. It helps average out market volatility through rupee cost averaging - you buy more units when prices are low and fewer when prices are high. SIPs are ideal for salaried individuals and long-term wealth creation."
  },
  {
    question: "What is the difference between Direct and Regular plans?",
    answer: "Direct plans have no distributor commission, resulting in lower expense ratios (typically 0.5-1% lower) and higher returns over time. Regular plans include distributor commissions. Always choose Direct plans if you're investing on your own - the difference compounds significantly over 10-20 years."
  },
  {
    question: "What is an expense ratio?",
    answer: "Expense ratio (TER - Total Expense Ratio) is the annual fee charged by the fund house for managing your money, expressed as a percentage of assets. It includes fund management fees, administrative costs, and marketing expenses. Lower is better - for equity funds, look for expense ratios below 1% for direct plans."
  },
  {
    question: "How are mutual funds taxed in India?",
    answer: "For equity funds (>65% equity): Long-term gains (held >1 year) above ₹1 lakh are taxed at 10%. Short-term gains are taxed at 15%. For debt funds: Gains are added to your income and taxed at your slab rate. ELSS funds have a 3-year lock-in period and qualify for 80C deduction up to ₹1.5 lakh."
  },
  {
    question: "What is AUM (Assets Under Management)?",
    answer: "AUM is the total market value of assets that a mutual fund manages. Very small AUMs (<₹100 crore) can indicate lack of investor confidence or liquidity issues. Very large AUMs (>₹50,000 crore) can make it difficult for fund managers to be nimble. Moderate AUMs (₹1,000-10,000 crore) are often ideal."
  },
  {
    question: "Can I lose money in mutual funds?",
    answer: "Yes, mutual funds are market-linked investments and carry risk. Your investment value can go down, especially in the short term. However, historically, equity mutual funds have delivered positive returns over 5-10 year periods. Diversification and long-term investing help mitigate risks."
  }
];

const intermediateFAQs: FAQItem[] = [
  {
    question: "What is Sharpe ratio?",
    answer: "Sharpe ratio measures risk-adjusted returns - how much excess return you're getting per unit of risk (volatility). Formula: (Fund Return - Risk-free Rate) / Standard Deviation. Higher is better. A Sharpe ratio above 1 is good, above 2 is excellent. It helps compare funds with different risk levels."
  },
  {
    question: "What is Sortino ratio?",
    answer: "Similar to Sharpe ratio but only considers downside volatility (negative returns), ignoring upside volatility. This is more relevant for investors as upside volatility is desirable. Higher Sortino ratios indicate better risk-adjusted returns with less downside risk."
  },
  {
    question: "What is alpha in mutual funds?",
    answer: "Alpha measures a fund's excess return compared to its benchmark index. Positive alpha means the fund outperformed its benchmark (good fund management), negative alpha means underperformance. An alpha of 2% means the fund beat its benchmark by 2% annually."
  },
  {
    question: "What is beta in mutual funds?",
    answer: "Beta measures a fund's volatility relative to its benchmark. Beta of 1 means the fund moves in line with the market. Beta >1 means higher volatility (more aggressive), Beta <1 means lower volatility (more defensive). Upside beta and downside beta show behavior in rising and falling markets respectively."
  },
  {
    question: "What is standard deviation in mutual funds?",
    answer: "Standard deviation measures volatility - how much a fund's returns deviate from its average return. Higher standard deviation means higher volatility and risk. For example, a fund with 15% standard deviation can be expected to have returns within ±15% of its average return about 68% of the time."
  },
  {
    question: "What is Information Ratio?",
    answer: "Information Ratio measures a fund manager's skill in generating excess returns relative to the benchmark, adjusted for the risk taken. Formula: (Fund Return - Benchmark Return) / Tracking Error. Higher is better. An IR above 0.5 is considered good, above 0.75 is excellent."
  },
  {
    question: "What is portfolio turnover ratio?",
    answer: "Turnover ratio indicates how frequently the fund manager buys and sells securities. High turnover (>100%) means active trading, which can increase transaction costs and tax implications. Low turnover (<50%) indicates a buy-and-hold strategy. Neither is inherently better - it depends on the fund's strategy."
  },
  {
    question: "What is tracking error?",
    answer: "Tracking error measures how closely a fund follows its benchmark index. It's the standard deviation of the difference between fund returns and benchmark returns. Lower tracking error means the fund closely mimics the benchmark. For index funds, tracking error should be minimal (<1%)."
  }
];

const advancedFAQs: FAQItem[] = [
  {
    question: "What is rolling return?",
    answer: "Rolling returns measure returns over overlapping time periods (e.g., every 3-year period over the last 10 years). Unlike point-to-point returns, rolling returns show consistency across different market cycles. High median rolling returns with low variation indicate consistent performance regardless of entry timing."
  },
  {
    question: "What is maximum drawdown?",
    answer: "Maximum drawdown is the largest peak-to-trough decline in a fund's value during a specific period. It shows the worst-case scenario an investor would have experienced. For example, a 30% max drawdown means the fund fell 30% from its peak before recovering. Lower drawdowns indicate better downside protection."
  },
  {
    question: "What is downside capture ratio?",
    answer: "Downside capture ratio measures how much a fund falls when the market declines. A ratio of 80% means when the market falls 10%, the fund falls only 8% (good downside protection). Lower is better. Funds with low downside capture and high upside capture are ideal."
  },
  {
    question: "What is upside capture ratio?",
    answer: "Upside capture ratio measures how much a fund gains when the market rises. A ratio of 120% means when the market rises 10%, the fund rises 12% (excellent). Higher is better. Combined with downside capture, it shows a fund's ability to participate in rallies while protecting in downturns."
  },
  {
    question: "What is the Treynor ratio?",
    answer: "Treynor ratio measures risk-adjusted returns using beta (systematic risk) instead of total volatility. Formula: (Fund Return - Risk-free Rate) / Beta. It's useful for well-diversified portfolios where systematic risk is the primary concern. Higher values indicate better risk-adjusted performance."
  },
  {
    question: "What is R-squared in mutual funds?",
    answer: "R-squared measures how much of a fund's movement can be explained by movements in its benchmark index (0-100%). High R-squared (>85%) means the fund closely follows its benchmark. Low R-squared means the fund's performance is driven by factors other than the benchmark."
  },
  {
    question: "What is the Calmar ratio?",
    answer: "Calmar ratio measures return relative to maximum drawdown. Formula: Annualized Return / Maximum Drawdown. It shows how much return you're getting for the worst-case risk. Higher is better. A Calmar ratio above 0.5 is considered good."
  },
  {
    question: "What is portfolio concentration risk?",
    answer: "Concentration risk arises when a fund has too much exposure to a few stocks or sectors. We measure this using: 1) Top 10 holdings percentage (>40% is high concentration), 2) Sector HHI (Herfindahl Index - higher values indicate concentration), 3) Top 3 sector exposure (>60% is risky). Diversification reduces concentration risk."
  },
  {
    question: "What is the difference between CAGR and absolute return?",
    answer: "Absolute return is the simple percentage gain/loss over a period. CAGR (Compound Annual Growth Rate) is the annualized return assuming compounding. CAGR is better for comparing funds over different time periods. For example, 100% return over 5 years = 14.87% CAGR."
  },
  {
    question: "How does MF Screener calculate fund scores?",
    answer: "Our proprietary scoring system evaluates funds across 5 dimensions: 1) Recent Performance (3M, 6M, 1Y, 3Y, 5Y returns), 2) Consistency (rolling return stability using alpha), 3) Risk (volatility, drawdowns, beta), 4) Valuation (portfolio PE, PB, ROE), 5) Portfolio Quality (diversification, AUM, expense ratio, turnover, manager experience). Each metric is normalized to 0-100 percentile within its category, then weighted to create the final score. You can customize weights using our Weight Customizer."
  }
];

export default function FAQPage() {
  return (
    <div style={{ 
      backgroundColor: "var(--bg-page)", 
      minHeight: "100vh", 
      padding: "40px 20px",
      fontFamily: "Inter, system-ui, sans-serif" 
    }}>
      <div style={{ maxWidth: 1000, margin: "0 auto" }}>
        {/* Header */}
        <div style={{ marginBottom: 48, textAlign: "center" }}>
          <h1 style={{ 
            fontSize: 42, 
            fontWeight: 800, 
            color: "var(--text-primary)",
            marginBottom: 16,
            letterSpacing: "-0.02em"
          }}>
            Mutual Fund FAQ
          </h1>
          <p style={{ 
            fontSize: 18, 
            color: "var(--text-secondary)",
            lineHeight: 1.6
          }}>
            Everything you need to know about mutual fund investing in India
          </p>
        </div>

        {/* Beginner Section */}
        <div style={{ marginBottom: 40 }}>
          <FAQ items={beginnerFAQs} title="Beginner Questions" />
        </div>

        {/* Intermediate Section */}
        <div style={{ marginBottom: 40 }}>
          <FAQ items={intermediateFAQs} title="Intermediate - Understanding Metrics" />
        </div>

        {/* Advanced Section */}
        <div style={{ marginBottom: 40 }}>
          <FAQ items={advancedFAQs} title="Advanced - Deep Dive" />
        </div>

        {/* CTA */}
        <div style={{ 
          textAlign: "center", 
          padding: 40,
          backgroundColor: "var(--bg-card)",
          borderRadius: 16,
          border: "1px solid var(--border-default)"
        }}>
          <h2 style={{ 
            fontSize: 28, 
            fontWeight: 700, 
            color: "var(--text-primary)",
            marginBottom: 16
          }}>
            Ready to find your perfect mutual fund?
          </h2>
          <p style={{ 
            fontSize: 16, 
            color: "var(--text-secondary)",
            marginBottom: 24
          }}>
            Use our advanced screener to compare and analyze 1000+ funds
          </p>
          <a 
            href="/category/large-cap"
            style={{
              display: "inline-block",
              padding: "14px 28px",
              fontSize: 16,
              fontWeight: 600,
              backgroundColor: "var(--accent-primary)",
              color: "#FFFFFF",
              borderRadius: 12,
              textDecoration: "none",
              transition: "all 0.2s ease"
            }}
          >
            Start Screening →
          </a>
        </div>
      </div>
    </div>
  );
}
