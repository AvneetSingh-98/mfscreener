"use client";

import { useState, useEffect } from "react";
import { WeightPreset, WEIGHT_PRESETS } from "@/lib/scoreCalculator";

interface WeightCustomizerProps {
  onWeightsChange: (weights: WeightPreset) => void;
}

export default function WeightCustomizer({ onWeightsChange }: WeightCustomizerProps) {
  const [activePreset, setActivePreset] = useState<string>("balanced");
  const [weights, setWeights] = useState<WeightPreset>(WEIGHT_PRESETS.balanced);
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Track which weights have been manually adjusted (to keep them fixed)
  const [adjustedWeights, setAdjustedWeights] = useState<Set<keyof WeightPreset>>(new Set());

  // Calculate total weight
  const totalWeight = Object.values(weights).reduce((sum, w) => sum + w, 0);
  const isValid = totalWeight === 100;

  // Handle preset selection
  const handlePresetClick = (presetName: string) => {
    setActivePreset(presetName);
    const newWeights = WEIGHT_PRESETS[presetName as keyof typeof WEIGHT_PRESETS];
    setWeights(newWeights);
    setAdjustedWeights(new Set()); // Reset adjusted tracking
    onWeightsChange(newWeights);
  };

  // Handle slider change with smart redistribution
  const handleSliderChange = (category: keyof WeightPreset, newValue: number) => {
    const oldValue = weights[category];
    const delta = newValue - oldValue;

    // Mark this weight as adjusted (locked)
    const newAdjustedWeights = new Set(adjustedWeights);
    newAdjustedWeights.add(category);

    // Get list of weights that can be adjusted (not locked)
    const adjustableCategories = (Object.keys(weights) as Array<keyof WeightPreset>).filter(
      (key) => key !== category && !adjustedWeights.has(key) // Use OLD adjustedWeights, not new
    );

    // If no adjustable categories, constrain to not exceed 100%
    if (adjustableCategories.length === 0) {
      const otherWeightsTotal = Object.keys(weights)
        .filter(key => key !== category)
        .reduce((sum, key) => sum + weights[key as keyof WeightPreset], 0);
      
      const maxAllowed = 100 - otherWeightsTotal;
      const constrainedValue = Math.max(0, Math.min(maxAllowed, newValue));
      
      const newWeights = { ...weights, [category]: constrainedValue };
      setWeights(newWeights);
      setAdjustedWeights(newAdjustedWeights);
      setActivePreset("custom");
      onWeightsChange(newWeights);
      return;
    }

    // Calculate total weight of adjustable categories
    const adjustableTotal = adjustableCategories.reduce((sum, key) => sum + weights[key], 0);

    // Check if we have enough adjustable weight to redistribute
    let actualNewValue = newValue;
    if (delta > 0 && adjustableTotal < delta) {
      // Not enough adjustable weight, constrain the increase
      actualNewValue = oldValue + adjustableTotal;
    }

    const actualDelta = actualNewValue - oldValue;
    
    // Create new weights object
    const newWeights = { ...weights, [category]: actualNewValue };
    
    // Redistribute the delta among adjustable categories
    if (adjustableTotal > 0 && actualDelta !== 0) {
      let remainingDelta = actualDelta;
      
      adjustableCategories.forEach((key, index) => {
        if (index === adjustableCategories.length - 1) {
          // Last category gets the remaining delta to ensure exact 100%
          const adjustment = remainingDelta;
          newWeights[key] = Math.max(0, weights[key] - adjustment);
        } else {
          // Distribute proportionally
          const proportion = weights[key] / adjustableTotal;
          const adjustment = Math.round(actualDelta * proportion);
          newWeights[key] = Math.max(0, weights[key] - adjustment);
          remainingDelta -= adjustment;
        }
      });
    }

    setWeights(newWeights);
    setAdjustedWeights(newAdjustedWeights);
    setActivePreset("custom");
    onWeightsChange(newWeights);
  };

  return (
    <div style={{ 
      marginBottom: 24, 
      padding: 20, 
      border: "1px solid var(--border-default)", 
      borderRadius: 16,
      backgroundColor: "var(--bg-card)",
      fontFamily: "Inter, system-ui, sans-serif",
      boxShadow: "0 4px 6px rgba(0, 0, 0, 0.3)",
    }}>
      {/* Header with Toggle */}
      <div style={{ 
        display: "flex", 
        justifyContent: "space-between", 
        alignItems: "center",
        marginBottom: isExpanded ? 20 : 0
      }}>
        <h3 style={{ margin: 0, fontSize: 14, fontWeight: 700, color: "var(--text-primary)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
          Weight Customizer
        </h3>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          style={{
            padding: "8px 16px",
            fontSize: 13,
            fontWeight: 600,
            border: "1px solid var(--border-default)",
            borderRadius: 12,
            backgroundColor: "var(--bg-card)",
            color: "var(--text-secondary)",
            cursor: "pointer",
            transition: "all 0.2s ease"
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = "var(--border-default)";
            e.currentTarget.style.color = "var(--text-primary)";
            e.currentTarget.style.transform = "translateY(-1px)";
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = "var(--bg-page)";
            e.currentTarget.style.color = "var(--text-secondary)";
            e.currentTarget.style.transform = "translateY(0)";
          }}
        >
          {isExpanded ? "Hide" : "Show"}
        </button>
      </div>

      {isExpanded && (
        <>
          {/* Preset Buttons */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ fontSize: 11, fontWeight: 700, marginBottom: 12, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>
              Presets:
            </div>
            <div style={{ display: "flex", gap: 10 }}>
              {Object.keys(WEIGHT_PRESETS).map((presetName) => {
                const isActive = activePreset === presetName;
                // Color mapping based on preset type
                let activeColor = "var(--bg-page)";
                let activeBg = "var(--positive)";
                let activeBorder = "var(--positive)";
                let inactiveColor = "var(--text-secondary)";
                let inactiveBg = "transparent";
                let inactiveBorder = "var(--border-default)";
                
                if (presetName === "balanced") {
                  activeBg = "var(--positive)";
                  activeBorder = "var(--positive)";
                  activeColor = "var(--bg-page)";
                } else if (presetName === "aggressive") {
                  activeBg = "var(--accent-purple)";
                  activeBorder = "var(--accent-purple)";
                  activeColor = "var(--bg-page)";
                } else if (presetName === "conservative") {
                  activeBg = "var(--warning)";
                  activeBorder = "var(--warning)";
                  activeColor = "var(--bg-page)";
                }
                
                return (
                  <button
                    key={presetName}
                    onClick={() => handlePresetClick(presetName)}
                    style={{
                      padding: "10px 20px",
                      fontSize: 13,
                      fontWeight: isActive ? 700 : 600,
                      border: `1px solid ${isActive ? activeBorder : inactiveBorder}`,
                      borderRadius: 12,
                      backgroundColor: isActive ? activeBg : inactiveBg,
                      color: isActive ? activeColor : inactiveColor,
                      cursor: "pointer",
                      textTransform: "capitalize",
                      transition: "all 0.2s ease"
                    }}
                    onMouseEnter={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.backgroundColor = "var(--bg-card-hover)";
                        e.currentTarget.style.color = "var(--text-primary)";
                        e.currentTarget.style.transform = "translateY(-1px)";
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!isActive) {
                        e.currentTarget.style.backgroundColor = inactiveBg;
                        e.currentTarget.style.color = inactiveColor;
                        e.currentTarget.style.transform = "translateY(0)";
                      }
                    }}
                  >
                    {presetName}
                  </button>
                );
              })}
              {activePreset === "custom" && (
                <div
                  style={{
                    padding: "10px 20px",
                    fontSize: 13,
                    fontWeight: 700,
                    border: "1px solid var(--positive)",
                    borderRadius: 12,
                    backgroundColor: "var(--positive)",
                    color: "var(--bg-page)"
                  }}
                >
                  Custom
                </div>
              )}
            </div>
          </div>

          {/* Sliders */}
          <div style={{ display: "grid", gap: 16 }}>
            {(Object.keys(weights) as Array<keyof WeightPreset>).map((category) => (
              <div key={category}>
                <div style={{ 
                  display: "flex", 
                  justifyContent: "space-between", 
                  marginBottom: 8,
                  fontSize: 12
                }}>
                  <label style={{ 
                    fontWeight: 600, 
                    textTransform: "capitalize",
                    color: adjustedWeights.has(category) ? "var(--accent-teal)" : "var(--text-secondary)"
                  }}>
                    {category.replace(/_/g, " ")}
                    {adjustedWeights.has(category) && " 🔒"}
                  </label>
                  <span style={{ fontWeight: 700, color: "var(--accent-teal)", fontFamily: "'SF Mono', 'Monaco', monospace" }}>
                    {weights[category]}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  step="5"
                  value={weights[category]}
                  onChange={(e) => handleSliderChange(category, parseInt(e.target.value))}
                  style={{
                    width: "100%",
                    height: 6,
                    borderRadius: 3,
                    outline: "none",
                    cursor: "pointer",
                    accentColor: "var(--accent-teal)"
                  }}
                />
              </div>
            ))}
          </div>

          {/* Total Weight Indicator */}
          <div style={{ 
            marginTop: 20, 
            padding: 14, 
            borderRadius: 6,
            backgroundColor: isValid ? "rgba(34, 197, 94, 0.1)" : "rgba(239, 68, 68, 0.1)",
            border: `1px solid ${isValid ? "var(--positive)" : "var(--negative)"}`,
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center"
          }}>
            <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-secondary)" }}>
              Total Weight:
            </span>
            <span style={{ 
              fontSize: 18, 
              fontWeight: 800,
              color: isValid ? "var(--positive)" : "var(--negative)",
              fontFamily: "'SF Mono', 'Monaco', monospace"
            }}>
              {totalWeight}%
            </span>
          </div>

          {adjustedWeights.size > 0 && (
            <div style={{ 
              marginTop: 12, 
              fontSize: 11, 
              color: "var(--text-muted)",
              fontStyle: "italic"
            }}>
              🔒 = Locked (manually adjusted). Other sliders will adjust to maintain 100%.
            </div>
          )}
        </>
      )}
    </div>
  );
}
