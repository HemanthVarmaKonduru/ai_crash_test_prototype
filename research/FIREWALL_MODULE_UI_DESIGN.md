# Firewall Module UI/UX Design Document

## 📋 Document Purpose

This document provides comprehensive design specifications for the **Firewall Module** - a new post-deployment production guardrail system for the Evalence AI Security Testing Platform. This document is intended for frontend development agents to implement the UI components and pages.

---

## 🎯 Project Context

### What We're Building

We are adding a **Firewall Module** to the existing Evalence platform. This module provides **real-time production protection** for AI applications, evaluating and blocking threats as they occur in production environments.

### Platform Structure

- **Pre-Deployment (Existing)**: Testing modules (Prompt Injection, Jailbreak, Data Extraction, Adversarial)
- **Post-Deployment (New)**: Firewall module with 6 sub-modules for real-time protection

### Technology Stack Reference

- **Framework**: Next.js 15.2.4 (App Router)
- **Language**: TypeScript
- **UI Library**: shadcn/ui components (already in use)
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **State**: React Hooks

### Existing Codebase Patterns

**Reference Files for Patterns**:
- Layout: `frontend/app/dashboard/layout.tsx`
- Example Page: `frontend/app/dashboard/prompt-injection/page.tsx`
- Dashboard: `frontend/app/dashboard/page.tsx`
- Components: `frontend/components/ui/*`
- API Config: `frontend/lib/api-config.ts`

**Key Design Patterns to Follow**:
- Card-based layouts with gradient backgrounds
- Stat cards with icons and trend indicators
- Tables with sorting and filtering
- Dialog modals for detailed views
- Tabs for organizing content
- Real-time data polling (2-second intervals)
- Progress indicators for loading states

---

## 📁 File Structure Requirements

### New Files to Create

```
frontend/
├── app/
│   └── dashboard/
│       └── firewall/
│           ├── page.tsx                    # Main firewall dashboard
│           ├── input-guardrails/
│           │   ├── page.tsx
│           │   └── loading.tsx
│           ├── output-evaluation/
│           │   ├── page.tsx
│           │   └── loading.tsx
│           ├── threat-intelligence/
│           │   ├── page.tsx
│           │   └── loading.tsx
│           ├── incident-response/
│           │   ├── page.tsx
│           │   └── loading.tsx
│           └── analytics/
│               ├── page.tsx
│               └── loading.tsx
├── components/
│   └── firewall/
│       ├── SecurityScoreWidget.tsx
│       ├── RealTimeFeed.tsx
│       ├── ThreatChart.tsx
│       ├── DetectionRulesPanel.tsx
│       ├── EvaluationRulesPanel.tsx
│       ├── IncidentList.tsx
│       ├── IncidentDetails.tsx
│       └── MetricsDashboard.tsx
└── lib/
    └── api-config.ts                       # Update with firewall endpoints
```

### Sidebar Navigation Update

**File**: `frontend/app/dashboard/layout.tsx`

**Action Required**: Add a new sidebar section titled "Firewall (Production)" with the following menu items:

1. **Firewall Dashboard** - Icon: Shield or Firewall icon, URL: `/dashboard/firewall`
2. **Input Guardrails** - Icon: ShieldCheck, URL: `/dashboard/firewall/input-guardrails`
3. **Output Evaluation** - Icon: FileCheck, URL: `/dashboard/firewall/output-evaluation`
4. **Threat Intelligence** - Icon: Brain, URL: `/dashboard/firewall/threat-intelligence`
5. **Incident Response** - Icon: AlertTriangle, URL: `/dashboard/firewall/incident-response`
6. **Analytics** - Icon: BarChart3, URL: `/dashboard/firewall/analytics`

Place this section **after** the "Attack Modules" section in the sidebar.

### API Configuration Update

**File**: `frontend/lib/api-config.ts`

**Action Required**: Add firewall endpoints to `apiConfig.endpoints`:

