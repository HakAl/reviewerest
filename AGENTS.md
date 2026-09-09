# Working in reviewerest

- The product is `review/`. Keep its core guidance compact and optional detail in references.
- Review is read-only. Authorized editing belongs to the surrounding workflow.
- Run `python3 scripts/verify.py` after relevant changes. It needs Python 3.11+ and git,
  uses no model accounts, and is the same gate CI runs.
- Use `python3 scripts/push_verified.py origin main` to verify a committed snapshot
  before pushing that exact commit. Do not bypass a failed gate.
- Keep private reviews and raw model traces in ignored `.scratch/` or `evals/results/`.
  Never add personal paths, session metadata, credentials, or external skill packages.
- New public files require deliberate addition to `public-files.json`. Review contents
  first; the allowlist is not a substitute for content review.
- Preserve frozen fixtures and expectations. Update `evals/package-manifest.json`
  for intentional skill changes and bump skill/report versions when appropriate.
- The skill's record validator checks structure and consistency, not finding truth.
  Report model-evaluation limits and preserve failures privately or in clearly edited summaries.
- Claude uses `/reviewerest-review` for direct installs and `reviewerest-eval:review`
  in the isolated evaluation runner because its bundled `/review` caused a collision.
- Avoid em dash characters in authored files. Do not require GitHub CLI.
