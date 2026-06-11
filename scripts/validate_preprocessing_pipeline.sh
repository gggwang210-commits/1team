#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

echo "Preprocessing validation pipeline started."
echo "Project root: ${PROJECT_ROOT}"
echo "No source validation PASS, no preprocessing."


echo "Python environment:"
python --version

echo "[1/7] Validating raw data sources..."
python src/data/validate_sources.py

echo "[2/7] Building Korea filtered processed match dataset..."
python src/data/build_dataset.py

echo "[3/7] Building Korea filtered model-ready features..."
python src/features/make_features.py --target-scope korea

echo "[4/7] Building global processed match dataset..."
python src/data/build_dataset.py --global-scope

echo "[5/7] Building global model-ready features..."
python src/features/make_features.py --target-scope home

echo "[6/7] Validating team-name mapping..."
python src/data/validate_team_mapping.py

echo "[7/7] Running preprocessing validation gate..."
python src/data/validate_preprocessing.py --scope both

echo "Preprocessing validation pipeline passed."
echo "Generated validation reports:"
echo "- reports/source_validation.md"
echo "- reports/source_validation.csv"
echo "- reports/preprocessing_validation.md"
echo "- reports/preprocessing_validation.csv"
echo "- reports/team_mapping_validation.md"
echo "- reports/unmapped_teams.csv"
echo "- reports/data_quality_summary.md"
echo ""
echo "Next allowed steps after PASS:"
echo "- python src/models/train_baseline.py"
echo "- python src/models/calibrate.py"
echo "- python src/simulation/run_tournament.py"
