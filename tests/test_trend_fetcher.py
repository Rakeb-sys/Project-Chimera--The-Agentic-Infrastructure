from skills.skill_trend_fetcher import fetch_trends

def test_trend_structure():
    result = fetch_trends("youtube")

    assert "trends" in result
    assert isinstance(result["trends"], list)