```typescript
firewall: {
  overview: `${API_URL}/api/v1/firewall/overview`,
  stats: `${API_URL}/api/v1/firewall/stats`,
  evaluateInput: `${API_URL}/api/v1/firewall/evaluate/input`,
  evaluateOutput: `${API_URL}/api/v1/firewall/evaluate/output`,
  inputRules: `${API_URL}/api/v1/firewall/rules/input`,
  outputRules: `${API_URL}/api/v1/firewall/rules/output`,
  blockedInputs: `${API_URL}/api/v1/firewall/blocked/inputs`,
  blockedOutputs: `${API_URL}/api/v1/firewall/blocked/outputs`,
  threats: `${API_URL}/api/v1/firewall/threats`,
  patterns: `${API_URL}/api/v1/firewall/patterns`,
  incidents: `${API_URL}/api/v1/firewall/incidents`,
  incidentDetails: (id: string) => `${API_URL}/api/v1/firewall/incidents/${id}`,
  analytics: `${API_URL}/api/v1/firewall/analytics`,
  metrics: `${API_URL}/api/v1/firewall/metrics`,
}
```

---

## 🎨 Design System Reference

### Color System

**Use existing color variables**:
- Primary: `hsl(var(--primary))` - Blue for security
- Destructive: `hsl(var(--destructive))` - Red for blocked/critical
- Success: Green-500 - For allowed/safe
- Warning: Yellow-500 - For caution
- Danger: Red-500 - For critical/blocked

**Gradient Patterns** (from existing code):
- `bg-gradient-to-br from-blue-500/10 to-transparent border-blue-500/20`
- `bg-gradient-to-br from-green-500/10 to-transparent border-green-500/20`
- `bg-gradient-to-br from-red-500/10 to-transparent border-red-500/20`
- `bg-gradient-to-br from-yellow-500/10 to-transparent border-yellow-500/20`

### Typography

- **H1**: `text-3xl font-bold tracking-tight`
- **H2**: `text-xl font-semibold`
- **H3**: `text-lg font-semibold`
- **Body**: `text-sm` or `text-base`
- **Muted**: `text-muted-foreground`
- **Monospace**: `font-mono text-sm` (for IDs, timestamps)

### Spacing

- **Page padding**: `p-4 md:p-6`
- **Section gap**: `gap-6`
- **Card gap**: `gap-4`
- **Element gap**: `gap-2`

### Component Patterns

**Follow existing patterns from**:
- `frontend/app/dashboard/prompt-injection/page.tsx` - For page structure
- `frontend/app/dashboard/page.tsx` - For stat cards
- `frontend/app/dashboard/layout.tsx` - For navigation

---

## 📊 Module 1: Firewall Dashboard

### Route
`/dashboard/firewall`

### Purpose
Main overview dashboard showing real-time firewall status, key metrics, and quick access to all firewall modules.

### Layout Structure

1. **Header Section**
   - Title: "Firewall Dashboard"
   - Icon: Shield (size-6, text-primary)
   - Status badge: "Active" with green pulsing dot
   - Description: "Real-time security monitoring and threat protection for your AI applications"

2. **Key Metrics Row** (4 columns, grid layout)
   - Security Score Widget
   - Real-Time Request Counter
   - Blocked Requests Widget
   - Average Latency Widget

3. **Real-Time Threat Feed Card**
   - Title: "Real-Time Threat Feed"
   - Description: "Live security events and blocked threats"
   - Controls: Pause/Resume button, Severity filter dropdown
   - Content: Scrollable list (max-height: 400px) of threat cards
   - Auto-refresh: Every 2 seconds

4. **Charts Row** (2 columns)
   - Threat Trends Chart (left)
   - Module Status Grid (right)

### Widget Specifications

#### Widget 1: Security Score Widget

**Visual Design**:
- Large circular progress indicator (radius: 80px, stroke-width: 8px)
- Score displayed in center (0-100 with % sign)
- Color coding:
  - Green: 90-100
  - Yellow: 70-89
  - Orange: 50-69
  - Red: <50
- Trend indicator below (↑/↓ arrow with percentage change)
- Label: "Security Score"

**Data Required**:
- `score`: number (0-100)
- `change`: number (percentage change from last hour)
- `trend`: "up" | "down"
- `breakdown`: { input: number, output: number, threatIntel: number } (optional)

**Interactions**:
- Click to view detailed breakdown in dialog
- Hover shows tooltip with sub-scores

#### Widget 2: Real-Time Request Counter

