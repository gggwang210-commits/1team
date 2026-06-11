#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${PROJECT_ROOT}"

echo "Preprocessing validation pipeline started."
echo "Project root: ${PROJECT_ROOT}"

echo "Python environment:"
python --version

echo "[1/6] Building Korea MVP processed match dataset..."
python src/data/build_dataset.py

echo "[2/6] Building Korea MVP model-ready features..."
python src/features/make_features.py --target-scope korea

echo "[3/6] Building global processed match dataset..."
python src/data/build_dataset.py --global-scope

echo "[4/6] Building global model-ready features..."
python src/features/make_features.py --target-scope home

echo "[5/6] Validating team-name mapping..."
python src/data/validate_team_mapping.py

echo "[6/6] Running preprocessing validation gate..."
python src/data/validate_preprocessing.py --scope both

echo "Preprocessing validation pipeline passed."
echo "Generated validation reports:"
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
