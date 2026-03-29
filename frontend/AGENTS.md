# frontend

This file provides guidance to AI agents when working with code in this repository.

## Commands

```sh
npm ci            # install dependencies
npm run dev       # dev server on :3000
npm run build     # production build
npm run lint      # ESLint (core-web-vitals + typescript)
npx shadcn@latest add <component>  # add shadcn/ui component
```

## Tech Stack

- Next.js 16 App Router with React Compiler enabled
- shadcn/ui (base-nova style, neutral base color, Lucide icons)
- Tailwind CSS v4
- `src/` directory layout, path alias `@/*` -> `src/*`

## Important: Next.js 16 Breaking Changes

This project uses Next.js 16 which has breaking changes from training data. Read `node_modules/next/dist/docs/` before writing code. Key differences:

- All request APIs are async: `await cookies()`, `await headers()`, `await params`, `await searchParams`
- `proxy.ts` replaces `middleware.ts`
- Turbopack config is top-level (not under `experimental`)

## Pages

- `/` — Landing page
- `/camera` — Live WebSocket camera stream (client component, `react-use-websocket`)
- `/stats` — Raspberry Pi system info (server component, reads CPU/memory/temp)

## Architecture

- `next.config.ts` rewrites `/py/*` to `http://localhost:8000/*` (backend proxy)
- `allowedDevOrigins` allows local network access (Raspberry Pi)
- `src/lib/system.ts` — server-side utility for CPU/memory/temperature data
- `src/components/nav.tsx` — client component, shared navigation bar

## No test suite configured

<!-- BEGIN:nextjs-agent-rules -->

# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.

<!-- END:nextjs-agent-rules -->
