#!/usr/bin/env python3
from pathlib import Path

def edit(path, operations):
    p=Path(path); s=p.read_text(encoding='utf-8'); original=s
    for old,new,label in operations:
        if new in s: continue
        if old not in s: raise SystemExit(f"Anchor not found ({label}) in {path}")
        s=s.replace(old,new,1)
    p.write_text(s,encoding='utf-8')
    print(('updated ' if s!=original else 'already patched ')+path)

edit('common/src/main/java/com/liskovsoft/smartyoutubetv2/common/app/presenters/PlaybackPresenter.java',[
('import com.liskovsoft.smartyoutubetv2.common.app.models.playback.controllers.SponsorBlockController;', 'import com.liskovsoft.smartyoutubetv2.common.app.models.playback.controllers.SponsorBlockController;\nimport com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEventController;', 'presenter import'),
('mEventListeners.add(new SponsorBlockController());', 'mEventListeners.add(new SponsorBlockController());\n        mEventListeners.add(new PartyQueueEventController(getContext()));', 'controller registration')])

edit('common/src/main/java/com/liskovsoft/smartyoutubetv2/common/app/models/playback/controllers/VideoLoaderController.java',[
('import com.liskovsoft.smartyoutubetv2.common.app.models.data.Video;', 'import com.liskovsoft.smartyoutubetv2.common.app.models.data.Video;\nimport com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEvent;\nimport com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEventClient;', 'loader imports'),
('''        } else {\n            loadNext();\n        }\n\n        return true;\n    }''','''        } else {\n            sendPartyQueueUserSkip();\n            loadNext();\n        }\n\n        return true;\n    }\n\n    private void sendPartyQueueUserSkip() {\n        if (getPlayer() == null || getVideo() == null) return;\n        Video video = getVideo();\n        PartyQueueEventClient.instance(getContext()).send(new PartyQueueEvent(PartyQueueEvent.USER_SKIP)\n                .setVideoId(video.videoId).setTitle(video.title)\n                .setPositionMs(getPlayer().getPositionMs()).setDurationMs(getPlayer().getDurationMs())\n                .setReason("next_clicked"));\n    }''','user next hook')])

edit('common/src/main/java/com/liskovsoft/smartyoutubetv2/common/app/models/playback/controllers/SponsorBlockController.java',[
('import com.liskovsoft.smartyoutubetv2.common.app.models.data.Video;', 'import com.liskovsoft.smartyoutubetv2.common.app.models.data.Video;\nimport com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEvent;\nimport com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEventClient;', 'sponsor imports'),
('''    private void simpleSkip(long skipPosMs) {''','''    private void sendPartyQueueSponsorSkip(long fromMs, long toMs, String category) {\n        if (getPlayer() == null || getVideo() == null) return;\n        Video video = getVideo();\n        PartyQueueEventClient.instance(getContext()).send(new PartyQueueEvent(PartyQueueEvent.SPONSORBLOCK_SKIP)\n                .setVideoId(video.videoId).setTitle(video.title).setFromMs(fromMs).setToMs(toMs)\n                .setPositionMs(fromMs).setDurationMs(getPlayer().getDurationMs())\n                .setCategory(category).setReason("sponsorblock"));\n    }\n\n    private void simpleSkip(long skipPosMs) {''','sponsor helper'),
('''    private void messageSkip(long skipPosMs, String category) {\n        if (mLastSkipPosMs == skipPosMs) {\n            return;\n        }''','''    private void messageSkip(long skipPosMs, String category) {\n        if (mLastSkipPosMs == skipPosMs) {\n            return;\n        }\n        sendPartyQueueSponsorSkip(getPlayer().getPositionMs(), skipPosMs, category);''','message skip hook'),
('''                option -> {\n                    // return to previous dialog or close if no other dialogs in stack\n                    dialogPresenter.goBack();\n                    setPositionMs(skipPosMs);''','''                option -> {\n                    sendPartyQueueSponsorSkip(getPlayer().getPositionMs(), skipPosMs, category);\n                    // return to previous dialog or close if no other dialogs in stack\n                    dialogPresenter.goBack();\n                    setPositionMs(skipPosMs);''','confirm skip hook')])
print('PartyQueue event hooks applied successfully.')
