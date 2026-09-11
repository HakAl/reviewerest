# reviewerest

An experimental general-purpose review skill for code, documents, plans, analyses, and product
UX. It chooses relevant review lenses, supports findings with evidence, and
reports what it could not check.

Findings distinguish support for the defect, its consequence and its proposed
correction. A reproduced failure does not automatically prove downstream harm
or a valid fix. Conditional claims name their assumptions and the next check.

**The product lives in [`review/`](review/SKILL.md).**

## Install

From the root of this repository, run the commands for your host. These install
the skill for use across your projects.

**[Codex](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)**

```sh
mkdir -p ~/.agents/skills/review
cp -R review/. ~/.agents/skills/review/
```

**[Claude Code](https://code.claude.com/docs/en/skills#where-skills-live)**

```sh
mkdir -p ~/.claude/skills/reviewerest-review
cp -R review/. ~/.claude/skills/reviewerest-review/
```

The Claude directory name gives it the command `/reviewerest-review`, avoiding
the `/review` collision observed in testing. To update an installed copy, pull
this repository and repeat its copy command.

## Use it

Start a new session in the project you want reviewed, then invoke the skill:

- **Codex:** `$review review this change for correctness and reliability`
- **Claude Code:** `/reviewerest-review review this plan for feasibility`

## Example

See the [short fictional review](examples/README.md): one missing status becomes
one finding across correctness and UX, with explicit evidence and limits.

## Develop and verify

Requires Python 3.11+ and git. From the repository root:

```sh
python3 scripts/verify.py
```

The gate runs offline tests and publication checks. It does not invoke a model.
For publishing, commit your changes and use:

```sh
python3 scripts/push_verified.py origin main
```

This verifies a clean committed snapshot before pushing that exact commit.
CI runs the same gate. See the [publishing workflow](docs/publishing.md).

- [Evaluation results and limits](docs/evaluations.md)
- [Agent working instructions](AGENTS.md)

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
