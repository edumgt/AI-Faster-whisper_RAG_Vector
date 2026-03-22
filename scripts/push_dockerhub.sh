#!/usr/bin/env bash
# scripts/push_dockerhub.sh
# Build the psycho-chroma Docker image and push it to Docker Hub (edumgt).
#
# Prerequisites:
#   docker login   (or DOCKER_USER / DOCKER_PAT env vars for CI)
#
# Usage:
#   bash scripts/push_dockerhub.sh [tag]
#   bash scripts/push_dockerhub.sh latest
#   bash scripts/push_dockerhub.sh v1.0.0
#
# Environment variables:
#   DOCKER_USER   - Docker Hub username (default: edumgt)
#   DOCKER_PAT    - Docker Hub Personal Access Token (for CI login)
#   IMAGE_TAG     - Image tag (default: latest, overridden by first arg)

set -euo pipefail

DOCKER_USER="${DOCKER_USER:-edumgt}"
IMAGE_NAME="${DOCKER_USER}/psycho-chroma-db"
IMAGE_TAG="${1:-${IMAGE_TAG:-latest}}"
FULL_TAG="${IMAGE_NAME}:${IMAGE_TAG}"

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "======================================"
echo "  Building image: ${FULL_TAG}"
echo "  Context: ${REPO_ROOT}"
echo "======================================"

# Optional CI login
if [[ -n "${DOCKER_PAT:-}" ]]; then
  echo "${DOCKER_PAT}" | docker login -u "${DOCKER_USER}" --password-stdin
fi

# Step 1: Run the crawl script to refresh seed data (skip Wikipedia in CI)
echo ""
echo ">> [1/3] Refreshing psychoanalysis seed data ..."
cd "${REPO_ROOT}"
python scripts/crawl_psychoanalysis.py --no-wikipedia \
    --input samples/psychoanalysis_seed.jsonl \
    --output samples/psychoanalysis_seed.jsonl

# Step 2: Build Docker image
echo ""
echo ">> [2/3] Building Docker image ..."
docker build \
  -f Dockerfile.chromadb \
  -t "${FULL_TAG}" \
  --label "build.date=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --label "build.version=${IMAGE_TAG}" \
  "${REPO_ROOT}"

# Also tag as latest if a specific version was given
if [[ "${IMAGE_TAG}" != "latest" ]]; then
  docker tag "${FULL_TAG}" "${IMAGE_NAME}:latest"
fi

# Step 3: Push
echo ""
echo ">> [3/3] Pushing to Docker Hub ..."
docker push "${FULL_TAG}"
if [[ "${IMAGE_TAG}" != "latest" ]]; then
  docker push "${IMAGE_NAME}:latest"
fi

echo ""
echo "======================================"
echo "  Done!"
echo "  Image pushed: ${FULL_TAG}"
if [[ "${IMAGE_TAG}" != "latest" ]]; then
  echo "  Also pushed:  ${IMAGE_NAME}:latest"
fi
echo "======================================"
