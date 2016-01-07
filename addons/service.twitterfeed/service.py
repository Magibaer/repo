#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, sys, os, urlparse
import xbmc ,xbmcgui, xbmcaddon,xbmcvfs
import urllib2,urllib, zlib,json
import pyxbmct.addonwindow as pyxbmct 
import twitter,shutil
import webbrowser
import re
from requests_oauthlib import OAuth1Session
from thread import start_new_thread
from requests.packages import urllib3
import math

urllib3.disable_warnings()

REQUEST_TOKEN_URL = 'https://api.twitter.com/oauth/request_token'
ACCESS_TOKEN_URL = 'https://api.twitter.com/oauth/access_token'
AUTHORIZATION_URL = 'https://api.twitter.com/oauth/authorize'
SIGNIN_URL = 'https://api.twitter.com/oauth/authenticate'
consumer_key = "X54OL8ozrRMQWmYrQJV2Ihirr"
consumer_secret = "0RHD0CRm7noPvwVYvPL5FAaqazBu49JUecUN7tWam7yaMqeLZi"
oauth_token=""
oauth_token_secret=""

__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__addondir__    = xbmc.translatePath( __addon__.getAddonInfo('path') )
__background__ = os.path.join(__addondir__,"bg.png")

blackList = [];

def showTweet(tweet):
    if xbmc.getCondVisibility('Pvr.IsPlayingTv'):
        startold=99999     
        start=xbmc.Player(xbmc.PLAYER_CORE_AUTO).getTime()
        if start < startold :
          startold=start
        xbmc.Player(xbmc.PLAYER_CORE_AUTO).setSubtitles(temp+"/x.ass")
        f = open(temp+"/tweet.ass", 'w')            
        f.write("﻿[Script Info]\n")
        f.write("﻿Title: Twitter\n")
        f.write("﻿ScriptType: v4.00+ \n")
        f.write("[V4+ Styles]\n")
        f.write("Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n")
        f.write("Style: Default,Arial,12,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,1,2,10,10,10,1\n")
        f.write("[Events]\n")
        f.write("Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        tw=unicode(tweet).encode('utf-8')      
        xbmc.log("Tweet:" +tw)        
        f.write("Dialogue: 0,0:0:5.00,9:1:50.00,Default,,0000,0000,0000,,{\\a6}"+tw+"\n")            
        f.write("Dialogue: 0,1:0:5.00,1:0:50.00,Default,,0000,0000,0000,,{\\a6}end\n")            
        f.close()        
        xbmc.Player(xbmc.PLAYER_CORE_AUTO).showSubtitles(True)
        xbmc.Player(xbmc.PLAYER_CORE_AUTO).setSubtitles(temp+"/tweet.ass")        
        time.sleep(10)
        xbmc.Player(xbmc.PLAYER_CORE_AUTO).showSubtitles(False)
         

    
def get_access_token(consumer_key, consumer_secret,browser="no"):
    oauth_client = OAuth1Session(consumer_key, client_secret=consumer_secret)

    xbmc.log("Requesting temp token from Twitter")

    try:
        resp = oauth_client.fetch_request_token(REQUEST_TOKEN_URL)
    except ValueError, e:
        xbmc.log("Invalid respond from Twitter requesting temp token: %s" % e)
        return
    url = oauth_client.authorization_url(AUTHORIZATION_URL)
    
    if browser=="yes":
       webbrowser.open(url)
    else :       
      xbmc.log("URL ---> "+url)
      dialog = xbmcgui.Dialog()
      dialog.ok("Bitte URL im Browser Aufrufen", url[:40] +"\n"+ url[40:80] +"\n" +url[80:120] )
    keyboard = xbmc.Keyboard('')
    keyboard.setHeading('Twitter Pin Eingeben')
    keyboard.doModal()
    if (keyboard.isConfirmed()):
      PIN=keyboard.getText()
    else:
      PIN='0000'
    if  PIN=='0000':
       return 1
    xbmc.log("PIn: "+ PIN)
    oauth_client = OAuth1Session(consumer_key, client_secret=consumer_secret,
                                 resource_owner_key=resp.get('oauth_token'),
                                 resource_owner_secret=resp.get('oauth_token_secret'),
                                 verifier=PIN
    )
    try:
        resp = oauth_client.fetch_access_token(ACCESS_TOKEN_URL)
    except ValueError, e:  
         return 1   
    xbmc.log(" Setze oauth"   )
    xbmc.log(resp.get('oauth_token'))
    xbmc.log(resp.get('oauth_token_secret'))
    global oauth_token
    global oauth_token_secret
    oauth_token= resp.get('oauth_token')
    oauth_token_secret=resp.get('oauth_token_secret') 
    f = open(temp+"init.ok", 'w')        
    zeile="oauth_token: "+ oauth_token +"#"    
    f.write(zeile)    
    zeile="oauth_token_secret: "+ oauth_token_secret +"#"
    xbmc.log("ZEILE2 : " + zeile)
    f.write(zeile)
    f.close()    


    


if __name__ == '__main__':
    senderold=""
    x=0    
    profile    = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")
    temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
    if not xbmcvfs.exists(temp):       
       xbmcvfs.mkdirs(temp)
    if not xbmcvfs.exists(temp+"/init.ok"):
      dialog = xbmcgui.Dialog()
      if dialog.yesno("message", "Twitter Auth im Browser?"):
        browser="yes"
      else:
        browser="no"      
      x=get_access_token(consumer_key, consumer_secret,browser)        
    else:
      f=xbmcvfs.File(temp+"/init.ok","r")   
      daten=f.read()
      match=re.compile('oauth_token: ([^#]+)', re.DOTALL).findall(daten)
      oauth_token=match[0]
      match=re.compile('oauth_token_secret: ([^#]+)', re.DOTALL).findall(daten)
      oauth_token_secret=match[0]
    monitor = xbmc.Monitor()
    xbmc.log("[CPT] CouchPotatoTweets starting")
    xbmc.log("oauth_token ::"+ oauth_token+"#")
    xbmc.log("oauth_token_secret ::"+ oauth_token_secret+"#")
    xbmc.log("consumer_key ::"+ consumer_key+"#")
    xbmc.log("consumer_secret ::"+ consumer_secret +"#")
    index = 0    
    api = twitter.Api(consumer_key=consumer_key,consumer_secret=consumer_secret,access_token_key=oauth_token,access_token_secret=oauth_token_secret)
    sinceid=0
    while not monitor.abortRequested():
    # Sleep/wait for abort for 5 seconds
      if monitor.waitForAbort(1):
        break
      xbmc.log("[CPT] running %s" % time.time())
      if xbmc.getCondVisibility('Pvr.IsPlayingTv'):
        now = xbmc.getInfoLabel('Player.Title')
        channel = xbmc.getInfoLabel('VideoPlayer.ChannelName')        
        if "Erste" in channel:
           channel="ard"
        
        if "DeutschlandsuchtdenSuperstar" in now:
            now="dsds"
        if "Alleswaszält" in now:
            now="awz"
        
        match=re.compile('([^-]+)', re.DOTALL).findall(now)        
        if match:
          now=match[0]
        match=re.compile('([^:]+)', re.DOTALL).findall(now)
        if match:
          now=match[0]
        now=now.replace(" ","")        
        now=now.replace("ä","ae") 
        channel=channel.replace(" HD","")
        channel=channel.replace(" ","")        
        if now :
          search="#"+ channel +" OR "+ "#"+ now
        else:
           search="#"+ channel                
        if index is 0:
          xbmc.log("SEARCH :"+ search + "\nID:" +str(sinceid))
          xbmc.log("[CPT] loading new data")
          if not senderold==channel:
              sinceid=0
              senderold=channel
          try:
            if sinceid==0:
               tweets=api.GetSearch(search,count=2)
            else:
               tweets=api.GetSearch(search,since_id=sinceid)              
            for tweet in tweets:
              #print name.text
              if not tweet.text in blackList:
                xbmc.log("--")
                text= tweet.user.name +":"+ tweet.text.replace("\n"," ")
                sinceid=tweet.id
                xbmc.log("######" + str(sinceid))
                showTweet(text)              
                blackList.append(tweet.text)
                time.sleep(6)
                break
          except:
            pass             
        index = index + 1
      else:
         sinceid=0
      if index>6:
        index = 0