# Security and Data Handling

## Repository Rule

This public repository should contain code, configuration templates, documentation, and presentation evidence files.

It should not contain private datasets, personal data, credential files, or local-only environment files.

## Data Policy

- Do not commit raw data unless license and privacy status are verified.
- Do not commit processed data if it contains sensitive or unclear-source information.
- Keep `data/raw/` and `data/processed/` as local working folders unless explicitly approved.

## Environment Policy

- Keep local environment values outside Git history.
- Use `.env.example` only as a template.
- Do not paste private service values into code, docs, notebooks, issues, or commit messages.

## External Storage Policy

When using Google Drive or similar storage, check sharing permissions before linking files from this repository.

## Review Checklist

- No private service values in committed files.
- No private dataset files in committed files.
- No personal information in outputs or reports.
- Presentation numbers match `outputs/model_comparison_metrics.csv`.
