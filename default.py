#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import xbmcplugin
import xbmcaddon
import xbmcgui
import sys
import re
import os
import json

addon = xbmcaddon.Addon()
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
translation = addon.getLocalizedString
showSubtitles = addon.getSetting("showSubtitles") == "true"
forceViewMode = addon.getSetting("forceViewMode") == "true"
useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"
viewMode = str(addon.getSetting("viewMode"))
baseUrl = "http://www.ardmediathek.de"
defaultThumb = baseUrl+"/ard/static/pics/default/16_9/default_webM_16_9.jpg"
defaultBackground = "http://www.ard.de/pool/img/ard/background/base_xl.jpg"
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
addon_work_folder = xbmc.translatePath("special://profile/addon_data/"+addonID)
channelFavsFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/"+addonID+".favorites")
subFile = xbmc.translatePath("special://profile/addon_data/"+addonID+"/sub.srt")
thumbwidth = 1920;

if not os.path.isdir(addon_work_folder):
    os.mkdir(addon_work_folder)


def index():
    addDir(translation(30001), baseUrl+"/tv/Neueste-Videos/mehr?documentId=21282466", 'listVideos', "")
    addDir(translation(30002), baseUrl+"/tv/Meistabgerufene-Videos/mehr?documentId=21282514", 'listVideos', "")
#    addDir(translation(30010), baseUrl+"/ard/servlet/ajax-cache/3516188/view=switch/index.html", 'listVideos', "")
    addDir(translation(30014), "", 'listEinsLike', "")
    addDir(translation(30003), baseUrl+"/tv/Reportage-Doku/mehr?documentId=21301806", 'listVideos', "")
    addDir(translation(30004), baseUrl+"/tv/Film-Highlights/mehr?documentId=21301808", 'listVideos', "")
    addDir(translation(30005), "", 'listShowsAZMain', "")
    addDir(translation(30011), "", 'listShowsFavs', "")
    addDir(translation(30006), "", 'listCats', "")
    addDir(translation(30007), "", 'listDossiers', "")
    addDir(translation(30008), "", 'search', "")
    addLink(translation(30013), "", 'playLive', icon)
    xbmcplugin.endOfDirectory(pluginhandle)


def listShowsFavs():
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    if os.path.exists(channelFavsFile):
        fh = open(channelFavsFile, 'r')
        all_lines = fh.readlines()
        for line in all_lines:
            title = line[line.find("###TITLE###=")+12:]
            title = title[:title.find("#")]
            url = line[line.find("###URL###=")+10:]
            url = url[:url.find("#")]
            thumb = line[line.find("###THUMB###=")+12:]
            thumb = thumb[:thumb.find("#")]
            addShowFavDir(title, urllib.unquote_plus(url), "listShowVideos", thumb)
        fh.close()
    xbmcplugin.endOfDirectory(pluginhandle)


def listEinsLike():
    addDir(translation(30001), baseUrl+"/einslike/Neueste-Videos/mehr?documentId=21282466", 'listVideos', "")
    addDir(translation(30002), baseUrl+"/einslike/Meistabgerufene-Videos/mehr?documentId=21282464", 'listVideos', "")
