# apps-repo

Central app distribution repository for the **rollersoft 全家桶**.

🌐 **Web**: [repo.rollersoft.com.au](https://repo.rollersoft.com.au)  
📦 **Index**: [index.json](https://exisz.github.io/apps-repo/index.json)

## Structure

```
apps/
  <app-dir>/
    metadata.json       # App metadata + version history
    icon.png            # App icon (512x512 recommended)
    screenshots/        # Optional screenshots
    *.apk               # APK files (managed by publish workflow)
index.json              # Generated app index (do not edit manually)
scripts/
  rebuild-index.py      # Regenerates index.json from apps/*/metadata.json
.github/workflows/
  publish.yml           # Reusable workflow_call — publish a new APK version
  pages.yml             # Deploys to GitHub Pages on every push to main
```

## Adding a new app

1. Create `apps/<your-app>/metadata.json` (see lifeforge for example)
2. Add an `icon.png`
3. In your app repo, add `.github/workflows/publish-to-store.yml` calling the reusable workflow

## Reusable publish workflow

```yaml
# In your app repo:
jobs:
  publish:
    uses: exisz/apps-repo/.github/workflows/publish.yml@main
    with:
      app_id: au.com.rollersoft.yourapp
      app_dir: yourapp
      apk_url: ${{ needs.build.outputs.apk_url }}
      version_code: ${{ needs.build.outputs.version_code }}
      version_name: ${{ needs.build.outputs.version_name }}
      changelog: "Your changelog here"
    secrets:
      APPS_REPO_PAT: ${{ secrets.APPS_REPO_PAT }}
```

> **Required secret**: `APPS_REPO_PAT` — a PAT with `contents: write` on this repo. Set it in your app repo's secrets.

---

## Onboarding a new project in 3 steps {#onboarding}

### Step 1: Create app metadata in apps-repo

```bash
mkdir -p apps/<your-app>
# Create apps/<your-app>/metadata.json (copy from apps/lifeforge/metadata.json)
# Add icon.png (512×512 recommended)
# Commit and push to main
```

### Step 2: Add publish workflow to your app repo

Create `.github/workflows/publish-to-store.yml`:

```yaml
name: Publish to apps-repo

on:
  release:
    types: [published]

jobs:
  publish:
    uses: exisz/apps-repo/.github/workflows/publish.yml@main
    with:
      app_id: au.com.rollersoft.yourapp
      app_dir: yourapp
      apk_url: ${{ github.event.release.assets[0].browser_download_url }}
      version_code: ${{ github.run_number }}
      version_name: ${{ github.event.release.tag_name }}
      changelog: ${{ github.event.release.body }}
    secrets:
      APPS_REPO_PAT: ${{ secrets.APPS_REPO_PAT }}
```

### Step 3: Set the `APPS_REPO_PAT` secret

1. Go to [GitHub → Settings → Developer Settings → Personal access tokens](https://github.com/settings/tokens?type=beta)
2. Create a fine-grained PAT named `apps-repo-publish-from-<your-app>`
3. Scope: **Contents → Read and write** on `exisz/apps-repo` only
4. Set it as a secret in your app repo:
   ```bash
   gh secret set APPS_REPO_PAT --repo exisz/<your-app> --body <token>
   ```

That's it — every new GitHub Release will automatically push the APK to apps-repo and update the index.
