# Installation Tracker

This file tracks software and artifacts installed or created during development of this assignment.
**Review this list after submission to reclaim disk space.**

## Installed During Development

| Item | Location / Command | Approx. Size | Safe to Delete? |
|------|-------------------|--------------|----------------|
| Python virtual environment | `backend/.venv/` | ~45 MB (measured) | Yes, after assignment — delete folder |
| pip packages (in venv) | Inside `.venv/` | Included above | Yes, with venv |
| pytest cache | `backend/.pytest_cache/` | < 5 MB | Yes |
| Docker image (if built) | `docker images` → `support-ticket-classifier-backend` | ~200–400 MB | Yes — `docker rmi <image>` |
| Docker build cache | Docker Desktop cache | Varies | Yes — Docker Desktop → Clean / `docker builder prune` |

## Not Installed (Prerequisites Only)

| Item | Notes |
|------|-------|
| Flutter SDK | Not installed on this machine. Install separately when running the frontend (~1–2 GB). |
| OpenAI API | Cloud service — no local install |

## Cleanup Commands (After Assignment)

```powershell
# Remove Python virtual environment
Remove-Item -Recurse -Force backend\.venv

# Remove pytest cache
Remove-Item -Recurse -Force backend\.pytest_cache -ErrorAction SilentlyContinue

# Remove Docker image (if built)
docker compose down
docker rmi support-ticket-classifier-backend 2>$null
docker builder prune -f

# Optional: remove entire project folder when no longer needed
# Remove-Item -Recurse -Force C:\Users\akaas\karthik-assignment\support-ticket-classifier
```

## Last Updated

2026-07-12 — Initial project setup
