// lib/weights.ts

export type InvestorType = "balanced" | "conservative" | "aggressive";

export const INVESTOR_PRESETS: Record<
  InvestorType,
  Record<string, number>
> = {
  balanced: {
    consistency: 30,
    performance: 15,
    risk: 25,
    portfolio: 20,
    valuation: 10,
  },

  conservative: {
    consistency: 40,
    risk: 30,
    portfolio: 20,
    performance: 5,
    valuation: 5,
  },

  aggressive: {
    performance: 35,
    risk: 20,
    valuation: 20,
    portfolio: 15,
    consistency: 10,
  },
};
