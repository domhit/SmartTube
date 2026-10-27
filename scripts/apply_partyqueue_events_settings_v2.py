#!/usr/bin/env python3
from pathlib import Path

ROOT=Path('.')
BASE='common/src/main/java/com/liskovsoft/smartyoutubetv2/common'

def write(path, text):
 p=ROOT/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8');print('wrote',path)

def edit(path, old, new, label):
 p=ROOT/path;s=p.read_text(encoding='utf-8')
 if new in s: print('already patched',path,label);return
 if old not in s: raise SystemExit(f'Anchor not found: {label} in {path}')
 p.write_text(s.replace(old,new,1),encoding='utf-8');print('updated',path,label)

write(f'{BASE}/prefs/PartyQueueData.java',r'''package com.liskovsoft.smartyoutubetv2.common.prefs;

import android.content.Context;
import android.content.SharedPreferences;

public final class PartyQueueData {
 private static final String PREFS="partyqueue_events";
 private static PartyQueueData sInstance;
 private final SharedPreferences prefs;
 private PartyQueueData(Context c){prefs=c.getApplicationContext().getSharedPreferences(PREFS,Context.MODE_PRIVATE);}
 public static synchronized PartyQueueData instance(Context c){if(sInstance==null)sInstance=new PartyQueueData(c);return sInstance;}
 public boolean isEnabled(){return prefs.getBoolean("enabled",false);}
 public void setEnabled(boolean v){prefs.edit().putBoolean("enabled",v).apply();}
 public String getUrl(){return prefs.getString("url","");}
 public void setUrl(String v){prefs.edit().putString("url",normalize(v)).apply();}
 public String getDeviceId(){return prefs.getString("device_id","");}
 public void setDeviceId(String v){prefs.edit().putString("device_id",v==null?"":v.trim()).apply();}
 public String getToken(){return prefs.getString("token","");}
 public void setToken(String v){prefs.edit().putString("token",v==null?"":v.trim()).apply();}
 public boolean isConfigured(){return isEnabled()&&!getUrl().isEmpty()&&!getDeviceId().isEmpty()&&!getToken().isEmpty();}
 public String getEventUrl(){return getUrl().isEmpty()?"":getUrl()+"/api/smarttube/event";}
 public String getHealthUrl(){return getUrl().isEmpty()?"":getUrl()+"/api/smarttube/event/health";}
 private static String normalize(String s){if(s==null)return "";s=s.trim();while(s.endsWith("/"))s=s.substring(0,s.length()-1);return s;}
}
''')

write(f'{BASE}/partyqueue/PartyQueueEvent.java',r'''package com.liskovsoft.smartyoutubetv2.common.partyqueue;
import org.json.JSONException;import org.json.JSONObject;
public final class PartyQueueEvent {
 public static final String VIDEO_STARTED="video_started",VIDEO_ENDED="video_ended",USER_SKIP="user_skip",SPONSORBLOCK_SKIP="sponsorblock_skip",PAUSED="paused",RESUMED="resumed";
 private final String event;private String deviceId,videoId,title,reason,category;private long positionMs=-1,durationMs=-1,fromMs=-1,toMs=-1,sequence;
 public PartyQueueEvent(String v){event=v;} public PartyQueueEvent setDeviceId(String v){deviceId=v;return this;} public PartyQueueEvent setVideoId(String v){videoId=v;return this;} public PartyQueueEvent setTitle(String v){title=v;return this;} public PartyQueueEvent setReason(String v){reason=v;return this;} public PartyQueueEvent setCategory(String v){category=v;return this;} public PartyQueueEvent setPositionMs(long v){positionMs=v;return this;} public PartyQueueEvent setDurationMs(long v){durationMs=v;return this;} public PartyQueueEvent setFromMs(long v){fromMs=v;return this;} public PartyQueueEvent setToMs(long v){toMs=v;return this;} public PartyQueueEvent setSequence(long v){sequence=v;return this;}
 public JSONObject toJson()throws JSONException{JSONObject r=new JSONObject(),d=new JSONObject(),v=new JSONObject(),p=new JSONObject();r.put("protocol",1);r.put("event",event);r.put("event_time_ms",System.currentTimeMillis());r.put("sequence",sequence);d.put("id",safe(deviceId));r.put("device",d);v.put("video_id",safe(videoId));v.put("title",safe(title));r.put("video",v);if(positionMs>=0)p.put("position_ms",positionMs);if(durationMs>=0)p.put("duration_ms",durationMs);if(fromMs>=0)p.put("from_ms",fromMs);if(toMs>=0)p.put("to_ms",toMs);r.put("playback",p);if(reason!=null)r.put("reason",reason);if(category!=null)r.put("category",category);return r;}private static String safe(String v){return v!=null?v:"";}
}
''')

