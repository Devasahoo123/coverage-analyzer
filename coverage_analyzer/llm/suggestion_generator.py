class SuggestionGenerator:
    def generate(self, design, uncovered_bin):
        return {
            "priority": "high",
            "difficulty": "medium",
            "suggestion": (
                f"Create a directed test to hit "
                f"{uncovered_bin['bin']} in "
                f"{uncovered_bin['coverpoint']}."
            ),
            "reasoning": (
                "This bin has zero hits and represents a "
                "critical functional scenario that is not "
                "covered by random testing."
            )
        }
