"""Simple gamification utilities."""

def calculate_level(points: int) -> int:
    """Return a user level derived from their points."""
    return max(1, points // 100 + 1)
