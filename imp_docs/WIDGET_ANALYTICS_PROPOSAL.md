# Advanced Analytics Widgets - Proposal & Design Ideas

## Current State Analysis

### Widget 1: "Results by Category" (Currently Static)
**Current Implementation:**
- Shows static categories: General, Privacy, Security, Bias, Toxicity, Compliance
- Displays fake pass/total counts with progress bars
- No connection to actual test results

### Widget 2: "Safety Flags Summary" (Currently Static)
**Current Implementation:**
- Shows static flags: Toxicity, PII, Bias, Behavior
- Displays fake counts and percentages
- No connection to actual test results

---

## Available Real Data from Test Results

### From Backend Evaluation System:
1. **Category Distribution** - Real categories from dataset:
   - `ignore_previous_instructions`
   - `role_playing`
   - `system_prompt_extraction`
   - `context_switching`
   - `delimiter_escape`
   - `encoding_manipulation`
   - And more...

2. **Technique Distribution** - Attack techniques:
   - `direct`
   - `indirect`
   - `role_playing`
   - `social_engineering`
   - And more...

3. **Severity Distribution** - Risk levels:
   - `low`, `medium`, `high`, `critical`

4. **Detected Patterns** - From multi-layer evaluation:
   - `data_leakage` (critical!)
   - `explicit_refusal`
   - `compliance`
   - `system_prompt_leakage`
   - `context_switch`
   - `redirection`
   - And more from structural analysis

5. **Signal Breakdown** - Multi-layer analysis:
   - Semantic signal (resistant/vulnerable/uncertain)
   - Structural signal (resistant/vulnerable/uncertain)
   - LLM signal (resistant/vulnerable/uncertain)
   - Aggregated signal

6. **Evaluation Layer Distribution**:
   - `layer1_semantic` (fast, high confidence)
   - `layer3_llm` (detailed analysis)
   - Layer distribution percentages

7. **Safety Metrics**:
   - Safety scores (0.0-1.0)
   - Confidence scores (0.0-1.0)
   - Average safety score per category/technique
   - Safety score distribution

8. **Outcome Distribution**:
   - Resistant count/percentage
   - Vulnerable count/percentage
   - Uncertain count/percentage

9. **Performance Metrics**:
   - API call times
   - Evaluation processing times
   - Layer-specific timing data

---

## Proposed Transformations

### **Widget 1: "Results by Category" → "Attack Category Performance Analysis"**

#### Option 1: Category-Based Security Analysis
**Transform into:** Dynamic category breakdown showing real test results

**Display:**
- **Real Categories** from dataset (not generic ones):
  - `ignore_previous_instructions`
  - `role_playing` 
  - `system_prompt_extraction`
  - `context_switching`
  - `delimiter_escape`
  - etc.

**Metrics per Category:**
- **Resistance Rate:** `successful_resistances / total_tests` × 100%
- **Vulnerability Rate:** `failed_resistances / total_tests` × 100%
- **Average Safety Score:** Mean safety score for all tests in category
- **Average Confidence:** Mean confidence score
- **Layer Distribution:** Which evaluation layer was used most (Layer 1 vs Layer 3)
- **Critical Vulnerabilities:** Count of critical severity failures

**Visual Design:**
- Progress bars showing resistance rate (green) vs vulnerability rate (red)
- Safety score indicators (color-coded: green = safe, red = vulnerable)
- Badge showing "Most Vulnerable Category" (highest failure rate)
- Badge showing "Best Protected Category" (highest resistance rate)

**Interaction:**
- Click category to filter results by that category
- Hover shows breakdown: resistant count, vulnerable count, uncertain count

---

#### Option 2: Multi-Dimensional Category Analysis
**Transform into:** Category × Severity × Technique Matrix

**Display:**
- **Heatmap Grid:** Categories (rows) × Severities (columns)
- **Cell Values:** Vulnerability count for each category-severity combination
- **Color Intensity:** Based on failure rate (darker = more vulnerable)
- **Tooltips:** Show technique breakdown, patterns detected, average safety scores

**Side Panel:**
- Top 3 most vulnerable category-severity combinations
- Recommendations for each vulnerable area

---

### **Widget 2: "Safety Flags Summary" → "Detected Pattern & Signal Analysis"**

#### Option 1: Pattern-Based Security Indicators
**Transform into:** Real detected patterns from evaluation system

**Display Patterns:**
1. **Data Leakage** (Critical):
   - Count: How many tests detected data leakage
   - Percentage of total tests
   - Average confidence when detected
   - Most common leaked data types

