from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from parser.coverage_parser import CoverageParser
from llm.suggestion_generator import SuggestionGenerator
from prioritizer.scoring import score_suggestion

app = FastAPI(title="Coverage Analyzer API")

# ✅ ADD CORS MIDDLEWARE
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/coverage")
def get_coverage():
    with open("data/sample_report.txt", encoding="utf-8") as f:
        report = f.read()

    parser = CoverageParser(report)
    parsed = parser.parse_all()

    generator = SuggestionGenerator()
    suggestions = []

    for bin_info in parsed["uncovered_bins"]:
        llm = generator.generate(parsed["design"], bin_info)
        score = score_suggestion(
            coverage_impact=1.0,
            difficulty=llm["difficulty"],
            has_dependencies=False
        )

        suggestions.append({
            "target": f"{bin_info['covergroup']}.{bin_info['coverpoint']}.{bin_info['bin']}",
            "score": score,
            "suggestion": llm
        })

    return {
        "design": parsed["design"],
        "overall_coverage": parsed["overall_coverage"],
        "uncovered_bins": parsed["uncovered_bins"],
        "cross_coverage": parsed["cross_coverage"],
        "prioritized_suggestions": suggestions
    }
