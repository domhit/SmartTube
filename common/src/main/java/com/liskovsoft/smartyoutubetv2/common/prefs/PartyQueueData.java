package com.liskovsoft.smartyoutubetv2.common.prefs;

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
