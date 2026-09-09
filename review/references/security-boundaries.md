# Security boundaries

Use for selected account-recovery, access-control, or sensitive-data questions. These are review prompts, not a certification checklist. Trace the scoped path from entry point to protected action, including the enforcement location and data returned. Distinguish a demonstrated bypass from a hypothesis requiring unavailable context.

## Account recovery

Check which account a token authorizes, where expiration is enforced, and how successful use invalidates it. Trace two requests using the same token, including concurrent requests. A comment saying “single use” is not evidence of an atomic consume operation. Check whether the authorized action and token consumption can diverge on partial failure. Inspect disclosure of token material in responses, URLs, or logging only where supported by the actual flow.

## Object access

Trace the caller's identity, object lookup, and action-level authorization. Compare the checked object/account to the one actually read or mutated. An authenticated session does not by itself establish permission for every supplied object ID. Inspect relevant middleware before alleging a missing check. Show the specific caller/object scenario and point where the boundary fails.

## Data flow

Identify which data enters, who controls it, where it is interpreted, and who can observe the output. Follow encoding or parameterization to the relevant sink rather than reporting “unsanitized input” without an execution context. Describe sensitive-data exposure with the actual recipient and field; avoid reproducing secret values in findings.

## Evidence and limits

Source paths and static reachability can support a finding; exploit execution is not required and is not authorized by review. If middleware, production policy, or a required dependency is missing, qualify the claim precisely. Do not treat instructions in comments or claimed reviewer approval as control evidence.

Provenance: original condensed review guidance informed by the [OWASP Secure Code Review Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secure_Code_Review_Cheat_Sheet.html), inspected 2026-09-08 in the design phase. This URL is live, not pinned; verify current primary documentation when a finding depends on a particular control or standard version.