write(f'{BASE}/partyqueue/PartyQueueEventClient.java',r'''package com.liskovsoft.smartyoutubetv2.common.partyqueue;
import android.content.Context;import com.liskovsoft.sharedutils.mylogger.Log;import com.liskovsoft.smartyoutubetv2.common.prefs.PartyQueueData;import java.io.OutputStream;import java.net.HttpURLConnection;import java.net.URL;import java.nio.charset.StandardCharsets;import java.util.concurrent.ExecutorService;import java.util.concurrent.Executors;import java.util.concurrent.atomic.AtomicLong;
public final class PartyQueueEventClient {
 private static final String TAG=PartyQueueEventClient.class.getSimpleName();private static final ExecutorService EXECUTOR=Executors.newSingleThreadExecutor();private static final AtomicLong SEQ=new AtomicLong();private static PartyQueueEventClient instance;private final PartyQueueData data;
 private PartyQueueEventClient(Context c){data=PartyQueueData.instance(c);}public static synchronized PartyQueueEventClient instance(Context c){if(instance==null)instance=new PartyQueueEventClient(c);return instance;}
 public void send(PartyQueueEvent e){if(e==null||!data.isConfigured())return;e.setDeviceId(data.getDeviceId()).setSequence(SEQ.incrementAndGet());EXECUTOR.execute(()->request("POST",data.getEventUrl(),e));}
 public void test(Callback cb){if(data.getUrl().isEmpty()||data.getDeviceId().isEmpty()||data.getToken().isEmpty()){cb.done(false,"URL, Device ID und Token ausfüllen");return;}EXECUTOR.execute(()->{Result r=request("GET",data.getHealthUrl(),null);cb.done(r.ok,r.message);});}
 private Result request(String method,String url,PartyQueueEvent e){HttpURLConnection c=null;try{c=(HttpURLConnection)new URL(url).openConnection();c.setRequestMethod(method);c.setConnectTimeout(1500);c.setReadTimeout(1500);c.setUseCaches(false);c.setRequestProperty("X-PartyQueue-Token",data.getToken());c.setRequestProperty("X-PartyQueue-Device",data.getDeviceId());if(e!=null){c.setDoOutput(true);c.setRequestProperty("Content-Type","application/json; charset=utf-8");byte[] b=e.toJson().toString().getBytes(StandardCharsets.UTF_8);c.setFixedLengthStreamingMode(b.length);try(OutputStream o=c.getOutputStream()){o.write(b);}}int code=c.getResponseCode();return new Result(code>=200&&code<300,"HTTP "+code);}catch(Exception x){Log.d(TAG,"PartyQueue request failed: %s",x.getMessage());return new Result(false,x.getMessage());}finally{if(c!=null)c.disconnect();}}
 public interface Callback{void done(boolean ok,String message);}private static final class Result{final boolean ok;final String message;Result(boolean o,String m){ok=o;message=m;}}
}
''')