#    addDir(translation(30010), baseUrl+"/ard/servlet/ajax-cache/3516156/view=switch/vflags=0-1,5-1/index.html", 'listVideos', "")
    addDir(translation(30015), baseUrl+"/einslike/Musik/mehr?documentId=21301894", 'listVideos', "")
    addDir(translation(30016), baseUrl+"/einslike/Leben/mehr?documentId=21301896", 'listVideos', "")
    addDir(translation(30017), baseUrl+"/einslike/Netz-Tech/mehr?documentId=21301898", 'listVideos', "")
    addDir(translation(30018), baseUrl+"/einslike/Info/mehr?documentId=21301900", 'listVideos', "")
    addDir(translation(30019), baseUrl+"/einslike/Spa%C3%9F-Fiktion/mehr?documentId=21301902", 'listVideos', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listDossiers():
    content = getUrl(baseUrl+"/tv")
    elements = content.split('<div class="con">')
    spl = elements[5].split('<div class="mediaCon">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        if "mediaA" in entry:
            match = re.compile('<a href="(.+?)" class="mediaLink">(.+?)alt="(.+?)" title="" data-ctrl-image(.+?)</a>', re.DOTALL).findall(entry)
            url = baseUrl+match[0][0].replace('&amp;', '&')
            title = cleanTitle(match[0][2])
            match = re.compile('<div class="textWrapper">(.+?)<p class="dachzeile">(.+?)</p>(.+?)<p class="subtitle">(.+?)</p>', re.DOTALL).findall(entry)
            duration = ""
            if match:
                date = match[0][1]
                duration = float(match[0][3][:2])
                title = date[:5]+" - "+title
            if duration == float('0'):
                duration = 1
            match = re.compile('<img class="img hideOnNoScript"(.+?)data-ctrl-image="{&#039;id&#039;:&#039;image(.+?)media&#039;,&#039;urlScheme&#039;:&#039;(.+?)&#039;}"/>', re.DOTALL).findall(entry)
            thumb = baseUrl+match[0][2].replace("##width##", str(thumbwidth))
            if "Livestream" not in title:
                addShowDir(title, url, 'listVideos', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShowsAZMain():
    addDir("0-9", "0-9", 'listShowsAZ', "")
    letters = [chr(i) for i in xrange(ord('a'), ord('z')+1)]
    for letter in letters:
        addDir(letter.upper(), letter.upper(), 'listShowsAZ', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listShowsAZ(letter):
    content = getUrl(baseUrl+"/tv/sendungen-a-z?buchstabe="+letter)
    spl = content.split('<div class="mediaCon">')
    for i in range(2, len(spl), 1):
        entry = spl[i]
        match = re.compile('<div class="textWrapper">(.+?)<a href="(.+?)" class="textLink">(.+?)<h4 class="headline">(.+?)</h4>(.+?)</a>', re.DOTALL).findall(entry)
        url = baseUrl+match[0][1]
        title = cleanTitle(match[0][3])
        match = re.compile('<img class="img hideOnNoScript"(.+?)data-ctrl-image="{&#039;id&#039;:&#039;image(.+?)media&#039;,&#039;urlScheme&#039;:&#039;(.+?)&#039;}"/>', re.DOTALL).findall(entry)
        addShowDir(title, url, 'listVideos', baseUrl+match[0][2].replace("##width##", str(thumbwidth)));
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listCats():
    content = getUrl(baseUrl)
    content = content[content.find('<div class="mt-reset mt-categories">'):]
    content = content[:content.find('</div>')]
    match = re.compile('<li><a href="(.+?)" title="">(.+?)</a></li>', re.DOTALL).findall(content)
    for url, title in match:
        id = url[url.find("documentId=")+11:]
        addDir(cleanTitle(title), id, 'listVideosMain', "", "")
    xbmcplugin.endOfDirectory(pluginhandle)


def listVideos(url):
    content = getUrl(url)
    spl = content.split('<div class="teaser"')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        if "mediaA" in entry:
            try:
                match = re.compile('<a href="(.+?)" class="mediaLink">(.+?)title="(.+?)" data-ctrl-image(.+?)</a>', re.DOTALL).findall(entry)
                match2 = re.compile('<a href="(.+?)" class="textLink">(.+?)class="headline">(.+?)</(.+?)</a>', re.DOTALL).findall(entry)
                url = baseUrl+match[0][0].replace('&amp;', '&')
                try:
                    title = cleanTitle(match2[0][2])
                except:
                    title = cleanTitle(match[0][2])
                match = re.compile('<div class="textWrapper">(.+?)<p class="dachzeile">(.+?)</p>(.+?)<p class="subtitle">(.+?)</p>', re.DOTALL).findall(entry)
                duration = ""
                if match:
                    date = match[0][1]
                    duration = float(match[0][3][:2])
                    try:
                        float(date[:2])
                        title = date[:5]+" - "+title
                    except ValueError:
                        title = cleanTitle(date) +" - "+title
                    
                if duration == float('0'):
                    duration = 1
                match = re.compile('<img class="img hideOnNoScript"(.+?)data-ctrl-image="{&#039;id&#039;:&#039;image(.+?)media&#039;,&#039;urlScheme&#039;:&#039;(.+?)&#039;}"/>', re.DOTALL).findall(entry)
                thumb = baseUrl+match[0][2].replace("##width##", str(thumbwidth))
                if "Livestream" not in title:
                    addLink(title, url, 'playVideo', thumb, duration)
            except:
                pass
    match = re.compile('<div class="entry" data-ctrl-(content(s?)|results)Loader-source="{&#039;pixValue&#039;:&#039;(.)&#039;}">\r\n            <a href="(.+?)">', re.DOTALL).findall(content)
    if match:
        addDir(translation(30009), baseUrl+match[len(match)-1][3].replace('&amp;', '&'), 'listVideos', "", "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(url):
    content = getUrl(url)
    match = re.compile('<div class="media mediaA" data-ctrl-player="{&#039;(.+?)&#039;,&#039;mcUrl&#039;:&#039;(.+?)&#039;(.+?)}">', re.DOTALL).findall(content)
    try:
        configContent = json.loads(getUrl(baseUrl+match[0][1]))
        if showSubtitles and configContent['_subtitleUrl'] != '':
            setSubtitle(baseUrl+configContent['_subtitleUrl'])
        
        bestqualityDefined = 0
        
        for media in configContent['_mediaArray']:
            if media['_plugin'] == 1:
                for (index, stream) in enumerate(media['_mediaStreamArray']):
                    if bestqualityDefined == 0 or bestquality['_quality'] < stream['_quality']:
                        bestquality = stream
                        bestqualityDefined = 1
        
        
        if bestqualityDefined == 0:
            xbmc.executebuiltin('XBMC.Notification(Unable to find stream.,The plugin needs a HTML5 player on the ardmediathek.de website.,15000)')
        else:
            try:
                url = bestquality['_stream'][0]
            except ValueError:
                url = bestquality['_stream']
            if isinstance(bestquality['_stream'], (list, tuple)):
                url = bestquality['_stream'][0]
            else:
                url = bestquality['_stream']
            if "?" in url:
                url = url[:url.find("?")]
            listitem = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    except IndexError:
        xbmc.executebuiltin('XBMC.Notification(Unable to find stream.,Is the access to the stream restricted (FSK)?,15000)')


def setSubtitle(url):
    if os.path.exists(subFile):
        os.remove(subFile)
    try:
        content = getUrl(url)
    except:
        content = ""
    if content:
        matchLine = re.compile('<p id=".+?" begin="1(.+?)" end="1(.+?)".+?>(.+?)</p>', re.DOTALL).findall(content)
        fh = open(subFile, 'a')
        count = 1
        for begin, end, line in matchLine:
            begin = "0"+begin.replace(".",",")[:-1]
            end = "0"+end.replace(".",",")[:-1]
            match = re.compile('<span(.+?)>', re.DOTALL).findall(line)
            for span in match:
                line = line.replace("<span"+span+">","")
            line = line.replace("<br />","\n").replace("</span>","").strip()
            fh.write(str(count)+"\n"+begin+" --> "+end+"\n"+cleanTitle(line)+"\n\n")
            count+=1
        fh.close()
        xbmc.sleep(1000)
        xbmc.Player().setSubtitles(subFile)


def queueVideo(url, name):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name)
    playlist.add(url, listitem)


def playLive():
    content = getUrl("http://live.daserste.de/de/livestream.xml")
    match = re.compile('<streamingUrlIPad>(.+?)</streamingUrlIPad>', re.DOTALL).findall(content)
    url = ""
    if match:
        url = match[0]
    if url:
        listitem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def search():
    keyboard = xbmc.Keyboard('', translation(30008))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        search_string = keyboard.getText().replace(" ", "+")
        listVideos(baseUrl+"/tv/suche?&searchText="+search_string)


def listVideosSearch(url):
    content = getUrl(url)
    spl = content.split('<div class="mt-media_item mt-media-item">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<a href="(.+?)" class="mt-fo_source" rel="(.+?)">(.+?)</a>', re.DOTALL).findall(entry)
        url = baseUrl+match[0][0]
        title = cleanTitle(match[0][2])
        match = re.compile('<p class="mt-source mt-tile-view_hide">aus: (.+?)</p>', re.DOTALL).findall(entry)
        show = ""
        if match:
            show = match[0]
        match = re.compile('<span class="mt-channel mt-tile-view_hide">(.+?)</span>', re.DOTALL).findall(entry)
        channel = ""
        if match:
            channel = match[0]
        match = re.compile('<span class="mt-airtime">(.+?) · (.+?) min</span>', re.DOTALL).findall(entry)
        duration = ""
        date = ""
        if match:
            date = match[0][0]
            duration = match[0][1]
            title = date[:5]+" - "+title
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = getBetterThumb(baseUrl+match[0])
        desc = cleanTitle(date+" - "+show+" ("+channel+")")
        if "Livestream" not in title:
            addLink(title, url, 'playVideo', thumb, duration, desc)
    match = re.compile('<a  href="(.+?)"  class=".+?" rel=".+?">(.+?)</a>', re.DOTALL).findall(content)
    for url, title in match:
        if title == "Weiter":
            addDir(translation(30009), baseUrl+url.replace("&amp;", "&"), 'listVideosSearch', "", "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode == True:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#034;", "\"").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö").replace("&eacute;", "é").replace("&egrave;", "è")
    title = title.replace("&#x00c4;","Ä").replace("&#x00e4;","ä").replace("&#x00d6;","Ö").replace("&#x00f6;","ö").replace("&#x00dc;","Ü").replace("&#x00fc;","ü").replace("&#x00df;","ß")
    title = title.replace("&apos;","'").strip()
    return title


def cleanUrl(title):
    return title.replace(" ", "%20").replace("%F6", "ö").replace("%FC", "ü").replace("%E4", "ä").replace("%26", "&").replace("%C4", "Ä").replace("%D6", "Ö").replace("%DC", "Ü")


def getUrl(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:19.0) Gecko/20100101 Firefox/19.0')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link


def favs(param):
    mode = param[param.find("###MODE###=")+11:]
    mode = mode[:mode.find("###")]
    channelEntry = param[param.find("###TITLE###="):]
    if mode == "ADD":
        if os.path.exists(channelFavsFile):
            fh = open(channelFavsFile, 'r')
            content = fh.read()
            fh.close()
            if content.find(channelEntry) == -1:
                fh = open(channelFavsFile, 'a')
                fh.write(channelEntry+"\n")
                fh.close()
        else:
            fh = open(channelFavsFile, 'a')
            fh.write(channelEntry+"\n")
            fh.close()
    elif mode == "REMOVE":
        refresh = param[param.find("###REFRESH###=")+14:]
        refresh = refresh[:refresh.find("#")]
        fh = open(channelFavsFile, 'r')
        content = fh.read()
        fh.close()
        entry = content[content.find(channelEntry):]
        fh = open(channelFavsFile, 'w')
        fh.write(content.replace(channelEntry+"\n", ""))
        fh.close()
        if refresh == "TRUE":
            xbmc.executebuiltin("Container.Refresh")


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage, duration="", desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Duration": duration, "Plot": desc})
    liz.setProperty('IsPlayable', 'true')
    if useThumbAsFanart:
        if not iconimage or iconimage==icon:
            iconimage = defaultBackground
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultBackground)
    liz.addContextMenuItems([(translation(30012), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, desc=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    if useThumbAsFanart:
        if not iconimage:
            iconimage = defaultBackground
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultBackground)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if useThumbAsFanart:
        if not iconimage:
            iconimage = defaultBackground
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultBackground)
    playListInfos = "###MODE###=ADD###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30028), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addShowFavDir(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=defaultThumb, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    if useThumbAsFanart:
        if not iconimage:
            iconimage = defaultBackground
        liz.setProperty("fanart_image", iconimage)
    else:
        liz.setProperty("fanart_image", defaultBackground)
    playListInfos = "###MODE###=REMOVE###REFRESH###=TRUE###TITLE###="+name+"###URL###="+urllib.quote_plus(url)+"###THUMB###="+iconimage+"###END###"
    liz.addContextMenuItems([(translation(30029), 'RunPlugin(plugin://'+addonID+'/?mode=favs&url='+urllib.quote_plus(playListInfos)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))

if mode == 'listChannel':
    listChannel(url)
elif mode == 'listVideos':
    listVideos(url)
elif mode == 'listVideosMain':
    listVideosMain(url)
elif mode == 'listDossiers':
    listDossiers()
elif mode == 'listEinsLike':
    listEinsLike()
elif mode == 'listShowsFavs':
    listShowsFavs()
elif mode == 'listVideosDossier':
    listVideosDossier(url)
elif mode == 'listVideosSearch':
    listVideosSearch(url)
elif mode == 'listShowsAZMain':
    listShowsAZMain()
elif mode == 'listShowsAZ':
    listShowsAZ(url)
elif mode == 'listCats':
    listCats()
elif mode == 'listShowVideos':
    listShowVideos(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == "queueVideo":
    queueVideo(url, name)
elif mode == 'playLive':
    playLive()
elif mode == 'search':
    search()
elif mode == 'favs':
    favs(url)
else:
    index()
