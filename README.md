# Coverage Analyzer with Prioritized Suggestions

## Overview
This is a **Full-Stack Python + React project** that analyzes functional coverage reports and provides **prioritized verification suggestions**.  

It parses:
- Covergroups & Coverpoints
- Uncovered bins
- Cross-coverage scenarios  

The backend also generates **prioritized suggestions** (mocked LLM or OpenAI API) for verification engineers.

The React frontend displays a **dashboard** with:
- Summary metrics
- Uncovered bins
- Prioritized suggestions
- Search & filter functionality
- Expandable suggestion cards

---

## Features

### Backend (Python)
- Parses functional coverage report (`sample_report.txt`)
- Extracts:
  - Design name
  - Overall coverage %
  - Uncovered bins
  - Cross-coverage
- Generates prioritized suggestions for uncovered bins
- Exposes REST API using **FastAPI**
- Mocked LLM for suggestion generation (no API key required)

### Frontend (React)
- Fetches JSON from backend API
- Displays **summary cards**:
  - Design
  - Overall Coverage
  - Total Uncovered Bins
- Table of uncovered bins with search/filter
- Prioritized suggestions with expandable details
- Priority color-coded (High = red, Medium = orange, Low = green)
- Full-screen, centered responsive dashboard

---

## 🗂 Project Structure
├── coverage_analyzer/ # Python backend
│ ├── api.py # FastAPI backend
│ ├── main.py # CLI testing
│ ├── parser/ # Coverage parser
│ ├── llm/ # LLM suggestion generator
│ ├── prioritizer/ # Priority scoring
│ └── data/ # Sample coverage reports
│
├── coverage_ui/ # React frontend
│ ├── src/
│ │ └── App.jsx
│ ├── public/
│ └── package.json
│
├── .gitignore # Git ignore file
├── requirements.txt # Python dependencies
└── README.md