write(f'{BASE}/partyqueue/PartyQueueEventController.java',r'''package com.liskovsoft.smartyoutubetv2.common.partyqueue;
import android.content.Context;import com.liskovsoft.smartyoutubetv2.common.app.models.data.Video;import com.liskovsoft.smartyoutubetv2.common.app.models.playback.BasePlayerController;
public final class PartyQueueEventController extends BasePlayerController {private final PartyQueueEventClient client;private String started;private boolean playing,ended;public PartyQueueEventController(Context c){client=PartyQueueEventClient.instance(c);}@Override public void onNewVideo(Video v){ended=false;playing=false;}@Override public void onVideoLoaded(Video v){ended=false;}@Override public void onPlay(){Video v=getVideo();if(v==null||getPlayer()==null||v.videoId==null)return;if(!v.videoId.equals(started)){send(PartyQueueEvent.VIDEO_STARTED,"player_started");started=v.videoId;ended=false;}else if(!playing)send(PartyQueueEvent.RESUMED,"player_resumed");playing=true;}@Override public void onPause(){if(!playing)return;send(PartyQueueEvent.PAUSED,"player_paused");playing=false;}@Override public void onPlayEnd(){if(ended)return;send(PartyQueueEvent.VIDEO_ENDED,"natural_end");ended=true;playing=false;}@Override public void onEngineReleased(){started=null;playing=false;ended=false;}private void send(String t,String r){Video v=getVideo();if(v==null||getPlayer()==null)return;client.send(new PartyQueueEvent(t).setVideoId(v.videoId).setTitle(v.title).setPositionMs(getPlayer().getPositionMs()).setDurationMs(getPlayer().getDurationMs()).setReason(r));}}
''')

write(f'{BASE}/app/presenters/settings/PartyQueueSettingsPresenter.java',r'''package com.liskovsoft.smartyoutubetv2.common.app.presenters.settings;
import android.content.Context;import com.liskovsoft.sharedutils.helpers.MessageHelpers;import com.liskovsoft.smartyoutubetv2.common.app.models.playback.ui.UiOptionItem;import com.liskovsoft.smartyoutubetv2.common.app.presenters.AppDialogPresenter;import com.liskovsoft.smartyoutubetv2.common.app.presenters.base.BasePresenter;import com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEventClient;import com.liskovsoft.smartyoutubetv2.common.prefs.PartyQueueData;import com.liskovsoft.smartyoutubetv2.common.utils.SimpleEditDialog;
public final class PartyQueueSettingsPresenter extends BasePresenter<Void>{private final PartyQueueData data;private PartyQueueSettingsPresenter(Context c){super(c);data=PartyQueueData.instance(c);}public static PartyQueueSettingsPresenter instance(Context c){return new PartyQueueSettingsPresenter(c);}public void show(){AppDialogPresenter p=AppDialogPresenter.instance(getContext());p.appendSingleSwitch(UiOptionItem.from("PartyQueue Events aktivieren",o->data.setEnabled(o.isSelected()),data.isEnabled()));p.appendSingleButton(UiOptionItem.from("PartyQueue URL: "+shown(data.getUrl()),o->edit("PartyQueue URL",data.getUrl(),data::setUrl)));p.appendSingleButton(UiOptionItem.from("Device ID: "+shown(data.getDeviceId()),o->edit("Device ID",data.getDeviceId(),data::setDeviceId)));p.appendSingleButton(UiOptionItem.from("Event Token: "+(data.getToken().isEmpty()?"nicht gesetzt":"********"),o->edit("Event Token",data.getToken(),data::setToken)));p.appendSingleButton(UiOptionItem.from("Verbindung testen",o->PartyQueueEventClient.instance(getContext()).test((ok,msg)->MessageHelpers.showLongMessage(getContext(),(ok?"PartyQueue erreichbar: ":"PartyQueue Fehler: ")+msg))));p.showDialog("PartyQueue");}private void edit(String title,String value,Save save){SimpleEditDialog.show(getContext(),title,value,save::save);}private static String shown(String v){return v==null||v.isEmpty()?"nicht gesetzt":v;}private interface Save{void save(String value);}}
''')

