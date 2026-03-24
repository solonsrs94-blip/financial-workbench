# Personal Financial Workbench — Vision Document

## What This Is

A personal financial workbench that combines professional-grade analysis tools, AI-powered exploration, and built-in financial education — all built on free data sources.

It starts as a Streamlit app for rapid development and evolves into a polished web application with a React frontend. It is designed to be shared with friends and family, not just used by one person.

This is **not** a finished product. It is a living tool that evolves over time through continuous use and iteration with Claude Code. It starts small and grows organically.

For the full technical structure, see **ARCHITECTURE.md**.

---

## Core Philosophy

- **The app is a window, not the product.** The real value is the ongoing process of exploring financial data. The app is just a comfortable visual interface for that exploration.
- **Bottom-up development.** Features emerge from experimentation. When an experiment proves useful enough that I keep coming back to it, it becomes a permanent feature.
- **I interpret, the AI assists.** The AI helps gather data, write code, execute analysis, and teach. I make the judgments about what the results mean.
- **Never "finished."** The app is always a work in progress. Claude Code is always part of the process. There is no launch date and no final version.
- **Minimal viable start.** Each new feature starts as the simplest useful version and gets refined through use, not upfront planning.
- **General foundation, personal experience.** The app itself is not tied to any specific investment methodology — but each user can customize it to fit their own approach. Your screener filters, watchlists, strategies, learning paths, and analysis style are yours. The platform is general; the experience is personal.
- **Learn by doing.** Anyone should be able to go from knowing nothing about finance to having deep understanding, just by using the app. Every number, every assumption, every calculation is explainable in context.

---

## Four Pillars

```
┌─────────────────────────────────────────────────┐
│              DASHBOARD                           │
│   Professional-grade screens for daily use —     │
│   company overview, charts, financials,          │
│   screener, valuation, macro, portfolio,         │
│   heatmaps, options, risk, and more.             │
│                                                  │
│   Grows over time as sandbox experiments         │
│   get "pinned" as permanent features.            │
├─────────────────────────────────────────────────┤
│              AI LAYER                            │
│   AI-powered features throughout the app:        │
│   • Sandbox — describe an idea, get results      │
│   • Chat — ask your data anything                │
│   • Document analysis — read 10-Ks, earnings     │
│   • Thesis challenger — AI questions your logic  │
│   • Smart alerts — AI explains what happened     │
│   • Reports — AI writes on "human language"      │
├─────────────────────────────────────────────────┤
│              EDUCATION                           │
│   Built-in learning system:                      │
│   • ? button on every number and assumption      │
│   • Three depth levels (beginner → advanced)     │
│   • "Ask AI" button with full context prompt     │
│   • Structured learning paths (courses)          │
│   • Interactive exercises                        │
│   • AI tutor — personalized teaching             │
│                                                  │
│   Goal: equivalent of a university education     │
│   in finance, economics, and investing —         │
│   learned through using the app itself.          │
├─────────────────────────────────────────────────┤
│              DATA LAYER                          │
│   Fetches and caches data from free sources.     │
│   Provider-based: new data sources added as      │
│   simple plugin files. Shared by all layers.     │
│   Starts local (SQLite), moves to cloud later.   │
└─────────────────────────────────────────────────┘
```

---

## The Sandbox — Core Differentiator

An embedded environment where anyone can describe any idea in natural language and get results.

1. Type an idea — plain English or Icelandic, no code needed.
   - *"Show me all S&P 500 companies that increased dividends every year for the past 10 years. Compare their average return to the index."*
2. Claude API writes Python code to answer the question.
3. The code runs in a sandboxed environment.
4. Results (charts, tables, numbers) are displayed.
5. Refine: *"Same thing but broken down by sector"*
6. Save, iterate, or pin as a permanent feature.

```
  IDEA (in sandbox)
       │
       ▼
  EXPERIMENT (run, see results)
       │
       ├── Not interesting → discard or save
       │
       └── Interesting → refine, iterate
                │
                ├── One-off insight → save as experiment
                │
                └── Useful regularly → PIN to dashboard
                         │
                         ▼
                  PERMANENT FEATURE
```

---

## The Analysis Workspace

Where data meets human reasoning:

1. You perform analysis (e.g., valuation of a company)
2. You write your reasoning in text boxes alongside the numbers
3. The app has: assumptions + data + calculations + your reasoning
4. AI combines everything and writes a report in plain language
5. Export as PDF — readable by anyone, not just finance experts

---

## Evolution Path

### Phase 1: Streamlit + Core Features
Build the foundation — data layer, key screens, basic functionality. Streamlit as the UI framework for rapid development.

### Phase 2-5: Features, AI, Education
Add screens, AI capabilities, education system, more data sources. See ARCHITECTURE.md for detailed phase breakdown.

### Phase 6: Beautiful Web App
Replace Streamlit with a React frontend and polished design. The entire `lib/` backend stays unchanged — only the UI layer is swapped.

### Phase 6+: Sharing
Add authentication, cloud storage, and deploy so others can use it.

---

## What This Is NOT

- **Not a trading tool.** No real-time execution, no automated trading.
- **Not an AI analyst.** The AI helps with data, code, education, and reports. The human does the thinking.
- **Not a one-time project.** This is an ongoing, evolving tool with no end date.
- **Not a Bloomberg replacement.** It recreates much of the analytical functionality using free data, but without proprietary data or real-time feeds.
- **Not methodology-specific.** The app is general-purpose. Any investment approach works.

---

## Context: My Background

- BS in Economics (financial economics), currently in M.Fin program.
- Studying various investment methodologies and IB valuation (Rosenbaum & Pearl).
- Long-term career goal: investment banking / corporate finance.
- This tool serves dual purposes: personal learning/exploration and building demonstrable technical + financial skills.
- I do not write code directly — Claude Code writes all code.

---

*This document is a living reference. Updated as the app evolves.*
*Last updated: 2026-03-24*
