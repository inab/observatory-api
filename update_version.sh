#!/bin/bash

# Fail script if any command fails
set -e

# Ensure that we're on the main branch and up to date
git checkout main
git pull origin main

# Read the latest version from the VERSION file
NEW_VERSION=$(cat VERSION)

echo "Validating version format..."

# Check if the version follows Semantic Versioning (MAJOR.MINOR.PATCH)
if [[ ! "$NEW_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "ERROR: The version '$NEW_VERSION' in the VERSION file does not follow Semantic Versioning (e.g., 1.0.0)."
  exit 1
fi

# Check if the version needs a "v" prefix, and add it if not present
if [[ "$NEW_VERSION" != v* ]]; then
  NEW_VERSION="v$NEW_VERSION"
  echo "Prepending 'v' to version. New version is $NEW_VERSION"
fi

# Check if the version already has a Git tag
echo "Checking if version $NEW_VERSION already has a tag..."
if git rev-parse "$NEW_VERSION" >/dev/null 2>&1; then
  echo "ERROR: Version $NEW_VERSION already has a tag!"
  echo "It looks like you forgot to update the VERSION file."
  echo "Please update the VERSION file to the new version."
  exit 1
fi

# If no existing tag, proceed with committing and pushing the version update
echo "Version $NEW_VERSION does not have a tag. Proceeding with the update."

git tag "$NEW_VERSION"

git push origin main "$NEW_VERSION"

echo "Version updated to $NEW_VERSION and pushed to main branch."
