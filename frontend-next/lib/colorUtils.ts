/**
 * Color utility functions for the premium fintech UI
 * Returns CSS variable names for consistent theming
 */

/**
 * Get color for score values based on premium design system
 * @param score - Score value (0-100) or null/undefined
 * @returns CSS variable name
 * 
 * Color mapping:
 * - 80+: --score-excellent (green - best)
 * - 60-79: --score-good (blue - good)
 * - 40-59: --score-average (amber - average)
 * - <40: --score-poor (red - poor)
 * - null/undefined: --text-muted (gray - no data)
 */
export function getScoreColor(score?: number | null): string {
  if (score == null) return "var(--text-muted)";
  if (score >= 80) return "var(--score-excellent)";
  if (score >= 60) return "var(--score-good)";
  if (score >= 40) return "var(--score-average)";
  return "var(--score-poor)";
}

/**
 * Get color for return/performance values
 * @param value - Return percentage or null/undefined
 * @returns CSS variable name
 */
export function getReturnColor(value?: number | null): string {
  if (value == null) return "var(--text-muted)";
  if (value >= 0) return "var(--positive)";
  return "var(--negative)";
}

/**
 * Get color for allocation percentages
 * @param allocation - Allocation percentage or null/undefined
 * @returns CSS variable name
 */
export function getAllocationColor(allocation?: number | null): string {
  if (allocation == null) return "var(--text-secondary)";
  if (allocation > 5) return "var(--positive)";
  return "var(--text-secondary)";
}
