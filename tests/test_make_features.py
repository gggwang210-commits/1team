import pandas as pd

from src.features.make_features import make_features


def test_make_features_drops_rows_without_target():
    matches = pd.DataFrame(
        {
            "date": ["2026-06-01", "2026-06-02"],
            "home_team": ["Korea Republic", "Korea Republic"],
            "away_team": ["Team A", "Team B"],
            "target_result_korea_perspective": ["Win", None],
        }
    )

    features = make_features(matches, target_scope="korea")

    assert len(features) == 1
    assert features["target_result"].tolist() == ["Win"]


def test_make_features_does_not_include_score_columns():
    matches = pd.DataFrame(
        {
            "date": ["2026-06-01"],
            "home_team": ["Korea Republic"],
            "away_team": ["Team A"],
            "home_score": [2],
            "away_score": [1],
            "target_result_korea_perspective": ["Win"],
        }
    )

    features = make_features(matches, target_scope="korea")

    assert "home_score" not in features.columns
    assert "away_score" not in features.columns


def test_make_features_preserves_duplicate_rows_before_save_step():
    matches = pd.DataFrame(
        {
            "date": ["2026-06-01", "2026-06-01"],
            "home_team": ["Team A", "Team A"],
            "away_team": ["Team B", "Team B"],
            "target_result": ["Win", "Win"],
        }
    )

    features = make_features(matches, target_scope="home")

    assert len(features) == 2