**Visual Design**:
- Large number (formatted with commas)
- Small sparkline chart below (last 60 minutes, height: 32px)
- Status indicator dot (green/yellow/red based on RPM)
- Subtext: "{RPM} req/min"
- Label: "Requests (Last Hour)"
- Icon: Activity (size-8, opacity-50, indigo-500)

**Data Required**:
- `requestCount`: number (total requests in last hour)
- `rpm`: number (requests per minute)
- `sparklineData`: Array<{ time: string, value: number }>
- `status`: "normal" | "high" | "critical"

**Interactions**:
- Click to view detailed request analytics
- Hover shows time breakdown

#### Widget 3: Blocked Requests Widget

**Visual Design**:
- Large number in red (text-red-600)
- Block rate percentage below
- Top 3 block reasons listed (with colored dots)
- Alert badge if spike detected
- Label: "Blocked Today"
- Icon: Shield (size-8, opacity-50, red-500)

**Data Required**:
- `blockedCount`: number
- `blockRate`: number (percentage)
- `breakdown`: Array<{ type: string, count: number }>
- `spikeDetected`: boolean

**Interactions**:
- Click to view blocked requests log
- Hover shows full breakdown

#### Widget 4: Average Latency Widget

**Visual Design**:
- Large number with "ms" unit
- Color coding: Green (<50ms), Yellow (50-100ms), Red (>100ms)
- Target indicator: "<50ms"
- P95 and P99 indicators below
- Label: "Avg Latency"
- Icon: Clock (size-8, opacity-50, yellow-500)

**Data Required**:
- `avgLatency`: number (milliseconds)
- `p95`: number
- `p99`: number
- `target`: number (50ms)

**Interactions**:
- Click to view latency breakdown
- Hover shows percentile distribution

#### Widget 5: Real-Time Threat Feed

**Component**: `RealTimeFeed.tsx`

**Visual Design**:
- Scrollable list container (max-height: 400px)
- Each threat as a card with:
  - Severity badge (color-coded)
  - Threat type
  - Description (truncated)
  - Timestamp (relative or formatted)
  - Action badge (blocked/allowed/sanitized)
  - Confidence percentage
- Color-coded borders based on severity
- Hover effect: background change

**Data Required**:
- `threats`: Array<Threat>
- `paused`: boolean
- `severityFilter`: string

**Interactions**:
- Click threat card to view details in dialog
- Pause/resume button toggles auto-refresh
- Severity filter dropdown
- Auto-scroll to top when new threats arrive

**Threat Interface**:
```typescript
interface Threat {
  id: string;
  type: string;
  severity: "critical" | "high" | "medium" | "low";
  description: string;
  timestamp: string;
  action: "blocked" | "allowed" | "sanitized";
  confidence: number;
}
```

#### Widget 6: Threat Trends Chart

**Visual Design**:
- Multi-line chart (Recharts LineChart)
- Three lines: Total threats, Blocked, Allowed
- Time range selector dropdown (1h, 6h, 24h, 7d, 30d)
- Interactive tooltips
- X-axis: Time (formatted)
- Y-axis: Count
- Legend at top

**Data Required**:
- `chartData`: Array<{ time: string, total: number, blocked: number, allowed: number }>
- `timeRange`: string

**Interactions**:
- Hover for detailed point data
- Click to zoom into time period
- Time range selector updates chart

#### Widget 7: Module Status Grid

**Visual Design**:
- Grid of 5 cards (2 columns on desktop, 1 on mobile)
- Each card shows:
  - Module icon (size-10, rounded-lg background)
  - Module name
  - Status indicator (green/yellow/red dot)
  - Quick stats (3 columns: Today, Blocked, Latency)
  - ChevronRight icon indicating clickable
- Hover effect: border color change

**Data Required**:
- `modules`: Array<Module>

**Module Interface**:
```typescript
interface Module {
  id: string;
  title: string;
  icon: LucideIcon;
  url: string;
  status: "active" | "inactive" | "error";
  todayCount: number;
  blockedCount: number;
  avgLatency: number;
  iconColor: string;
}
```

**Interactions**:
- Click card to navigate to module page
- Status dot indicates module health

---

## 🛡️ Module 2: Input Guardrails

### Route
`/dashboard/firewall/input-guardrails`

