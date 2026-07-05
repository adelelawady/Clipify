#!/usr/bin/env bash
set -euo pipefail

echo "=== Secret cleanse helper ==="
echo "This script will:
 - show likely secret occurrences (simple heuristics)
 - untrack .env files from git index (safe)
 - optionally run git-filter-repo or show BFG commands to remove from history
"

ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$ROOT"

echo "1) Show likely secrets (google API keys, 'AIza')"
git grep -n "AIza" || echo "No obvious Google API key pattern found in tracked files."

echo "\n2) Show .env files in repo root"
ls -la .env* 2>/dev/null || echo "No .env files found in working dir"

echo "\n3) Untrack .env and .env.save from git index (won't delete local files)"
git rm --cached -r .env .env.save || true
echo "Staged removal of tracked .env files. Commit the change to stop tracking them."
echo "Run:\n  git add .gitignore .env.example\n  git commit -m 'Stop tracking env files'"

read -p "Do you want to permanently remove .env and .env.save from git history now? (y/N) " confirm
if [[ "$confirm" =~ ^[Yy]$ ]]; then
  if command -v git-filter-repo >/dev/null 2>&1; then
    echo "Running git-filter-repo to remove .env files from history..."
    git filter-repo --invert-paths --paths .env --paths .env.save
    echo "git-filter-repo finished. You will need to force-push to remote."
    echo "Run: git push --force --all && git push --force --tags"
  else
    echo "git-filter-repo not found. You can install it (pip install git-filter-repo) or use BFG (https://rtyley.github.io/bfg-repo-cleaner/)"
    echo "BFG example (run locally):"
    echo "  java -jar bfg.jar --delete-files .env --delete-files .env.save your-repo.git"
    echo "Followed by: git reflog expire --expire=now --all && git gc --prune=now --aggressive && git push --force"
  fi
else
  echo "Skipping history rewrite. You should still commit the index changes to stop tracking env files." 
fi

echo "\nDone. Next steps: revoke compromised keys (see PUBLISHING.md) and push to your GitHub remote." 