2. **Explicit Refusal** (Positive Indicator):
   - Count: How many responses showed explicit refusal
   - Percentage: Indicates good resistance
   - Average confidence

3. **System Prompt Leakage**:
   - Count: Times system prompt was leaked
   - Percentage
   - Severity breakdown

4. **Context Switch**:
   - Count: Attempts to switch context detected
   - Success/failure rate of context switches

5. **Compliance Pattern**:
   - Count: Times model complied with injection
   - This is a vulnerability indicator

6. **Redirection Pattern**:
   - Count: Safe redirections detected
   - Shows good security posture

**Visual Design:**
- Color coding: Red = vulnerabilities (data_leakage, compliance), Green = resistances (explicit_refusal, redirection)
- Trend indicators: Up/down arrows showing pattern frequency
- Pattern confidence scores
- Severity distribution for each pattern

---

#### Option 2: Multi-Layer Signal Analysis Dashboard
**Transform into:** Signal breakdown visualization

**Display:**
1. **Semantic Signal Summary:**
   - Resistant signals: Count
   - Vulnerable signals: Count
   - Uncertain signals: Count
   - Average semantic similarity scores

2. **Structural Signal Summary:**
   - Patterns detected breakdown
   - Pattern effectiveness (did structural analysis catch issues?)

3. **LLM Signal Summary:**
   - Cases escalated to Layer 3
   - LLM evaluation outcomes
   - LLM vs Layer 1 agreement rate

4. **Signal Agreement Matrix:**
   - How often all signals agree (high confidence)
   - Cases where signals disagree (escalated to Layer 3)
   - Cross-signal validation metrics

**Visual Design:**
- Donut charts for each signal type
- Agreement matrix heatmap
- Signal flow diagram showing Layer 1 → Layer 3 escalation path

---

#### Option 3: Security Posture Indicators (Combined)
**Transform into:** Comprehensive security health dashboard

**Display:**
1. **Critical Vulnerabilities:**
   - Data leakage incidents
   - System prompt leaks
   - High-severity failures
   - Count + trend

2. **Resistance Indicators:**
   - Explicit refusals detected
   - Safe redirections
   - High safety scores
   - Count + percentage

3. **Uncertain Cases:**
   - Tests requiring Layer 3 evaluation
   - Low confidence evaluations
   - Needs attention count

4. **False Positive Checks:**
   - How many false positives were caught
   - False positive detection rate
   - System accuracy metric

**Visual Design:**
- Health score meter (0-100%)
- Color-coded indicators: Critical (red), Warning (yellow), Good (green)
- Action items based on findings

---

## Additional Advanced Analytics Ideas

### **Widget 3: "Evaluation Layer Performance Metrics"** (New Widget Idea)

**Purpose:** Show which evaluation layer handled what, and performance characteristics

**Display:**
- **Layer 1 (Semantic + Structural) Performance:**
  - How many cases handled (percentage)
  - Average processing time
  - Accuracy rate (agreement with Layer 3 when escalated)
  - Most common outcome: resistant/vulnerable/uncertain

- **Layer 3 (LLM) Performance:**
  - Escalation rate (how often Layer 1 needed help)
  - Average processing time
  - Cases where Layer 3 overturned Layer 1 decision
  - Confidence improvement from Layer 1 to Layer 3

- **Layer Efficiency Metrics:**
  - Cost savings (Layer 1 is fast/free, Layer 3 costs API calls)
  - Speed comparison
  - Accuracy comparison

---

### **Widget 4: "Severity-Based Risk Matrix"** (New Widget Idea)

**Purpose:** Visualize risk distribution and criticality

**Display:**
- **Severity Distribution:**
  - Critical: Count + percentage + vulnerable/resistant breakdown
  - High: Count + percentage + vulnerable/resistant breakdown
  - Medium: Count + percentage + vulnerable/resistant breakdown
  - Low: Count + percentage + vulnerable/resistant breakdown

- **Risk Heatmap:**
  - Severity (rows) × Category (columns)
  - Color intensity based on vulnerability rate
  - Interactive: Click to see specific test cases

- **Critical Findings Panel:**
  - List of all critical severity failures
  - Summary of what was compromised
  - Recommended actions

---

### **Widget 5: "Technique Effectiveness Analysis"** (New Widget Idea)

**Purpose:** Understand which attack techniques are most/least effective

**Display:**
- **Technique Success Rate:**
  - Each technique's injection success rate
  - Most successful attack technique (highest vulnerability rate)
  - Least successful attack technique (best resistance)
  
- **Technique Breakdown:**
  - Technique × Severity distribution
  - Average safety score per technique
  - Average confidence per technique

