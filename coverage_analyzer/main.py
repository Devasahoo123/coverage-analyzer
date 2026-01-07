import os
import json
from datetime import datetime, timedelta
from parser.coverage_parser import CoverageParser
from llm.suggestion_generator import SuggestionGenerator
from prioritizer.scoring import score_suggestion

# -----------------------
# Part 4: Coverage Closure Prediction
# -----------------------
class CoverageClosurePredictor:
    def __init__(self, parsed_report, coverage_history=None):
        self.parsed = parsed_report
        self.coverage_history = coverage_history or []

    def estimate_velocity(self):
        if len(self.coverage_history) < 2:
            return 1.0
        (t1, c1), (t2, c2) = self.coverage_history[-2], self.coverage_history[-1]
        delta_hours = (t2 - t1).total_seconds() / 3600
        delta_coverage = c2 - c1
        if delta_hours <= 0:
            return 1.0
        return delta_coverage / delta_hours

    def estimate_time_to_closure(self):
        current = self.parsed["overall_coverage"]
        velocity = self.estimate_velocity()
        remaining = 100.0 - current
        if velocity <= 0:
            return float("inf")
        return round(remaining / velocity, 2)

    def predict_closure_probability(self):
        uncovered_count = len(self.parsed["uncovered_bins"])
        if uncovered_count == 0:
            return 1.0
        hard_bins = [b for b in self.parsed["uncovered_bins"]
                     if any(h in b["bin"].lower() for h in ["decode_error", "timeout", "all_eight"])]
        probability = max(0.0, 1.0 - len(hard_bins)/uncovered_count)
        if self.parsed["overall_coverage"] >= 90:
            probability = max(probability, 0.9)
        return round(probability, 2)

    def find_blocking_bins(self):
        blocking = []
        for b in self.parsed["uncovered_bins"]:
            bin_lower = b["bin"].lower()
            if any(keyword in bin_lower for keyword in ["decode_error", "timeout", "all_eight"]):
                blocking.append(b)
        return blocking

    def predict_all(self):
        return {
            "estimated_time_to_closure_hours": self.estimate_time_to_closure(),
            "closure_probability": self.predict_closure_probability(),
            "blocking_bins": self.find_blocking_bins()
        }

# -----------------------
# Main execution
# -----------------------
if __name__ == "__main__":
    with open("data/sample_report.txt", encoding="utf-8") as f:
        report_text = f.read()

    parser = CoverageParser(report_text)
    parsed = parser.parse_all()

    generator = SuggestionGenerator()
    results = []

    for bin_info in parsed["uncovered_bins"]:
        llm_output = generator.generate(parsed["design"], bin_info)
        score = score_suggestion(
            coverage_impact=1.0,
            difficulty=llm_output["difficulty"],
            has_dependencies="dependency" in llm_output["reasoning"].lower()
        )
        results.append({
            "target_bin": f"{bin_info['covergroup']}.{bin_info['coverpoint']}.{bin_info['bin']}",
            "score": score,
            "llm_output": llm_output
        })

    results.sort(key=lambda x: x["score"], reverse=True)

    coverage_history = [
        (datetime.now() - timedelta(hours=5), 50.0),
        (datetime.now() - timedelta(hours=1), parsed["overall_coverage"])
    ]
    predictor = CoverageClosurePredictor(parsed, coverage_history)
    closure_prediction = predictor.predict_all()

    final_output = {
        "design": parsed["design"],
        "overall_coverage": parsed["overall_coverage"],
        "suggestions": [
            {**r["llm_output"], "target_bin": r["target_bin"], "score": r["score"]}
            for r in results
        ],
        "coverage_closure_prediction": closure_prediction
    }

    os.makedirs("examples", exist_ok=True)
    with open("examples/final_output.json", "w") as f:
        json.dump(final_output, f, indent=2)

    print(json.dumps(final_output, indent=2))
