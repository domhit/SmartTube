#!/usr/bin/env python3
from pathlib import Path

def remove_file(path):
    p = Path(path)
    if p.exists():
        p.unlink()
        print("removed", path)

def replace(path, old, new):
    p = Path(path)
    if not p.exists(): return
    s = p.read_text(encoding="utf-8")
    if old in s:
        p.write_text(s.replace(old, new, 1), encoding="utf-8")
        print("reverted", path)

remove_file("common/src/main/java/com/liskovsoft/smartyoutubetv2/common/partyqueue/PartyQueueEvent.java")
remove_file("common/src/main/java/com/liskovsoft/smartyoutubetv2/common/partyqueue/PartyQueueEventClient.java")
remove_file("common/src/main/java/com/liskovsoft/smartyoutubetv2/common/partyqueue/PartyQueueEventController.java")

replace("common/src/main/java/com/liskovsoft/smartyoutubetv2/common/app/presenters/PlaybackPresenter.java",
        "import com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEventController;\n", "")
replace("common/src/main/java/com/liskovsoft/smartyoutubetv2/common/app/presenters/PlaybackPresenter.java",
        "        mEventListeners.add(new PartyQueueEventController(getContext()));\n", "")

for path in [
 "common/src/main/java/com/liskovsoft/smartyoutubetv2/common/app/models/playback/controllers/VideoLoaderController.java",
 "common/src/main/java/com/liskovsoft/smartyoutubetv2/common/app/models/playback/controllers/SponsorBlockController.java"]:
    replace(path, "import com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEvent;\n", "")
    replace(path, "import com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEventClient;\n", "")

p=Path("common/src/main/java/com/liskovsoft/smartyoutubetv2/common/app/models/playback/controllers/VideoLoaderController.java")
if p.exists():
 s=p.read_text(encoding="utf-8")
 s=s.replace("            sendPartyQueueUserSkip();\n", "")
 a=s.find("    private void sendPartyQueueUserSkip()")
 if a>=0:
  b=s.find("\n    }", a)+6
  s=s[:a]+s[b:]
 p.write_text(s,encoding="utf-8")

p=Path("common/src/main/java/com/liskovsoft/smartyoutubetv2/common/app/models/playback/controllers/SponsorBlockController.java")
if p.exists():
 s=p.read_text(encoding="utf-8")
 s=s.replace("        sendPartyQueueSponsorSkip(getPlayer().getPositionMs(), skipPosMs, category);\n", "")
 a=s.find("    private void sendPartyQueueSponsorSkip(")
 if a>=0:
  b=s.find("\n    }", a)+6
  s=s[:a]+s[b:]
 p.write_text(s,encoding="utf-8")
print("v1 rollback complete")

