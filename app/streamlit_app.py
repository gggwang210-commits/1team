"""Minimal Streamlit UI for the Korea Republic prediction MVP."""

from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PREDICTION_TABLE_PATH = PROJECT_ROOT / "reports" / "prediction_table.csv"
MODEL_EVALUATION_PATH = PROJECT_ROOT / "reports" / "model_evaluation.md"
PIPELINE_COMMANDS = [
    "python src/data/build_dataset.py",
    "python src/features/make_features.py",
    "python src/models/train_baseline.py",
    "python src/models/predict.py",
    "python src/models/evaluate.py",
]


def show_pipeline_instructions() -> None:
    """Explain how beginners can generate the required report artifacts."""
    st.info(
        "예측 결과와 평가 리포트를 보려면 먼저 아래 명령을 프로젝트 루트에서 "
        "순서대로 실행하세요."
    )

    # Keep commands in one code block so users can copy and run them easily.
    st.code("\n".join(PIPELINE_COMMANDS), language="bash")


def render_prediction_table() -> bool:
    """Render the prediction table when it exists.

    Returns:
        True if the file exists, regardless of whether rendering succeeds.
        The caller uses this to decide whether to show pipeline instructions.
    """
    if not PREDICTION_TABLE_PATH.exists():
        return False

    st.subheader("Prediction Table")

    try:
        prediction_table = pd.read_csv(PREDICTION_TABLE_PATH)
    except Exception as exc:  # Display a friendly UI error instead of a blank app.
        st.error(f"예측 테이블을 읽는 중 오류가 발생했습니다: {exc}")
        return True

    st.dataframe(prediction_table, use_container_width=True)
    return True


def render_model_evaluation() -> bool:
    """Render the Markdown evaluation report when it exists."""
    if not MODEL_EVALUATION_PATH.exists():
        return False

    st.subheader("Model Evaluation")

    try:
        evaluation_markdown = MODEL_EVALUATION_PATH.read_text(encoding="utf-8")
    except Exception as exc:  # Display a friendly UI error instead of a blank app.
        st.error(f"모델 평가 리포트를 읽는 중 오류가 발생했습니다: {exc}")
        return True

    st.markdown(evaluation_markdown)
    return True


def main() -> None:
    """Run the MVP Streamlit application."""
    st.set_page_config(
        page_title="Korea Republic Match Outcome Prediction MVP",
        page_icon="🇰🇷",
        layout="wide",
    )

    st.title("Korea Republic Match Outcome Prediction MVP")
    st.caption("Win/Draw/Loss는 대한민국 관점입니다.")

    has_prediction_table = render_prediction_table()
    has_model_evaluation = render_model_evaluation()

    if not has_prediction_table or not has_model_evaluation:
        show_pipeline_instructions()


if __name__ == "__main__":
    main()
