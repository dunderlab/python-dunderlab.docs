#!/bin/bash

# Validate arguments
if [[ "$#" -lt 1 || "$#" -gt 2 || ( "$#" -eq 2 && "$2" != "--push" ) ]]; then
  echo "Usage: $0 <dockerfile-path> [--push]"
  exit 1
fi

# Check if Docker is logged in
ensure_logged_in() {
  if ! docker info 2>/dev/null | grep -q 'Username:'; then
    echo "You are not logged in. Initiating docker login..."
    docker login
  else
    echo "Already logged in to Docker Hub."
  fi
}

DOCKERFILE="$1"
DOCKERFILE_DIR=$(dirname "$DOCKERFILE")
DOCKERFILE_NAME=$(basename "$DOCKERFILE")

# Change to Dockerfile directory
cd "$DOCKERFILE_DIR" || { echo "Failed to change to directory $DOCKERFILE_DIR"; exit 1; }

# Extract LABEL lines
LABEL_LINES=$(grep "^LABEL" "$DOCKERFILE_NAME")
IMAGE_NAME=$(echo "$LABEL_LINES" | grep "image" | awk -F'="' '{print $2}' | awk -F'"' '{print $1}')
VERSION=$(echo "$LABEL_LINES" | grep "version" | awk -F'="' '{print $2}' | awk -F'"' '{print $1}')

if [[ -z "$IMAGE_NAME" || -z "$VERSION" ]]; then
  echo "Missing 'image' and 'version' LABELs in the Dockerfile."
  exit 1
fi

echo "Image: $IMAGE_NAME"
echo "Version: $VERSION"

# Create buildx builder if it doesn't exist
if ! docker buildx inspect multiarch-builder > /dev/null 2>&1; then
  docker buildx create --name multiarch-builder --use
fi
docker buildx use multiarch-builder

if [[ "$2" == "--push" ]]; then
  echo "Building and pushing image..."
  ensure_logged_in
  docker buildx build --platform linux/amd64,linux/arm64 \
    -t "$IMAGE_NAME:$VERSION" \
    -t "$IMAGE_NAME:latest" \
    -f "$DOCKERFILE_NAME" \
    --push .
else
  echo "Building image locally..."
  docker buildx build --platform linux/amd64,linux/arm64 \
    -t "$IMAGE_NAME:$VERSION" \
    -f "$DOCKERFILE_NAME" \
    --load .
  docker tag "$IMAGE_NAME:$VERSION" "$IMAGE_NAME:latest"
fi
