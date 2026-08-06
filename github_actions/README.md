# GitHub Actions: Scheduled Data Pipelines on GitHub Pages

These examples show how a GitHub Actions workflow can run a `doit` pipeline on
a daily schedule, pull fresh data, and publish the regenerated HTML to GitHub
Pages — a self-updating dashboard with no server to maintain.

**Live site:** https://finm-32900.github.io/inclass_examples/

The two subexamples are built and deployed together by a single workflow:
[.github/workflows/deploy_examples_site.yml](../.github/workflows/deploy_examples_site.yml).
Note that workflow files **must** live in `.github/workflows/` at the *repo
root* — a `.github/` directory inside a subfolder is ignored by GitHub.

## Examples

| Directory | Topic | Secret needed |
|-----------|-------|---------------|
| [01_fred_chartbook/](01_fred_chartbook/) | Scheduled pydoit pipeline + chartbook site | None |
| [02_databento_secret/](02_databento_secret/) | Passing API keys via GitHub Actions secrets | `DATABENTO_API_KEY` |

The progression: `01` establishes the full pipeline-to-Pages loop using a
keyless data source (FRED), so there are no credentials to think about. `02`
then adds the one thing most real pipelines need on top: an API key that must
work both locally (from `.env`) and in CI (from the secret store) without ever
being committed.

## Key Concepts

- **Cron schedules run in UTC.** `0 10 * * *` is 10:00 UTC daily (4–5 AM
  Chicago, depending on daylight saving). `workflow_dispatch` adds a manual
  "Run workflow" button, and a `push` trigger with a `paths:` filter rebuilds
  the site when these examples change.
- **One commit on gh-pages, forever.** The deploy step creates an *orphan*
  branch (`git checkout --orphan gh-pages`) and force-pushes it, so the
  branch is overwritten in place on every run instead of accumulating a new
  commit per day. A daily site would otherwise add 365 commits of rendered
  HTML per year to the repo's history.
- **`git clean -fdx` before staging the site.** `git rm -rf .` only removes
  *tracked* files; gitignored build outputs (`_data/`, `_output/`, `docs/`)
  survive the branch switch and would otherwise leak into — or nest inside —
  the published site. (An earlier version of this workflow in
  [example-updating-dashboard](https://github.com/jmbejara/example-updating-dashboard)
  had exactly that bug: the site was published with a full duplicate copy of
  itself inside `docs/docs-stage/`.)
- **`.nojekyll`.** GitHub Pages runs Jekyll by default, which silently drops
  underscore-prefixed directories like Sphinx's `_static/`. An empty
  `.nojekyll` file at the site root disables Jekyll.
- **`permissions: contents: write`.** The workflow's `GITHUB_TOKEN` needs
  write access to push `gh-pages`. Declaring it in the YAML is portable —
  it works regardless of the repository's default workflow permissions.
- **`concurrency` with `cancel-in-progress`.** Prevents two runs (say, the
  cron and a push) from interleaving their force-pushes; the newest run wins.
- **Install fresh, cache only downloads.** The workflow caches pip's wheel
  cache keyed on the requirements files, but installs packages fresh every
  run. Caching the virtualenv itself with a loose `restore-keys:` prefix can
  restore a stale environment and break builds in ways that are painful to
  debug.
- **Failure mode: the old site stays up.** The deploy step only runs after
  both builds succeed, so a FRED or Databento outage leaves the previous
  day's site live rather than publishing a broken one.

## One-Time Repository Setup

Already done for this repo; you'll need these when copying the pattern to
your own:

```bash
# 1. Store the Databento API key as an Actions secret
gh secret set DATABENTO_API_KEY --repo <owner>/<repo>

# 2. Push the workflow to main; the first successful run creates gh-pages

# 3. Point GitHub Pages at the gh-pages branch (root)
gh api -X POST repos/<owner>/<repo>/pages \
  -f "source[branch]=gh-pages" -f "source[path]=/"
```

Expect the site URL to 404 for a few minutes after Pages is first enabled.

## Verifying the Overwrite Behavior

After at least two workflow runs:

```bash
gh api "repos/<owner>/<repo>/commits?sha=gh-pages" --jq 'length'   # → 1
```

The branch always has exactly one commit; only its SHA and timestamp change.