### Purpose
Evaluate user prompts BEFORE sending to LLM. Block malicious inputs in real-time.

### Layout Structure

1. **Header Section**
   - Title: "Input Guardrails"
   - Icon: ShieldCheck
   - Status badge: Active/Inactive
   - Description: "Evaluate user prompts before sending to LLM. Block malicious inputs in real-time."

2. **Statistics Cards Row** (4 columns)
   - Blocked Today
   - Allowed Today
   - Pending Queue
   - Latency Average

3. **Tabs Navigation**
   - Tabs: All Threats, Prompt Injection, Jailbreak, PII
   - Each tab shows filtered content

4. **Content Area** (2 columns)
   - Left: Detection Rules Configuration Panel
   - Right: Recent Blocks Live Feed

### Widget Specifications

#### Widget 1: Detection Statistics Cards

**Blocked Today Card**:
- Large number in red
- Block rate percentage
- Top 3 block reasons (with dots)
- Alert badge if spike
- Icon: Shield (red-500)

**Allowed Today Card**:
- Large number in green
- Percentage of total
- False positive count (if > 0)
- Icon: CheckCircle2 (green-500)

**Pending Queue Card**:
- Queue size number
- Average wait time
- Processing rate
- Icon: Clock (yellow-500)

**Latency Average Card**:
- Average evaluation time
- P95 latency
- Target indicator
- Icon: Clock (yellow-500)

#### Widget 2: Detection Rules Configuration Panel

**Component**: `DetectionRulesPanel.tsx`

**Visual Design**:
- Accordion-based layout
- Each rule in expandable section
- Toggle switch for enable/disable
- Slider for block threshold (0-100%)
- Dropdown for action (Block/Allow/Log)
- Radio buttons for layer selection (Layer 1, Layer 3, Both)
- Impact preview box showing estimated effects

**Rules to Include**:
1. **Prompt Injection Detection**
   - Enable toggle
   - Block threshold slider
   - Action dropdown
   - Layer selection

2. **Jailbreak Detection**
   - Same controls as above

3. **PII Detection**
   - Enable toggle
   - Action dropdown (Block/Sanitize/Log)
   - PII types checkboxes (SSN, Credit Card, Email, Phone, etc.)

4. **Rate Limiting**
   - Enable toggle
   - Requests per minute input
   - Action dropdown (Block/Throttle)

**Interactions**:
- Real-time preview of rule impact
- Test rule button (optional)
- Save/Cancel buttons at top
- Changes highlighted until saved

#### Widget 3: Recent Blocks Live Feed

**Visual Design**:
- Table with sortable columns
- Auto-refresh every 2 seconds
- Search bar (by user ID or prompt text)
- Severity filter dropdown
- Color-coded rows by severity
- Expandable rows for details

**Table Columns**:
- Timestamp (with clock icon)
- Threat Type (badge)
- Severity (color-coded badge)
- Confidence (percentage with progress bar)
- Action (badge: blocked/allowed)
- User ID (monospace, optional)
- Actions (eye icon button)

**Interactions**:
- Click row to expand details
- Filter by severity
- Search functionality
- Export filtered results button

---

## ✅ Module 3: Output Evaluation

### Route
`/dashboard/firewall/output-evaluation`

### Purpose
Evaluate LLM responses AFTER generation. Detect unsafe or low-quality content.

### Layout Structure

1. **Header Section**
   - Title: "Output Evaluation"
   - Icon: FileCheck
   - Status badge
   - Description: "Evaluate LLM responses after generation. Detect unsafe or low-quality content."

2. **Statistics Cards Row** (4 columns)
   - Blocked Today
   - Sanitized Today (NEW - unique to output)
   - Allowed Today
   - Latency Average

3. **Tabs Navigation**
   - Tabs: All, Security, Content Safety, Quality, Compliance

4. **Content Area** (2 columns)
   - Left: Evaluation Rules Configuration Panel
   - Right: Recent Evaluations Feed

### Widget Specifications

#### Widget 1: Evaluation Statistics Cards

**Sanitized Today Card** (Unique to Output):
- Large number in orange
- Number of sanitization methods used
- "Preview sanitizations" button
- Icon: FileCheck (orange-500)

**Other cards**: Similar to Input Guardrails

