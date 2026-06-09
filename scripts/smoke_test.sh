#!/usr/bin/env bash
# Run the MVP smoke test and write a small execution report.
#
# Beginner note: this script intentionally fails before doing any project work
# when the local `main` branch is missing. That keeps local and CI smoke-test
# runs reproducible because they must start from a known baseline branch.

set -Eeuo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPORT_PATH="${PROJECT_ROOT}/reports/smoke_test_report.md"
EXPECTED_BRANCH="main"

fail() {
  local message="$1"
  echo "ERROR: ${message}" >&2
  exit 1
}

run_step() {
  local description="$1"
  shift

  echo "==> ${description}"
  "$@"
}

cd "${PROJECT_ROOT}"

# `git show-ref --verify` checks only local refs. It does not silently accept
# `origin/main`, which is important because this wrapper must fail immediately
# when a local `main` branch has not been created or checked out.
git show-ref --verify --quiet "refs/heads/${EXPECTED_BRANCH}" \
  || fail "Local '${EXPECTED_BRANCH}' branch was not found. Run 'git fetch origin main && git checkout main' before the smoke test."

CURRENT_BRANCH="$(git branch --show-current)"
if [[ "${CURRENT_BRANCH}" != "${EXPECTED_BRANCH}" ]]; then
  fail "Smoke test must run on '${EXPECTED_BRANCH}', but current branch is '${CURRENT_BRANCH:-detached HEAD}'. Run 'git checkout ${EXPECTED_BRANCH}' first."
fi

COMMIT_HASH="$(git rev-parse HEAD)"
STARTED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

# Keep this command list short and close to the MVP data flow documented in the
# README: dataset build -> features -> training -> prediction -> evaluation.
SMOKE_COMMANDS=(
  "python src/data/build_dataset.py"
  "python src/features/make_features.py"
  "python src/models/train_baseline.py"
  "python src/models/predict.py"
  "python src/models/evaluate.py"
)

mkdir -p "$(dirname "${REPORT_PATH}")"

STATUS="passed"
FAILED_COMMAND="none"
{
  echo "# Smoke Test Report"
  echo
  echo "- Started At (UTC): ${STARTED_AT}"
  echo "- Branch: ${CURRENT_BRANCH}"
  echo "- Commit Hash: ${COMMIT_HASH}"
  echo "- Status: running"
  echo "- Failed Command: none"
  echo
  echo "## Commands"
  for command in "${SMOKE_COMMANDS[@]}"; do
    echo "- \`${command}\`"
  done
} > "${REPORT_PATH}"

for command in "${SMOKE_COMMANDS[@]}"; do
  if ! run_step "${command}" bash -c "${command}"; then
    STATUS="failed"
    FAILED_COMMAND="${command}"
    break
  fi
done

FINISHED_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
{
  echo "# Smoke Test Report"
  echo
  echo "- Started At (UTC): ${STARTED_AT}"
  echo "- Finished At (UTC): ${FINISHED_AT}"
  echo "- Branch: ${CURRENT_BRANCH}"
  echo "- Commit Hash: ${COMMIT_HASH}"
  echo "- Status: ${STATUS}"
  echo "- Failed Command: ${FAILED_COMMAND}"
  echo
  echo "## Commands"
  for command in "${SMOKE_COMMANDS[@]}"; do
    echo "- \`${command}\`"
  done
} > "${REPORT_PATH}"

if [[ "${STATUS}" != "passed" ]]; then
  fail "Smoke test failed. See ${REPORT_PATH} for branch and commit metadata."
fi

echo "Smoke test passed. Report saved to: ${REPORT_PATH}"
