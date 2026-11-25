# SmartTube PartyQueue maintenance guide

This fork tracks `yuliskov/SmartTube` and keeps the PartyQueue REST API, playback events, settings, signing and update channel as a small patch series.

## Current baseline

- Upstream remote: `https://github.com/yuliskov/SmartTube.git`
- Fork: `https://github.com/domhit/SmartTube.git`
- Development branch: `port/partyqueue-events`
- REST-only checkpoint: `port/rest-api-5797`
- Tag format: `partyqueue-<smarttube-version>-v<partyqueue-version>`
- Current SmartTube base: `32.83`

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
git switch port/partyqueue-events
git pull
git fetch upstream --tags
git switch -c port/partyqueue-<new-smarttube-version> upstream/master
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

## Versioning and releases

Every update release needs a strictly higher Android `versionCode`. `versionName` follows upstream SmartTube; the Git tag carries the PartyQueue integration version.

Example: `partyqueue-32.83-v1.0.0-alpha3`

```bash
git tag -a partyqueue-<smarttube-version>-v<partyqueue-version> -m "SmartTube <smarttube-version> PartyQueue <partyqueue-version>"
git push origin partyqueue-<smarttube-version>-v<partyqueue-version>
```

Prerelease tags update `partyqueue-prerelease-latest`; final tags update `partyqueue-latest`.

## Likely conflict files

- `smarttubetv/build.gradle`
- `common/src/stbeta/res/values/update_urls.xml`
- `common/src/ststable/res/values/update_urls.xml`
- `common/.../PartyQueueSettingsPresenter.java`
- `common/.../partyqueue/*`
- `.github/workflows/partyqueue-build.yml`

Never replace the signing key during a routine upstream update. A different key prevents Android from installing the new APK as an update.