#### Widget 2: Evaluation Rules Configuration Panel

**Component**: `EvaluationRulesPanel.tsx`

**Visual Design**: Similar to DetectionRulesPanel but with different categories:

**Categories**:
1. **Security Validation**
   - Data leakage detection
   - Prompt injection success detection
   - Jailbreak success detection

2. **Content Safety**
   - Toxicity detection (threshold slider)
   - Bias detection (threshold slider)
   - Hate speech detection (threshold slider)

3. **Quality Control**
   - Hallucination detection (threshold slider)
   - Coherence check (toggle)
   - Relevance validation (toggle)

4. **Compliance**
   - GDPR compliance (toggle)
   - HIPAA compliance (toggle)
   - Custom policies (add/edit buttons)

**Each rule has**:
- Enable toggle
- Threshold slider (where applicable)
- Action dropdown (Block/Sanitize/Flag/Log)
- Impact preview

#### Widget 3: Recent Evaluations Feed

**Visual Design**: Similar to Recent Blocks Feed but with different columns:

**Table Columns**:
- Timestamp
- Issue Type (Security/Content Safety/Quality/Compliance)
- Severity
- Confidence
- Action (Blocked/Sanitized/Allowed)
- Safety Score (with progress bar)
- Actions (view details button)

#### Widget 4: Safety Score Distribution Chart

**Visual Design**:
- Histogram (Bar chart)
- X-axis: Safety score ranges (0-20, 20-40, 40-60, 60-80, 80-100)
- Y-axis: Count
- Color gradient: Red (low) to Green (high)
- Vertical line overlay: Block threshold
- Statistics below: Average, Median, Below Threshold

**Data Required**:
- `distributionData`: Array<{ range: string, count: number, midpoint: number }>
- `threshold`: number
- `avgSafetyScore`: number
- `medianSafetyScore`: number
- `belowThreshold`: number

#### Widget 5: Sanitization Preview Widget

**Component**: `SanitizationPreview.tsx`

**Visual Design**:
- Dialog modal (max-width: 4xl)
- Tabs: Side by Side, Diff View
- Side by Side: Two cards showing original vs sanitized
- Diff View: Highlighted changes
- Changes summary section
- Copy sanitized button

**Data Required**:
- `originalResponse`: string
- `sanitizedResponse`: string
- `changes`: Array<{ type: string, description: string }>

---

## 🧠 Module 4: Threat Intelligence

### Route
`/dashboard/firewall/threat-intelligence`

### Purpose
Analyze threat patterns, detect new attack vectors, maintain threat database.

### Layout Structure

1. **Header Section**
   - Title: "Threat Intelligence"
   - Icon: Brain
   - Last updated timestamp
   - Description: "Threat pattern detection and attack vector analysis"

2. **Statistics Cards Row** (4 columns)
   - Active Threats
   - New Threats (last 24h)
   - Patterns Detected
   - Database Size

3. **Tabs Navigation**
   - Tabs: Threat Patterns, Attack Vectors, Threat Database

4. **Content Area**
   - Pattern Detection Panel
   - Threat Timeline Chart

### Widget Specifications

#### Widget 1: Threat Pattern Detection Panel

**Visual Design**:
- Grid of pattern cards (3 columns)
- Each card shows:
  - Pattern name (title)
  - Description
  - Occurrences count
  - Confidence score
  - Frequency (per hour)
  - First seen / Last seen dates
  - Severity badge
- Confidence filter dropdown
- Click card to view pattern details

**Data Required**:
- `patterns`: Array<Pattern>

**Pattern Interface**:
```typescript
interface Pattern {
  id: string;
  name: string;
  description: string;
  count: number;
  confidence: number;
  frequency: number;
  firstSeen: string;
  lastSeen: string;
  severity: "critical" | "high" | "medium" | "low";
}
```

#### Widget 2: Threat Timeline Chart

**Visual Design**:
- Scatter plot or timeline visualization
- X-axis: Time
- Y-axis: Severity (0-4 scale)
- Points color-coded by severity
- Interactive tooltips
- Time range selector

**Data Required**:
- `timelineData`: Array<{ time: number, severity: number, threatType: string, confidence: number }>
- `timeRange`: string

#### Widget 3: Threat Database Browser

