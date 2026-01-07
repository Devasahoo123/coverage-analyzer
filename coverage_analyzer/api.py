from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from parser.coverage_parser import CoverageParser
from llm.suggestion_generator import SuggestionGenerator
from prioritizer.scoring import score_suggestion

app = FastAPI(title="Coverage Analyzer API")

# ✅ Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/coverage")
def get_coverage():
    # ---------- Parse coverage report ----------
    with open("data/sample_report.txt", encoding="utf-8") as f:
        report = f.read()

    parser = CoverageParser(report)
    parsed = parser.parse_all()

    # ---------- Generate LLM suggestions ----------
    generator = SuggestionGenerator()
    suggestions = []

    for bin_info in parsed["uncovered_bins"]:
        llm_output = generator.generate(parsed["design"], bin_info)
        score = score_suggestion(
            coverage_impact=1.0,  # placeholder, could be dynamic
            difficulty=llm_output["difficulty"],
            has_dependencies=len(llm_output.get("dependencies", [])) > 0
        )

        suggestions.append({
            "target_bin": f"{bin_info['covergroup']}.{bin_info['coverpoint']}.{bin_info['bin']}",
            "score": score,
            **llm_output
        })

    # ---------- Coverage Closure Prediction (Bonus Part 4) ----------
    # Simple heuristic model for demo purposes
    uncovered_count = len(parsed["uncovered_bins"])
    total_bins = uncovered_count + sum(len(cg.get("bins", [])) for cg in parsed.get("covergroups", []))
    closure_probability = max(0, min(1, parsed["overall_coverage"] / 100))
    estimated_time_to_closure_hours = uncovered_count * 2  # example: 2 hours per uncovered bin
    blocking_bins = [
        bin_info for bin_info in parsed["uncovered_bins"]
        if "all_eight" in bin_info["bin"] or "max" in bin_info["bin"]
    ]

    return {
        "design": parsed["design"],
        "overall_coverage": parsed["overall_coverage"],
        "uncovered_bins": parsed["uncovered_bins"],
        "cross_coverage": parsed["cross_coverage"],
        "suggestions": suggestions,
        "coverage_closure_prediction": {
            "estimated_time_to_closure_hours": estimated_time_to_closure_hours,
            "closure_probability": closure_probability,
            "blocking_bins": blocking_bins
        }
    }
