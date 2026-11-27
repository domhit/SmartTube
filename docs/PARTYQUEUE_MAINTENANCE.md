# SmartTube PartyQueue maintenance guide

This fork tracks `yuliskov/SmartTube` and keeps the PartyQueue REST API, playback events, settings, signing and update channel as a small patch series.

## Current baseline

- Upstream remote: `https://github.com/yuliskov/SmartTube.git`
- Fork: `https://github.com/domhit/SmartTube.git`
- Maintained PartyQueue branch: `partyqueue-api`
- Current tested SmartTube base: `32.85`
- Current source `versionCode`: `2475`
- Last hardware-tested release: `partyqueue-32.85-v1.0.0-beta1`
- Update channel: `partyqueue-latest`
- Downloader code: `7029871`
- Temporary legacy migration channel: `partyqueue-prerelease-latest`
- Legacy Downloader code: `7001040` (migration only; do not use for new installations)
- Tag format: `partyqueue-<smarttube-version>-v<partyqueue-version>`

## Branch model

- `upstream/master` is the official SmartTube source.
- `origin/partyqueue-api` is the maintained and hardware-tested PartyQueue fork.
- `origin/update/partyqueue-<version>` is temporary and exists only while porting a new SmartTube upstream version.
- The fork intentionally has no `origin/master` branch.

## Update channel

PartyQueue uses one permanent update channel:

- Moving tag: `partyqueue-latest`
- Downloader code: `7029871`
- Permanent APK: `https://github.com/domhit/SmartTube/releases/download/partyqueue-latest/SmartTube_PartyQueue_latest.apk`
- Update manifest: `https://github.com/domhit/SmartTube/releases/download/partyqueue-latest/smarttube_partyqueue.json`

All new installations and all migrated devices use this channel. The APK is still built from SmartTube's `stbeta` flavor; "Release" means a tested PartyQueue integration, not the official SmartTube Stable flavor.

### One-time legacy migration bridge

The currently installed 32.85 / versionCode 2475 PartyQueue build still checks the former `partyqueue-prerelease-latest` URL. Therefore the one-time migration build uses versionCode `2476`, already contains the new `partyqueue-latest` URL, and is temporarily published to both moving tags.

After all maintained devices have updated to versionCode 2476 or newer:

1. Delete the visible `partyqueue-prerelease-latest` legacy release/tag.
2. Remove the legacy compatibility block from `.github/workflows/partyqueue-build.yml`.
3. Retire Downloader code `7001040`.
4. Keep Downloader code `7029871` as the only installation code.

## Before updating from upstream

```bash
git status
git fetch upstream --tags
git submodule update --init --recursive
git show upstream/master:smarttubetv/build.gradle | grep -E "versionCode|versionName"
```

The working tree must be clean. Record the current PartyQueue baseline and create a safety tag when appropriate.

## Future SmartTube upstream update workflow

1. Start from the tested PartyQueue branch:

```bash
git switch partyqueue-api
git pull
git status
```

2. Fetch official SmartTube and determine the new version:

```bash
git fetch upstream --tags
git show upstream/master:smarttubetv/build.gradle | grep -E "versionCode|versionName"
```

3. Create a temporary update branch **from `partyqueue-api`**:

```bash
git switch -c update/partyqueue-<new-smarttube-version>
git push -u origin update/partyqueue-<new-smarttube-version>
```

4. Merge the official upstream branch:

```bash
git merge upstream/master
```

5. Resolve conflicts by keeping current upstream playback changes and reapplying/preserving the PartyQueue REST API, playback events, PartyQueue settings, `domhit/SmartTube` update URLs, signing and release workflow. Never blindly choose `ours` or `theirs` for playback-controller conflicts.

6. Synchronize submodules after resolving the merge:

```bash
git submodule sync --recursive
git submodule update --init --recursive
```

7. Push the update branch and require a green signed `StbetaRelease` GitHub Actions build.

8. When the port is ready, publish the intended PartyQueue release tag and test the upgrade from the preceding installed PartyQueue build through SmartTube's built-in updater. Do not replace the installed app manually for this migration test.

9. Hardware validate REST, queue control and PartyQueue Events. At minimum verify `video_started`, `user_skip`, `sponsorblock_skip`, settings persistence, HTTP 200 connection test, and a normal playback transition.

10. Update this maintenance document with the tested SmartTube version and `versionCode`.

11. Merge `update/partyqueue-<version>` into `partyqueue-api`, require another green build, then delete the temporary update branch locally and remotely.

Historical PartyQueue implementation checkpoints are preserved through release tags and Git commit history rather than permanent feature/port branches.

## Mandatory validation

- GitHub Actions `StbetaRelease` build is green.
- APK is signed with the existing PartyQueue key.
- REST: playback state, queue, play, pause, seek and next.
- Events: `video_started`, `video_ended`, `user_skip`, `sponsorblock_skip`, and a fresh `session_id` after app restart.
- PartyQueue settings persist and connection test returns HTTP 200.
- Beta and stable `update_urls.xml` still point to `domhit/SmartTube`.
- Release contains `smarttube_partyqueue.json` and `SmartTube_PartyQueue_latest.apk`.
- In-app update from the preceding PartyQueue release succeeds and preserves settings.

## Versioning and releases

Every update release needs a strictly higher Android `versionCode`. `versionName` follows upstream SmartTube; the Git tag carries the PartyQueue integration version.

Example: `partyqueue-32.85-v1.0.0-beta1`

```bash
git tag -a partyqueue-<smarttube-version>-v<partyqueue-version> -m "SmartTube <smarttube-version> PartyQueue <partyqueue-version>"
git push origin partyqueue-<smarttube-version>-v<partyqueue-version>
```

Every published PartyQueue tag updates `partyqueue-latest`. There is no permanent prerelease channel.

The committed `versionCode` in `smarttubetv/build.gradle` must match the signed APK, `smarttube_partyqueue.json`, and generated release notes. Never override the release `versionCode` only inside GitHub Actions.

The moving release must be created with `--target "$GITHUB_SHA"` so that its Git tag, source commit, update manifest and APK assets refer to the same build.

## Likely conflict files

- `smarttubetv/build.gradle`
- `common/src/stbeta/res/values/update_urls.xml`
- `common/src/ststable/res/values/update_urls.xml`
- `common/.../PartyQueueSettingsPresenter.java`
- `common/.../partyqueue/*`
- `.github/workflows/partyqueue-build.yml`

Never replace the signing key during a routine upstream update. A different key prevents Android from installing the new APK as an update.