**Visual Design**:
- Searchable, sortable table
- Columns: Threat ID, Name, Type, Severity, First Seen, Last Seen, Occurrences, Status
- Filter by type/severity
- Export button

---

## 🚨 Module 5: Incident Response

### Route
`/dashboard/firewall/incident-response`

### Purpose
Manage security incidents, track response times, handle remediation.

### Layout Structure

1. **Header Section**
   - Title: "Incident Response"
   - Icon: AlertTriangle
   - Active incidents count badge
   - Description: "Manage and respond to security incidents"

2. **Statistics Cards Row** (4 columns)
   - Active Incidents
   - Resolved Today
   - Response Time (avg)
   - Resolution Time (avg)

3. **Tabs Navigation**
   - Tabs: Active (with count badge), Resolved, All

4. **Content Area** (3 columns)
   - Left (2 cols): Incident List Table
   - Right (1 col): Incident Details Panel

### Widget Specifications

#### Widget 1: Incident List Table

**Component**: `IncidentList.tsx`

**Visual Design**:
- Sortable table
- Search bar
- Status filter dropdown
- Color-coded rows by severity
- Click row to select and show in details panel

**Table Columns**:
- Incident ID (monospace)
- Type (badge)
- Severity (color-coded badge)
- Status (badge: new/assigned/in-progress/resolved)
- Detected At (timestamp)
- Response Time (minutes or "N/A")
- Assigned To (name or "Unassigned" badge)
- Actions (dropdown menu)

**Actions Menu**:
- Assign to me
- Mark in progress
- Resolve
- View details

#### Widget 2: Incident Details Panel

**Component**: `IncidentDetails.tsx`

**Visual Design**:
- Fixed side panel or expandable card
- Sections:
  1. **Overview**: ID, Type, Severity, Status, Detected At, Resolved At
  2. **Threat Details**: Type, Description, Confidence
  3. **Impact Analysis**: Affected systems, User impact, Data exposure
  4. **Response Actions**: Buttons for assign, update status, resolve
  5. **Timeline**: Vertical timeline of events
  6. **Notes**: Text area for notes

**Timeline Visualization**:
- Vertical timeline
- Events as nodes
- Color-coded by event type
- Timestamp and user for each event

**Interactions**:
- Assign incident button
- Update status dropdown
- Resolve button
- Add note textarea
- Timeline expandable

---

## 📈 Module 6: Monitoring & Analytics

### Route
`/dashboard/firewall/analytics`

### Purpose
Comprehensive analytics, performance monitoring, compliance reporting.

### Layout Structure

1. **Header Section**
   - Title: "Monitoring & Analytics"
   - Icon: BarChart3
   - Date range picker (Last 7 days default)
   - Description: "Comprehensive analytics and performance monitoring"

2. **Key Metrics Cards Row** (4 columns)
   - Total Requests
   - Block Rate
   - False Positive Rate
   - Average Latency

3. **Tabs Navigation**
   - Tabs: Overview, Performance, Security, Compliance

4. **Content Area**
   - Charts and analytics widgets
   - Custom report builder

### Widget Specifications

#### Widget 1: Request Volume Chart

**Visual Design**:
- Area chart
- X-axis: Time
- Y-axis: Request count
- Time range selector
- Peak times highlighted

#### Widget 2: Latency Distribution Chart

**Visual Design**:
- Histogram
- P50, P95, P99 markers
- Target line overlay
- Color gradient

#### Widget 3: Threat Distribution Chart

**Visual Design**:
- Pie chart by threat type
- Stacked bar by severity
- Interactive tooltips

#### Widget 4: Compliance Dashboard

**Visual Design**:
- Compliance score (circular progress)
- Breakdown by regulation
- Policy violations table
- Audit trail table

#### Widget 5: Custom Report Builder

**Visual Design**:
- Drag-and-drop interface
- Widget selection panel
- Date range picker
- Filter builder
- Preview area
- Export options (PDF, CSV, JSON)

---

## 🎨 Design Criteria & Best Practices

### Visual Design Requirements

1. **Color System**
   - Use existing CSS variables
   - Green for success/allowed
   - Red for blocked/critical
   - Yellow for warning
   - Blue for primary actions