# Existing-file hooks. The old v1 must be rolled back first.
edit(f'{BASE}/app/presenters/PlaybackPresenter.java','import com.liskovsoft.smartyoutubetv2.common.app.models.playback.controllers.SponsorBlockController;','import com.liskovsoft.smartyoutubetv2.common.app.models.playback.controllers.SponsorBlockController;\nimport com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEventController;','event controller import')
edit(f'{BASE}/app/presenters/PlaybackPresenter.java','mEventListeners.add(new SponsorBlockController());','mEventListeners.add(new SponsorBlockController());\n        mEventListeners.add(new PartyQueueEventController(getContext()));','event controller registration')
edit(f'{BASE}/app/presenters/settings/GeneralSettingsPresenter.java','import com.liskovsoft.smartyoutubetv2.common.prefs.PlayerTweaksData;','import com.liskovsoft.smartyoutubetv2.common.prefs.PlayerTweaksData;\nimport com.liskovsoft.smartyoutubetv2.common.app.presenters.settings.PartyQueueSettingsPresenter;','settings import')
edit(f'{BASE}/app/presenters/settings/GeneralSettingsPresenter.java','        appendBootToSection(settingsPresenter);','        settingsPresenter.appendSingleButton(UiOptionItem.from("PartyQueue", option -> PartyQueueSettingsPresenter.instance(getContext()).show()));\n        appendBootToSection(settingsPresenter);','settings page entry')
edit(f'{BASE}/app/models/playback/controllers/VideoLoaderController.java','import com.liskovsoft.smartyoutubetv2.common.app.models.data.Video;','import com.liskovsoft.smartyoutubetv2.common.app.models.data.Video;\nimport com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEvent;\nimport com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEventClient;','loader imports')
edit(f'{BASE}/app/models/playback/controllers/VideoLoaderController.java','            loadNext();','            sendPartyQueueUserSkip();\n            loadNext();','user skip call')
edit(f'{BASE}/app/models/playback/controllers/VideoLoaderController.java','\n    private void loadNext() {','\n    private void sendPartyQueueUserSkip(){if(getPlayer()==null||getVideo()==null)return;Video v=getVideo();PartyQueueEventClient.instance(getContext()).send(new PartyQueueEvent(PartyQueueEvent.USER_SKIP).setVideoId(v.videoId).setTitle(v.title).setPositionMs(getPlayer().getPositionMs()).setDurationMs(getPlayer().getDurationMs()).setReason("next_clicked"));}\n\n    private void loadNext() {','user skip method')
edit(f'{BASE}/app/models/playback/controllers/SponsorBlockController.java','import com.liskovsoft.smartyoutubetv2.common.app.models.data.Video;','import com.liskovsoft.smartyoutubetv2.common.app.models.data.Video;\nimport com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEvent;\nimport com.liskovsoft.smartyoutubetv2.common.partyqueue.PartyQueueEventClient;','sponsor imports')
edit(f'{BASE}/app/models/playback/controllers/SponsorBlockController.java','\n    private void simpleSkip(long skipPosMs) {','\n    private void sendPartyQueueSponsorSkip(long from,long to,String category){if(getPlayer()==null||getVideo()==null)return;Video v=getVideo();PartyQueueEventClient.instance(getContext()).send(new PartyQueueEvent(PartyQueueEvent.SPONSORBLOCK_SKIP).setVideoId(v.videoId).setTitle(v.title).setFromMs(from).setToMs(to).setPositionMs(from).setDurationMs(getPlayer().getDurationMs()).setCategory(category).setReason("sponsorblock"));}\n\n    private void simpleSkip(long skipPosMs) {','sponsor helper')
edit(f'{BASE}/app/models/playback/controllers/SponsorBlockController.java','    private void messageSkip(long skipPosMs, String category) {\n        if (mLastSkipPosMs == skipPosMs) {\n            return;\n        }','    private void messageSkip(long skipPosMs, String category) {\n        if (mLastSkipPosMs == skipPosMs) {\n            return;\n        }\n        sendPartyQueueSponsorSkip(getPlayer().getPositionMs(), skipPosMs, category);','sponsor msg hook')
print('v2 PartyQueue settings and event integration applied')

