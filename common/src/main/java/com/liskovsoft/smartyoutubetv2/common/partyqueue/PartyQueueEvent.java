package com.liskovsoft.smartyoutubetv2.common.partyqueue;

import org.json.JSONException;
import org.json.JSONObject;

public final class PartyQueueEvent {
    public static final String VIDEO_STARTED = "video_started";
    public static final String VIDEO_ENDED = "video_ended";
    public static final String USER_SKIP = "user_skip";
    public static final String SPONSORBLOCK_SKIP = "sponsorblock_skip";
    public static final String PAUSED = "paused";
    public static final String RESUMED = "resumed";

    private final String event;

    private String deviceId;
    private String sessionId;
    private String videoId;
    private String title;
    private String reason;
    private String category;

    private long positionMs = -1;
    private long durationMs = -1;
    private long fromMs = -1;
    private long toMs = -1;
    private long sequence;

    public PartyQueueEvent(String event) {
        this.event = event;
    }

    public PartyQueueEvent setDeviceId(String value) {
        deviceId = value;
        return this;
    }

    public PartyQueueEvent setSessionId(String value) {
        sessionId = value;
        return this;
    }

    public PartyQueueEvent setVideoId(String value) {
        videoId = value;
        return this;
    }

    public PartyQueueEvent setTitle(String value) {
        title = value;
        return this;
    }

    public PartyQueueEvent setReason(String value) {
        reason = value;
        return this;
    }

    public PartyQueueEvent setCategory(String value) {
        category = value;
        return this;
    }

    public PartyQueueEvent setPositionMs(long value) {
        positionMs = value;
        return this;
    }

    public PartyQueueEvent setDurationMs(long value) {
        durationMs = value;
        return this;
    }

    public PartyQueueEvent setFromMs(long value) {
        fromMs = value;
        return this;
    }

    public PartyQueueEvent setToMs(long value) {
        toMs = value;
        return this;
    }

    public PartyQueueEvent setSequence(long value) {
        sequence = value;
        return this;
    }

    public JSONObject toJson() throws JSONException {
        JSONObject root = new JSONObject();
        JSONObject device = new JSONObject();
        JSONObject video = new JSONObject();
        JSONObject playback = new JSONObject();

        root.put("protocol", 1);
        root.put("event", event);
        root.put("event_time_ms", System.currentTimeMillis());
        root.put("session_id", safe(sessionId));
        root.put("sequence", sequence);

        device.put("id", safe(deviceId));
        root.put("device", device);

        video.put("video_id", safe(videoId));
        video.put("title", safe(title));
        root.put("video", video);

        if (positionMs >= 0) {
            playback.put("position_ms", positionMs);
        }

        if (durationMs >= 0) {
            playback.put("duration_ms", durationMs);
        }

        if (fromMs >= 0) {
            playback.put("from_ms", fromMs);
        }

        if (toMs >= 0) {
            playback.put("to_ms", toMs);
        }

        root.put("playback", playback);

        if (reason != null) {
            root.put("reason", reason);
        }

        if (category != null) {
            root.put("category", category);
        }

        return root;
    }

    private static String safe(String value) {
        return value != null ? value : "";
    }
}