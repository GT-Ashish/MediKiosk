# MediKiosk Frontend

React 19 + Vite + TypeScript + Tailwind CSS v4 application for MediKiosk.

## Status

Foundation initialized with application shell and backend connectivity status monitor.

## Current Structure

```
frontend/
├── public/             # Static public assets
│   ├── favicon.svg
│   └── icons.svg
├── src/
│   ├── assets/         # Static assets
│   ├── components/     # Reusable UI components
│   │   └── HealthStatus.tsx  # Backend connectivity status card
│   ├── hooks/          # Custom React hooks
│   │   └── useHealthCheck.ts # Backend health polling/fetching hook
│   ├── pages/          # Page components (planned)
│   ├── services/       # API client services
│   │   └── api.ts      # Health check API client
│   ├── utils/          # Utility functions (planned)
│   ├── App.tsx         # Root application shell
│   ├── config.ts       # Environment configuration
│   ├── index.css       # Tailwind CSS v4 design tokens & base styles
│   └── main.tsx        # React entry point
├── .env.example        # Environment variable template
├── index.html          # HTML document template
├── package.json        # Frontend dependencies and scripts
├── tsconfig.json       # TypeScript configuration
└── vite.config.ts      # Vite configuration with proxy to backend
```

## Running Locally

```bash
# Install dependencies
npm install

# Start development server (port 5173)
npm run dev

# Production build
npm run build
```

The Vite dev server proxies `/api` requests to the FastAPI backend running at `http://localhost:8000`.
