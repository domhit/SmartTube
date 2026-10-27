package com.liskovsoft.smartyoutubetv2.common.partyqueue;

import android.content.Context;

import com.liskovsoft.smartyoutubetv2.common.app.models.data.Video;
import com.liskovsoft.smartyoutubetv2.common.app.models.playback.BasePlayerController;

public final class PartyQueueEventController extends BasePlayerController {
    private final PartyQueueEventClient mClient;

    private String mStartedVideoId;
    private String mStartedTitle;
    private long mStartedDurationMs;
    private long mLastPositionMs;

    private boolean mWasPlaying;
    private boolean mNaturalEndSent;

    private long mPauseStartedAtMs;
    private boolean mPauseEventSent;

    private static final long PAUSE_DEBOUNCE_MS = 500;

    public PartyQueueEventController(Context context) {
        mClient = PartyQueueEventClient.instance(context);
    }

    @Override
    public void onNewVideo(Video item) {
        mNaturalEndSent = false;
        mWasPlaying = false;
        mPauseStartedAtMs = 0;
        mPauseEventSent = false;
    }

    @Override
    public void onVideoLoaded(Video item) {
        mNaturalEndSent = false;

        if (item != null) {
            mStartedVideoId = item.videoId;
            mStartedTitle = item.title;
        }

        if (getPlayer() != null) {
            mStartedDurationMs = getPlayer().getDurationMs();
            mLastPositionMs = getPlayer().getPositionMs();
        }
    }

    @Override
    public void onPlay() {
        Video video = getVideo();

        if (video == null || getPlayer() == null || video.videoId == null) {
            return;
        }

        updatePlaybackSnapshot();

        boolean newVideo =
                mStartedVideoId == null ||
                !video.videoId.equals(mStartedVideoId);

        if (newVideo) {
            mStartedVideoId = video.videoId;
            mStartedTitle = video.title;
            mStartedDurationMs = getPlayer().getDurationMs();
            mLastPositionMs = getPlayer().getPositionMs();

            mClient.send(
                    new PartyQueueEvent(PartyQueueEvent.VIDEO_STARTED)
                            .setVideoId(mStartedVideoId)
                            .setTitle(mStartedTitle)
                            .setPositionMs(mLastPositionMs)
                            .setDurationMs(mStartedDurationMs)
                            .setReason("player_started")
            );

            mNaturalEndSent = false;
        } else if (!mWasPlaying) {
            /*
             * Nur ein echtes Resume veröffentlichen, wenn vorher
             * auch tatsächlich ein PAUSED-Event gesendet wurde.
             *
             * Kurze Pause/Play-Zyklen beim Seek werden damit
             * nicht als Resume an PartyQueue gemeldet.
             */
            if (mPauseEventSent) {
                mClient.send(
                        new PartyQueueEvent(PartyQueueEvent.RESUMED)
                                .setVideoId(mStartedVideoId)
                                .setTitle(mStartedTitle)
                                .setPositionMs(getPlayer().getPositionMs())
                                .setDurationMs(getPlayer().getDurationMs())
                                .setReason("player_resumed")
                );
            }
        }

        mPauseStartedAtMs = 0;
        mPauseEventSent = false;
        mWasPlaying = true;
    }

    @Override
    public void onPause() {
        if (!mWasPlaying || getPlayer() == null) {
            return;
        }

        updatePlaybackSnapshot();

        mPauseStartedAtMs = System.currentTimeMillis();
        mWasPlaying = false;

        /*
         * Noch KEIN paused senden.
         *
         * SmartTube erzeugt beim 10-Sekunden-Seek offenbar ebenfalls
         * kurz Pause/Play. Erst eine länger bestehende Pause soll
         * später als echtes PAUSED gelten.
         */
    }

    @Override
    public void onPlayEnd() {
        if (mNaturalEndSent) {
            return;
        }

        /*
         * WICHTIG:
         *
         * Hier NICHT getVideo() verwenden.
         * Beim onPlayEnd()-Callback kann SmartTube bereits das nächste
         * Video als aktuelles Video gesetzt haben.
         *
         * Deshalb verwenden wir ausschließlich den Snapshot des zuvor
         * gestarteten Videos.
         */

        long durationMs = mStartedDurationMs;
        long positionMs = mLastPositionMs;

        /*
         * Bei einem echten Ende darf die letzte bekannte Position auf
         * die bekannte Dauer angehoben werden.
         */
        if (durationMs > 0 && positionMs < durationMs) {
            positionMs = durationMs;
        }

        mClient.send(
                new PartyQueueEvent(PartyQueueEvent.VIDEO_ENDED)
                        .setVideoId(mStartedVideoId)
                        .setTitle(mStartedTitle)
                        .setPositionMs(positionMs)
                        .setDurationMs(durationMs)
                        .setReason("natural_end")
        );

        mNaturalEndSent = true;
        mWasPlaying = false;
        mPauseStartedAtMs = 0;
        mPauseEventSent = false;
    }

    @Override
    public void onEngineReleased() {
        mStartedVideoId = null;
        mStartedTitle = null;
        mStartedDurationMs = 0;
        mLastPositionMs = 0;

        mWasPlaying = false;
        mNaturalEndSent = false;

        mPauseStartedAtMs = 0;
        mPauseEventSent = false;
    }

    @Override
    public void onTickle() {
        if (getPlayer() == null) {
            return;
        }

        updatePlaybackSnapshot();

        /*
         * Pause-Debounce:
         * Erst nach 500 ms echter Pause ein PAUSED-Event senden.
         */
        if (!mWasPlaying &&
                !mPauseEventSent &&
                mPauseStartedAtMs > 0 &&
                System.currentTimeMillis() - mPauseStartedAtMs >= PAUSE_DEBOUNCE_MS) {

            mClient.send(
                    new PartyQueueEvent(PartyQueueEvent.PAUSED)
                            .setVideoId(mStartedVideoId)
                            .setTitle(mStartedTitle)
                            .setPositionMs(mLastPositionMs)
                            .setDurationMs(mStartedDurationMs)
                            .setReason("player_paused")
            );

            mPauseEventSent = true;
        }
    }

    private void updatePlaybackSnapshot() {
        if (getPlayer() == null) {
            return;
        }

        long positionMs = getPlayer().getPositionMs();
        long durationMs = getPlayer().getDurationMs();

        if (positionMs >= 0) {
            mLastPositionMs = positionMs;
        }

        if (durationMs > 0) {
            mStartedDurationMs = durationMs;
        }
    }
}