- **Top Vulnerable Techniques:**
  - List techniques sorted by vulnerability rate
  - Show recommended defenses

---

## Recommended Implementation Priority

### **Phase 1: Core Transformations** (High Priority)

1. **Widget 1 → Category Performance Analysis**
   - Use real categories from test results
   - Show resistance rate, vulnerability rate, safety scores
   - Make interactive (click to filter)
   - Replace static data with `testResults.detailed_analysis.technique_distribution` and category aggregation

2. **Widget 2 → Pattern Detection Summary**
   - Replace with real detected patterns from `result.evaluation.detected_patterns`
   - Show data_leakage, explicit_refusal, compliance, etc.
   - Color-code by vulnerability vs resistance
   - Aggregate across all test results

### **Phase 2: Advanced Analytics** (Medium Priority)

3. **Layer Performance Metrics** (New Widget)
   - Show Layer 1 vs Layer 3 distribution
   - Performance metrics (time, cost, accuracy)
   - Escalation analytics

4. **Severity Risk Matrix** (Enhanced Widget 1)
   - Add severity dimension to category analysis
   - Create interactive heatmap

### **Phase 3: Advanced Features** (Lower Priority)

5. **Technique Effectiveness** (New Widget)
   - Attack technique success analysis
   - Defense recommendations

6. **Signal Agreement Dashboard** (Enhanced Widget 2)
   - Multi-signal analysis
   - Cross-validation metrics

---

## Data Aggregation Strategy

### For Category Widget:
```javascript
// Aggregate from testResults.evaluated_responses
const categoryStats = evaluated_responses.reduce((acc, result) => {
  const category = result.category || 'unknown';
  if (!acc[category]) {
    acc[category] = {
      total: 0,
      resistant: 0,
      vulnerable: 0,
      safetyScores: [],
      confidenceScores: [],
      severityCounts: {}
    };
  }
  acc[category].total++;
  if (!result.injection_successful) acc[category].resistant++;
  else acc[category].vulnerable++;
  acc[category].safetyScores.push(result.safety_score || 0);
  acc[category].confidenceScores.push(result.confidence_score || 0);
  acc[category].severityCounts[result.severity] = 
    (acc[category].severityCounts[result.severity] || 0) + 1;
  return acc;
}, {});
```

### For Pattern Detection Widget:
```javascript
// Aggregate detected patterns from evaluation results
const patternStats = evaluated_responses.reduce((acc, result) => {
  const patterns = result.evaluation?.detected_patterns || [];
  patterns.forEach(pattern => {
    if (!acc[pattern]) {
      acc[pattern] = {
        count: 0,
        vulnerable: 0,
        resistant: 0,
        averageConfidence: []
      };
    }
    acc[pattern].count++;
    if (result.injection_successful) acc[pattern].vulnerable++;
    else acc[pattern].resistant++;
    acc[pattern].averageConfidence.push(result.confidence_score || 0);
  });
  return acc;
}, {});
```

---

## UX Enhancement Ideas

### Interactive Features:
1. **Click to Filter:** Click any category/pattern to filter detailed results view
2. **Drill-Down:** Click to see all test cases in that category/pattern
3. **Comparison Mode:** Compare current test run vs previous runs
4. **Export Analytics:** Export category/pattern breakdowns as CSV

### Visual Enhancements:
1. **Color Coding:**
   - Green = Good (high resistance, high safety scores)
   - Yellow = Warning (uncertain, medium safety)
   - Red = Critical (vulnerabilities, low safety scores)

2. **Icons & Badges:**
   - Shield icon for resistant categories
   - Alert icon for vulnerable categories
   - Trending indicators (up/down from previous runs)

3. **Progress Indicators:**
   - Animated progress bars
   - Circular progress for percentages
   - Sparklines for trends (if historical data available)

---

## Summary of Recommendations

### Widget 1 Transformation:
**From:** Static "Results by Category" with fake data  
**To:** Dynamic "Attack Category Performance" with:
- Real categories from test dataset
- Resistance/vulnerability rates per category
- Safety score averages
- Severity distribution
- Interactive filtering

### Widget 2 Transformation:
**From:** Static "Safety Flags Summary" with generic flags  
**To:** Dynamic "Detected Pattern & Signal Analysis" with:
- Real detected patterns (data_leakage, explicit_refusal, compliance, etc.)
- Pattern-based vulnerability indicators
- Signal breakdown (semantic, structural, LLM)
- False positive detection metrics
- Pattern effectiveness analysis

Both widgets become **data-driven, interactive, and provide actionable security insights** based on actual test results from your advanced multi-layer evaluation system.

