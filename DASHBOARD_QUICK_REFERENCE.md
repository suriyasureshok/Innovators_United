# 🚀 BRIDGE Hub Dashboard - Quick Reference

## Getting Started in 3 Steps

### 1️⃣ Install
```bash
cd dashboard/bridge-insights
npm install
```

### 2️⃣ Configure
```bash
cp .env.example .env
# Edit .env if needed (default: http://localhost:8000)
```

### 3️⃣ Launch
```bash
# Terminal 1: Start backend
cd bridge_hub
uvicorn main:app --reload

# Terminal 2: Start dashboard
cd dashboard/bridge-insights
npm run dev
```

**Dashboard URL**: http://localhost:5173  
**API URL**: http://localhost:8000

---

## Page Overview

| Page | Route | Purpose | Key Features |
|------|-------|---------|--------------|
| **Overview** | `/` | Main dashboard | Health status, 4 KPIs, 3 tabs (Real-Time/Advisories/Performance) |
| **Patterns** | `/patterns` | Pattern detection | Active/Cooling/Dormant status, recent observations |
| **Advisories** | `/advisories` | Advisory management | Search, filter, detailed cards with metrics |
| **BRG Graph** | `/brg-graph` | Graph visualization | Nodes, edges, correlations |
| **Entities** | `/entities` | Entity monitoring | Participation metrics, fingerprint distribution |
| **Metrics** | `/metrics` | Performance analytics | Latency (P95/P99), throughput, health summary |

---

## API Hooks Quick Reference

```typescript
import { useHealthCheck, useHubStats, useAdvisories, 
         useMetrics, useBRGGraph } from '@/hooks/useHubAPI';

// Health monitoring (10s refresh)
const { data: health } = useHealthCheck();

// Hub statistics (5s refresh)
const { data: stats } = useHubStats();

// Advisory list (5s refresh)
const { data: advisories } = useAdvisories();

// Performance metrics (5s refresh)
const { data: metrics } = useMetrics();

// BRG graph data (5s refresh)
const { data: graph } = useBRGGraph();
```

---

## Color Coding

| Color | Hex | Usage |
|-------|-----|-------|
| 🔵 Cyan | `#06b6d4` | Entities, data flows |
| 🟣 Purple | `#a855f7` | Patterns, correlations |
| 🟠 Orange | `#fb923c` | Advisories, warnings |
| 🔴 Red | `#ef4444` | Fraud scores, critical |
| 🟢 Green | `#22c55e` | Active, healthy |
| 🟡 Yellow | `#eab308` | Cooling, moderate |

---

## Component Patterns

### Metric Card
```tsx
<Card className="bg-gradient-to-br from-cyan-900 to-cyan-950 border-cyan-800">
  <CardHeader className="pb-2">
    <CardTitle className="text-sm font-medium text-cyan-300">
      <Icon className="w-4 h-4" /> Label
    </CardTitle>
  </CardHeader>
  <CardContent>
    <div className="text-4xl font-bold text-white">{value}</div>
    <p className="text-xs text-cyan-300">Description</p>
  </CardContent>
</Card>
```

### Loading State
```tsx
{isLoading ? (
  <Skeleton className="h-12 w-24" />
) : (
  <div>{content}</div>
)}
```

### Status Badge
```tsx
<Badge className={
  status === 'ACTIVE' ? 'bg-green-500' :
  status === 'COOLING' ? 'bg-yellow-500' :
  'bg-slate-500'
}>
  {status}
</Badge>
```

---

## Auto-Refresh Configuration

**Global Settings** (in `App.tsx`):
```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchInterval: 5000,  // 5 seconds
      staleTime: 2000,        // 2 seconds
    },
  },
});
```

**Per-Hook Settings** (in `useHubAPI.ts`):
```typescript
// Health check - slower refresh
useQuery({
  queryKey: ['health'],
  refetchInterval: 10000,  // 10 seconds
});

// Stats - fast refresh
useQuery({
  queryKey: ['stats'],
  refetchInterval: 5000,   // 5 seconds
});
```

---

## Troubleshooting

### ❌ API Connection Failed
```bash
# Check backend is running
curl http://localhost:8000/health

# Check .env configuration
cat .env
# Should contain: VITE_HUB_API_URL=http://localhost:8000

# Restart dashboard
npm run dev
```

