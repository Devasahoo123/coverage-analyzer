def score_suggestion(coverage_impact, difficulty, has_dependencies):
    difficulty_map = {
        "easy": 1,
        "medium": 2,
        "hard": 3
    }

    inverse_difficulty = 1 / difficulty_map.get(difficulty, 2)
    dependency_score = 0.5 if has_dependencies else 1.0

    score = (
        coverage_impact * 0.4 +
        inverse_difficulty * 0.3 +
        dependency_score * 0.3
    )

    return round(score, 2)
