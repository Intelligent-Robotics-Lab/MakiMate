# MakiMate — Simple Contribution Guide

This is the short, practical version for contributors. Use feature branches off `main`, prefixed with a scope.

---

## Branches & What They Mean
These are **scope namespaces** for naming your branches. They are not long‑lived dev branches.

- **main** — Protected, always stable. All PRs merge here after review and CI.
- **behavior** — High‑level behaviors, interaction logic, PAD regulation scripts, launch orchestration.
- **core** — Core framework & ROS 2 infrastructure (build, package structure, bringup, utils).
- **devops** — Dockerfiles, Buildx, CI/CD workflows, GHCR publishing, release scripts.
- **docs** — Documentation: READMEs, setup guides, architecture notes, diagrams.
- **hw** — Hardware interfaces, drivers, device config (sensors, motors, GPIO), platform specifics.
- **perception** — Vision/audio/sensing modules (e.g., face detection, VAD, ASR), data pipelines.
- **replicate** — Experiment replication: datasets pointers, eval scripts, fixed configs to reproduce results.
- **ui** — Visualization, teleop panels, dashboards, RViz configs, web/desktop UIs.

### Naming Pattern
```
<scope>/<type>/<short-description>
```
Examples:
```
perception/feature/face-detection
behavior/fix/pad-timing
devops/chore/ghcr-permissions
ui/feature/teleop-dashboard
```
Rules: lowercase + hyphens; one branch = one change set; open a draft PR early.

---

## Git Cheatsheet
> Run these from the repo root. Replace names in <> with yours.

### Setup (one-time)
```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### Get the Code / Sync It
```bash
git clone https://github.com/Intelligent-Robotics-Lab/MakiMate.git
cd MakiMate
git pull origin main  # update local main
```

### Create & Switch to a Feature Branch
```bash
git checkout main
git pull origin main
git checkout -b perception/feature/face-detection
```

### See Where You Are / What Changed
```bash
git status
git diff                 # unstaged changes
git diff --staged        # what will be committed
```

### Stage, Commit, Push
```bash
git add .
git commit -m "feat(perception): add face detection node"
git push -u origin perception/feature/face-detection
```

### Open a Pull Request
- Go to GitHub → your branch page → “Compare & pull request”.
- In the PR body, describe **what/why/how**, link issues, and add test/launch notes.

### Keep Your Branch Up To Date
```bash
git fetch origin
git rebase origin/main   # or: git merge origin/main
# resolve conflicts → git add <files> → git rebase --continue
```

### Stash Work in Progress
```bash
git stash push -m "wip: experiments"
git stash list
git stash pop
```

### Undo Carefully
```bash
git restore <file>          # discard unstaged changes in a file
git reset HEAD <file>       # unstage a file
git reset --soft HEAD~1     # undo last commit, keep changes staged
git revert <commit-sha>     # new commit that reverses a prior one
```

### Delete Branches After Merge
```bash
git branch -d perception/feature/face-detection               # local
git push origin --delete perception/feature/face-detection    # remote
```

### List / Filter Branches
```bash
git branch                 # local branches
git branch -r              # remote branches
git branch | grep '^\s*perception/'
```

### Tag a Release (Maintainers)
```bash
git tag -a v0.1.0 -m "MakiMate v0.1.0"
git push origin v0.1.0
```

---

## Workflow Summary
1) Branch from `main` using a scope prefix.
2) Build/test inside the Docker dev image.
3) Keep branch small; push and open a draft PR early.
4) Rebase/merge `main` often; keep CI green.
5) Squash-merge; delete branch after merge.

If anything is unclear, open a discussion or ping **#dev-setup** on Discord (@pourya9698).

