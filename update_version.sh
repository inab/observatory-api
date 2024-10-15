#!/bin/bash

# Fail script if any command fails
set -e

# Ensure that we're on the main branch and up to date
git checkout main
git pull origin main

# Read the latest version from the VERSION file
NEW_VERSION=$(cat VERSION)

echo "Checking if version $NEW_VERSION already has a tag..."

# Check if the version already has a Git tag
if git rev-parse "v$NEW_VERSION" >/dev/null 2>&1; then
  echo "ERROR: Version $NEW_VERSION already has a tag!"
  echo "It looks like you forgot to update the VERSION file."
  echo "Please update the VERSION file to the new version."
  exit 1
fi

# If no existing tag, proceed with committing and pushing the version update
echo "Version $NEW_VERSION does not have a tag. Proceeding with the update."

# Stage the VERSION file for commit
git add VERSION

# Commit the change with a message
git commit -m "Update version to $NEW_VERSION"

# Push the commit to the remote repository
git push origin main

echo "Version updated to $NEW_VERSION and pushed to main branch."