### ❌ Blank Page / White Screen
```bash
# Clear cache and reinstall
rm -rf node_modules .vite
npm install
npm run dev
```

### ❌ CORS Errors
Backend needs CORS middleware. In `bridge_hub/main.py`:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## File Locations

```
📁 dashboard/bridge-insights/
├── 🔧 .env.example           # Environment template
├── 📖 README_DASHBOARD.md    # Full documentation
├── 📁 src/
│   ├── 📁 components/
│   │   └── Navigation.tsx    # Main nav bar
│   ├── 📁 hooks/
│   │   └── useHubAPI.ts      # API integration
│   ├── 📁 pages/
│   │   ├── Overview.tsx      # Main dashboard
│   │   ├── Advisories.tsx    # Advisory mgmt
│   │   ├── Entities.tsx      # Entity monitoring
│   │   ├── Metrics.tsx       # Performance
│   │   ├── BRGGraph.tsx      # Graph viz
│   │   └── PatternsNew.tsx   # Pattern detection
│   └── App.tsx               # Router + QueryClient

📁 root/
├── 📊 FRONTEND_UPDATE_SUMMARY.md
├── 🎨 DASHBOARD_DESIGN_GUIDE.md
├── ✅ DASHBOARD_IMPLEMENTATION_CHECKLIST.md
└── 🚀 start-dashboard.ps1
```

---

## Testing with Sample Data

### Generate Test Data
```bash
# Terminal 1: Start entity_a
cd entity_a
python main.py

# Terminal 2: Start entity_b  
cd entity_b
python main.py

# Both will start sending fingerprints to BRIDGE Hub
```

### Verify in Dashboard
1. Navigate to **Overview** - see metrics update
2. Check **Patterns** - see ACTIVE patterns
3. View **Advisories** - see generated advisories
4. Monitor **Metrics** - see latency and throughput
5. Explore **Entities** - see entity_a and entity_b
6. Inspect **BRG Graph** - see nodes and edges

---

## Build for Production

```bash
# Build optimized bundle
npm run build

# Output: dist/ directory

# Preview production build locally
npm run preview

# Deploy dist/ to:
# - Nginx
# - Apache
# - Vercel
# - Netlify
# - AWS S3 + CloudFront
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_HUB_API_URL` | `http://localhost:8000` | BRIDGE Hub API endpoint |
| `VITE_DEBUG` | `false` | Enable debug logging |
| `VITE_REFRESH_INTERVAL` | `5000` | Data refresh interval (ms) |
| `VITE_HEALTH_CHECK_INTERVAL` | `10000` | Health check interval (ms) |

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Ctrl + R` | Refresh data manually |
| `Ctrl + F` | Focus search (on Advisories page) |
| `Esc` | Close modals/dialogs |
| `Tab` | Navigate between elements |

---

## Performance Tips

1. **Optimize Refresh Intervals**
   - Increase `refetchInterval` if data changes slowly
   - Decrease for critical real-time monitoring

2. **Lazy Load Heavy Components**
   - Use `React.lazy()` for graph visualization
   - Implement code splitting for large pages

3. **Monitor Network Tab**
   - Check for excessive API calls
   - Verify caching is working

4. **Use Production Build**
   - `npm run build` optimizes bundle size
   - Minifies and tree-shakes code

---

## Support & Documentation

- 📖 **Full Docs**: [README_DASHBOARD.md](dashboard/bridge-insights/README_DASHBOARD.md)
- 🎨 **Design Guide**: [DASHBOARD_DESIGN_GUIDE.md](DASHBOARD_DESIGN_GUIDE.md)
- ✅ **Checklist**: [DASHBOARD_IMPLEMENTATION_CHECKLIST.md](DASHBOARD_IMPLEMENTATION_CHECKLIST.md)
- 📊 **Summary**: [FRONTEND_UPDATE_SUMMARY.md](FRONTEND_UPDATE_SUMMARY.md)

---

## Quick Commands

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint

# Type check
npx tsc --noEmit
```

---

**🎉 Happy Monitoring! 🎉**

For questions or issues, refer to the full documentation in `README_DASHBOARD.md`.