2. **Typography**
   - Follow existing heading hierarchy
   - Use monospace for IDs and timestamps
   - Consistent font sizes

3. **Spacing**
   - Page: `p-4 md:p-6`
   - Sections: `gap-6`
   - Cards: `gap-4`
   - Elements: `gap-2`

4. **Component Styling**
   - Use gradient backgrounds for stat cards
   - Glass effects where appropriate
   - Consistent border colors
   - Hover states on interactive elements

### Interaction Requirements

1. **Real-Time Updates**
   - Poll API every 2 seconds for live data
   - Show loading states during updates
   - Pause/resume controls for feeds
   - Smooth transitions

2. **User Feedback**
   - Toast notifications for actions
   - Loading skeletons
   - Error states
   - Empty states

3. **Navigation**
   - Breadcrumbs in header
   - Sidebar navigation
   - Tab navigation within modules
   - Back buttons where needed

4. **Data Presentation**
   - Progressive disclosure (expandable rows)
   - Modal dialogs for details
   - Tooltips for additional info
   - Search and filter functionality

### Performance Requirements

1. **Loading**
   - Skeleton screens for initial load
   - Progressive loading for charts
   - Lazy loading where possible

2. **Real-Time**
   - Efficient polling (2-5 second intervals)
   - WebSocket support (if available)
   - Debounced search/filter

3. **Optimization**
   - Virtual scrolling for long lists
   - Pagination for tables
   - Memoization for expensive calculations

### Responsiveness Requirements

1. **Breakpoints**
   - Mobile: Single column layouts
   - Tablet: 2 columns
   - Desktop: 3-4 columns

2. **Adaptive Elements**
   - Collapsible sections on mobile
   - Horizontal scroll for tables
   - Stacked cards on mobile

3. **Touch Targets**
   - Minimum 44x44px for buttons
   - Adequate spacing between clickable elements

### Accessibility Requirements

1. **Keyboard Navigation**
   - Tab order logical
   - Focus indicators visible
   - Keyboard shortcuts where appropriate

2. **Screen Readers**
   - ARIA labels on icons
   - Semantic HTML
   - Alt text for charts (descriptions)

3. **Color Contrast**
   - WCAG AA compliance
   - Don't rely solely on color for information
   - Text alternatives for color coding

---

## 🔧 Implementation Guidelines

### 1. Follow Existing Patterns

**Study these files**:
- `frontend/app/dashboard/prompt-injection/page.tsx` - Complete page example
- `frontend/app/dashboard/page.tsx` - Dashboard layout and stat cards
- `frontend/app/dashboard/layout.tsx` - Sidebar navigation structure

### 2. Component Imports

**Use existing shadcn/ui components**:
- Card, CardHeader, CardTitle, CardDescription, CardContent
- Button, Badge, Table, Tabs, Dialog, Progress, Switch, Slider
- Select, Input, Label, Accordion, ScrollArea, Separator

### 3. Icons

**Use Lucide React icons**:
- Shield, ShieldCheck, FileCheck, AlertTriangle, CheckCircle2
- XCircle, TrendingUp, TrendingDown, Activity, Clock, Eye
- Download, Copy, Play, Pause, MoreVertical, User, Brain
- BarChart3, Target, Zap, FileText, Settings, Home

### 4. State Management

**Use React Hooks**:
- `useState` for local state
- `useEffect` for data fetching and polling
- `useRouter` for navigation
- `usePathname` for active route detection

### 5. Data Fetching Pattern

**Follow existing pattern**:
```typescript
// Polling pattern (from prompt-injection page)
useEffect(() => {
  const interval = setInterval(async () => {
    const response = await fetch(apiConfig.endpoints.firewall.stats);
    const data = await response.json();
    setStats(data);
  }, 2000);
  return () => clearInterval(interval);
}, []);
```

### 6. Error Handling

- Show error states in UI
- Toast notifications for errors
- Fallback to empty states
- Retry mechanisms

### 7. Loading States

- Skeleton screens for initial load
- Spinners for actions
- Progress bars for long operations
- Disabled states during operations

---

## 📋 Implementation Checklist

