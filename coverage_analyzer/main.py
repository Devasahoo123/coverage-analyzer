from parser.coverage_parser import CoverageParser
from llm.suggestion_generator import SuggestionGenerator
from prioritizer.scoring import score_suggestion

with open("data/sample_report.txt", encoding="utf-8") as f:
    report_text = f.read()

parser = CoverageParser(report_text)
parsed = parser.parse_all()

print("Design:", parsed["design"])
print("Overall Coverage:", parsed["overall_coverage"])

print("\nUncovered Bins:")
for b in parsed["uncovered_bins"]:
    print(b)

print("\nCross Coverage:")
for c in parsed["cross_coverage"]:
    print(c)

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

print("\n=== PRIORITIZED SUGGESTIONS ===")
for r in results:
    print("\nTarget:", r["target_bin"])
    print("Score:", r["score"])
    print("LLM:", r["llm_output"])
