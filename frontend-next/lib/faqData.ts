import { FAQItem } from "@/Components/FAQ";

// Homepage FAQs - Broad beginner questions
export const homepageFAQs: FAQItem[] = [
  {
    question: "What is MF Screener?",
    answer: "MF Screener is India's most comprehensive mutual fund analysis platform. We help investors compare and analyze 1000+ equity mutual funds using advanced metrics, proprietary scoring, and intelligent filtering. Our platform is updated daily with the latest NAV data and fund performance metrics."
  },
  {
    question: "How does the MF Screener score work?",
    answer: "Our proprietary scoring system evaluates funds across 5 key dimensions: Recent Performance (returns), Consistency (rolling returns stability), Risk (volatility and drawdowns), Valuation (portfolio PE/PB ratios), and Portfolio Quality (diversification, AUM, expense ratio). Each dimension is weighted and normalized to create a final score out of 100. You can customize these weights using our Weight Customizer tool."
  },
  {
    question: "What are Balanced, Aggressive, and Conservative investment styles?",
    answer: "These are preset weight configurations in our Weight Customizer: Balanced (25% each dimension) suits most investors seeking well-rounded funds. Aggressive (higher weight on returns and recent performance) is for growth-focused investors willing to take more risk. Conservative (higher weight on consistency and risk metrics) is for risk-averse investors prioritizing stability over high returns."
  },
  {
    question: "How do I choose a mutual fund in India?",
    answer: "Start by identifying your investment goal and risk tolerance. Use our category filters (Large Cap, Mid Cap, etc.) to narrow down options. Look for funds with consistent performance (high rolling returns), low volatility, reasonable expense ratios, and experienced fund managers. Our scoring system helps identify top performers, but always consider your personal financial goals and time horizon."
  },
  {
    question: "What is a good mutual fund score?",
    answer: "Scores above 70 are considered excellent, 60-70 are good, 40-60 are average, and below 40 need careful evaluation. However, the score is just one factor - also consider the fund's category, your risk appetite, investment horizon, and how it fits into your overall portfolio diversification strategy."
  },
  {
    question: "Is MF Screener free to use?",
    answer: "Yes! MF Screener is completely free to use. We provide comprehensive fund analysis, advanced filtering, customizable scoring, and daily data updates at no cost. Our mission is to democratize mutual fund research and help Indian investors make informed decisions."
  },
  {
    question: "How often are the scores updated?",
    answer: "Our database is updated daily with the latest NAV (Net Asset Value) data from AMFI. Fund scores and rankings are recalculated every day to reflect the most current performance metrics. Portfolio holdings and qualitative data are updated monthly as fund houses release their factsheets."
  }
];

// Category Page FAQs
export const categoryFAQs: Record<string, FAQItem[]> = {
  "large-cap": [
    {
      question: "What are Large Cap mutual funds?",
      answer: "Large Cap funds invest at least 80% of their assets in the top 100 companies by market capitalization. These are well-established, blue-chip companies like Reliance, TCS, HDFC Bank, and Infosys. Large Cap funds offer relatively stable returns with lower volatility compared to mid and small cap funds."
    },
    {
      question: "Who should invest in Large Cap funds?",
      answer: "Large Cap funds are suitable for conservative investors seeking steady growth with lower risk. They're ideal for first-time mutual fund investors, those nearing retirement, or anyone with a 3-5 year investment horizon who wants exposure to India's top companies."
    },
    {
      question: "What returns can I expect from Large Cap funds?",
      answer: "Historically, Large Cap funds have delivered 10-12% annualized returns over 5-10 year periods. However, past performance doesn't guarantee future results. Returns vary based on market conditions, fund management, and economic cycles."
    },
    {
      question: "How do I compare Large Cap funds?",
      answer: "Use our screener to compare funds based on: 1) Consistent rolling returns (3Y and 5Y), 2) Low volatility and drawdowns, 3) Sharpe and Sortino ratios for risk-adjusted returns, 4) Expense ratio (lower is better), 5) Fund manager experience, and 6) AUM size (very large or very small AUMs can be concerning)."
    }
  ],
  "mid-cap": [
    {
      question: "What are Mid Cap mutual funds?",
      answer: "Mid Cap funds invest at least 65% of their assets in companies ranked 101-250 by market capitalization. These are growing companies with strong potential but higher volatility than large caps. Mid caps offer a balance between growth potential and stability."
    },
    {
      question: "Are Mid Cap funds risky?",
      answer: "Mid Cap funds carry moderate to high risk. They're more volatile than Large Cap funds but less risky than Small Cap funds. During market downturns, mid caps can see significant corrections, but they also have strong recovery potential. Suitable for investors with 5-7 year horizon and moderate risk appetite."
    },
    {
      question: "What returns can I expect from Mid Cap funds?",
      answer: "Mid Cap funds have historically delivered 12-15% annualized returns over long periods, outperforming Large Caps. However, they experience higher volatility and deeper drawdowns during market corrections."
    }
  ],
  "small-cap": [
    {
      question: "What are Small Cap mutual funds?",
      answer: "Small Cap funds invest at least 65% in companies ranked 251st onwards by market capitalization. These are emerging companies with high growth potential but also the highest risk and volatility among equity fund categories."
    },
    {
      question: "Who should invest in Small Cap funds?",
      answer: "Small Cap funds are suitable only for aggressive investors with high risk tolerance and a long investment horizon (7-10 years minimum). They should form a small portion (10-20%) of your overall equity portfolio for diversification."
    }
  ]
};

// Fund-specific FAQ template (will be dynamically populated)
export const getFundPageFAQs = (fundName: string, amc: string): FAQItem[] => [
  {
    question: `Is ${fundName} a good investment?`,
    answer: `${fundName} is managed by ${amc}. Check our comprehensive score and metrics above to evaluate its performance across returns, consistency, risk, and portfolio quality. Compare it with peer funds in the same category and consider your investment goals and risk tolerance before investing.`
  },
  {
    question: `What is the expense ratio of ${fundName}?`,
    answer: `The expense ratio (TER) is displayed in the fund details above. Lower expense ratios mean more of your returns stay with you. For equity funds, anything below 1% for direct plans is considered good. Always choose Direct plans over Regular plans to save on costs.`
  },
  {
    question: `Who is the fund manager of ${fundName}?`,
    answer: `Fund manager details are shown in the fund information section above. Check their experience, track record, and tenure with this fund. Experienced managers with consistent performance across market cycles are preferable.`
  },
  {
    question: `What is the risk level of ${fundName}?`,
    answer: `Check the volatility, maximum drawdown, and beta metrics above. Lower volatility and drawdown indicate lower risk. Also review the Sharpe and Sortino ratios - higher values indicate better risk-adjusted returns.`
  },
  {
    question: `What does the MF Screener score mean for ${fundName}?`,
    answer: `Our score evaluates this fund across 5 dimensions: Recent Performance, Consistency, Risk, Valuation, and Portfolio Quality. A higher score indicates better overall performance, but always review individual metrics and compare with similar funds before making investment decisions.`
  }
];
