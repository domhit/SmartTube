# SmartTube PartyQueue maintenance guide

This fork tracks `yuliskov/SmartTube` and keeps the PartyQueue REST API, playback events, settings, signing and update channel as a small patch series.

## Current baseline

- Upstream remote: `https://github.com/yuliskov/SmartTube.git`
- Fork: `https://github.com/domhit/SmartTube.git`
- Maintained PartyQueue branch: `partyqueue-api`
- Historical tested branch: `port/partyqueue-events`
- Historical REST-only checkpoint: `port/rest-api-5797`
- Current tested SmartTube base: `32.85`
- Current source `versionCode`: `2475`
- Last hardware-tested release: `partyqueue-32.85-v1.0.0-beta1`
- Prerelease update channel: `partyqueue-prerelease-latest`
- Permanent Downloader code: `7001040`
- Tag format: `partyqueue-<smarttube-version>-v<partyqueue-version>`

The Downloader code `7001040` points to the permanent prerelease APK:

`https://github.com/domhit/SmartTube/releases/download/partyqueue-prerelease-latest/SmartTube_PartyQueue_latest.apk`

Existing PartyQueue SmartTube installations should normally use the built-in updater instead of reinstalling the APK manually.

## Before updating from upstream

```bash
git status
git fetch upstream --tags
git submodule update --init --recursive
git show upstream/master:smarttubetv/build.gradle | grep -E "versionCode|versionName"
```

The working tree must be clean. Record the current PartyQueue baseline and create a safety tag when appropriate.

## Recommended upstream update procedure

Do not merge a new upstream directly into the tested PartyQueue branch. Create a fresh port branch from the new upstream commit:

```bash
git switch partyqueue-api
git pull
git fetch upstream --tags
git switch -c update/partyqueue-<new-smarttube-version> upstream/master
git submodule update --init --recursive
```

Port and validate in this order:

1. REST API from PR #5797 and its hardening commits.
2. PartyQueue playback event integration.
3. PartyQueue settings and connection test.
4. PartyQueue update URLs.
5. GitHub Actions signing, update manifest and moving release channel.

Use the historical commits on `port/rest-api-5797` and `port/partyqueue-events` as the source of truth. Cherry-pick when clean; otherwise port manually and preserve one focused commit per layer.

## Mandatory validation

- GitHub Actions `StbetaRelease` build is green.
- APK is signed with the existing PartyQueue key.
- REST: playback state, queue, play, pause, seek and next.
- Events: `video_started`, `video_ended`, `user_skip`, `sponsorblock_skip`, and a fresh `session_id` after app restart.
- PartyQueue settings persist and connection test returns HTTP 200.
- Beta and stable `update_urls.xml` still point to `domhit/SmartTube`.
- Release contains `smarttube_partyqueue.json` and `SmartTube_PartyQueue_latest.apk`.
- In-app update from the preceding PartyQueue release succeeds and preserves settings.

## SmartTube 32.85 hardware validation

Hardware tested on `ke75`:

- In-app update from SmartTube PartyQueue 32.83 / versionCode 2474 to 32.85 / versionCode 2475 succeeded.
- Existing PartyQueue settings were preserved.
- REST API connection test returned HTTP 200.
- REST playback and SmartTube queue access worked.
- `video_started` events worked.
- `user_skip` events worked and produced `skipped` history.
- `sponsorblock_skip` events worked.
- Event session and sequence handling worked after the update.

## Versioning and releases

Every update release needs a strictly higher Android `versionCode`. `versionName` follows upstream SmartTube; the Git tag carries the PartyQueue integration version.

Example: `partyqueue-32.85-v1.0.0-beta1`

```bash
git tag -a partyqueue-<smarttube-version>-v<partyqueue-version> -m "SmartTube <smarttube-version> PartyQueue <partyqueue-version>"
git push origin partyqueue-<smarttube-version>-v<partyqueue-version>
```

Prerelease tags update `partyqueue-prerelease-latest`; final tags update `partyqueue-latest`.

The committed `versionCode` in `smarttubetv/build.gradle` must match the version used by the signed APK and `smarttube_partyqueue.json`. Do not override the release `versionCode` only inside GitHub Actions.

The moving release must be created with `--target "$GITHUB_SHA"` so that its Git tag, source commit, update manifest and APK assets refer to the same build.

## Likely conflict files

- `smarttubetv/build.gradle`
- `common/src/stbeta/res/values/update_urls.xml`
- `common/src/ststable/res/values/update_urls.xml`
- `common/.../PartyQueueSettingsPresenter.java`
- `common/.../partyqueue/*`
- `.github/workflows/partyqueue-build.yml`

Never replace the signing key during a routine upstream update. A different key prevents Android from installing the new APK as an update.