### Phase 1: Core Dashboard
- [ ] Create `/dashboard/firewall/page.tsx`
- [ ] Implement Security Score Widget
- [ ] Implement Real-Time Request Counter
- [ ] Implement Blocked Requests Widget
- [ ] Implement Average Latency Widget
- [ ] Implement Real-Time Threat Feed
- [ ] Implement Threat Trends Chart
- [ ] Implement Module Status Grid
- [ ] Update sidebar navigation

### Phase 2: Input Guardrails
- [ ] Create `/dashboard/firewall/input-guardrails/page.tsx`
- [ ] Implement Detection Statistics Cards
- [ ] Implement Detection Rules Panel component
- [ ] Implement Recent Blocks Feed
- [ ] Add tabs for threat types
- [ ] Implement filtering and search

### Phase 3: Output Evaluation
- [ ] Create `/dashboard/firewall/output-evaluation/page.tsx`
- [ ] Implement Evaluation Statistics Cards
- [ ] Implement Evaluation Rules Panel component
- [ ] Implement Recent Evaluations Feed
- [ ] Implement Safety Score Distribution Chart
- [ ] Implement Sanitization Preview component
- [ ] Add tabs for issue types

### Phase 4: Threat Intelligence
- [ ] Create `/dashboard/firewall/threat-intelligence/page.tsx`
- [ ] Implement Threat Pattern Detection Panel
- [ ] Implement Threat Timeline Chart
- [ ] Implement Threat Database Browser
- [ ] Add pattern similarity visualization

### Phase 5: Incident Response
- [ ] Create `/dashboard/firewall/incident-response/page.tsx`
- [ ] Implement Incident Statistics Cards
- [ ] Implement Incident List component
- [ ] Implement Incident Details component
- [ ] Implement Timeline visualization
- [ ] Add incident actions

### Phase 6: Analytics
- [ ] Create `/dashboard/firewall/analytics/page.tsx`
- [ ] Implement Key Metrics Cards
- [ ] Implement Request Volume Chart
- [ ] Implement Latency Distribution Chart
- [ ] Implement Threat Distribution Charts
- [ ] Implement Compliance Dashboard
- [ ] Implement Custom Report Builder

### Phase 7: API Integration
- [ ] Update `api-config.ts` with firewall endpoints
- [ ] Implement API calls for all modules
- [ ] Add error handling
- [ ] Add loading states
- [ ] Implement polling for real-time data

### Phase 8: Polish & Testing
- [ ] Add loading.tsx files for each route
- [ ] Implement error boundaries
- [ ] Add empty states
- [ ] Test responsiveness
- [ ] Test accessibility
- [ ] Performance optimization

---

## 🎯 Success Criteria

The implemented UI should:

1. **Visual Consistency**
   - Match existing design language
   - Use same color system and gradients
   - Consistent spacing and typography

2. **Functionality**
   - All widgets display real-time data
   - Filters and search work correctly
   - Navigation is smooth
   - Modals and dialogs function properly

3. **Performance**
   - Pages load in < 2 seconds
   - Real-time updates are smooth
   - No lag during interactions
   - Charts render efficiently

4. **User Experience**
   - Intuitive navigation
   - Clear information hierarchy
   - Helpful tooltips and labels
   - Responsive on all devices

5. **Accessibility**
   - Keyboard navigable
   - Screen reader friendly
   - Proper ARIA labels
   - Color contrast compliant

---

## 📝 Notes for Implementation

1. **Start with Dashboard**: Implement the main firewall dashboard first as it provides the overview
2. **Reuse Components**: Create reusable components for common patterns (stat cards, feeds, charts)
3. **Mock Data First**: Use mock data initially, then connect to real API
4. **Progressive Enhancement**: Build basic functionality first, then add advanced features
5. **Test Incrementally**: Test each module as you build it
6. **Follow Existing Code**: Study `prompt-injection/page.tsx` for patterns and structure

---

## 🔗 Reference Links

- **Existing Dashboard**: `frontend/app/dashboard/page.tsx`
- **Example Module Page**: `frontend/app/dashboard/prompt-injection/page.tsx`
- **Layout Structure**: `frontend/app/dashboard/layout.tsx`
- **UI Components**: `frontend/components/ui/*`
- **API Config**: `frontend/lib/api-config.ts`

---

**Document Version**: 1.0  
**Last Updated**: January 2025  
**For**: Frontend Development Agents

