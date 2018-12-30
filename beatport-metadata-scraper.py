#!/usr/bin/python

import os
import sys
import requests
import json
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import re

#########################################
# Beatport class for searching and extracting track metadata
#########################################
class beatport(object):

    def __init__(self):
        print("Initializing Beatport search...")
        pass

    def query(self, artist, title):
        '''
        Search beatport for artist+title
        :return:
        Html response from server
        '''
        search = "https://pro.beatport.com/search?"
        value = urlencode({"q":str(artist + " " + title)}, safe='', encoding=None, errors=None)

        print("Request: " + search+value)
        return requests.get(search+value).text

    def jsonify(self, html):
        '''
        Beatport returns a script id 'data-objects' containing json of track metadata
        :return:
        Only json string
        '''
        begin = "window.Playables ="
        end = "};"
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.find("script",attrs={"id":"data-objects"})
        return tag.string[(tag.string.find(begin)+len(begin)):(tag.string.find(end)+1)]

    def jsonify_id(self, html):
        '''
        Beatport returns a product id containing json of the selected track metadata
        :return:
        Only json string
        '''
        begin = "window.ProductDetail ="
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.find('script', type='application/ld+json')
        tag = tag.find_next()
        return tag.string[(tag.string.find(begin)+len(begin)):]

    def get_artists(self, track_list):
        '''
        Json track data
        :return:
        Concatentated artists string
        '''        
        artist_str = ""
        artists_len = len(track_list['artists'])

        if artists_len == 1:
            artist_str = track_list['artists'][0]['name']
        elif artists_len > 1:
            for idx, l in enumerate(track_list['artists']):
                artist_str = artist_str + l['name']
                
                if idx < artists_len - 1:
                    artist_str = artist_str + ", "

        return artist_str

    def choose_track(self, track_list):
        '''
        Json array of track data
        :return:
        Single json string
        '''           
        track_list = [t for t in track_list['tracks'] if t['component'] != "None"]
        print('Search results:...' + str(len(track_list)))
        index = 1
        for t in track_list:
            artist_l = beat_api.get_artists(t)
            print(str(index) + "... " + artist_l + ": " + t['title'] + " - " + t['duration']['minutes'] + " - " + t['key'] + " - " + t['label']['name'] + " - " + str(t['id']))
            index = index + 1
        #########################################

        ##### Select the appropriate track ######
        str_idx = input("Which track index?...")
        while (not str_idx or str_idx == ''):
            str_idx = input("Which track index?...")
        idx = int(str_idx)
        if idx == 0:
            print("Exiting...")
            sys.exit()
        else:
            INDEX = idx - 1

        return track_list[INDEX]
# End Beatport class
#########################################        

######################################### 
# Google class for searching beatport tracks
#########################################
class google(object):

    def __init__(self):
        print("Initializing Google search...")
        pass

    def query(self, artist, title):
        '''
        Search for artist+title using restrictive domain
        :return:
        Html response from server
        '''
        source = "beatport.com"
        search = "https://www.google.com/search?"
        value = urlencode({"q":str(artist + " " + title) + " site:" + source}, safe='', encoding=None, errors=None)

        print("Request: " + search+value)
        return requests.get(search+value).text

    def jsonify(self, html):
        '''
        Google returns a list of results containing title and track metadata
        :return:
        Only json string
        '''
        soup = BeautifulSoup(html, 'lxml')

        #########################################
        ##### Parse Google search results ######
        titles = [ tit.text for tit in soup.findAll('h3', attrs={'class':'r'}) ]
        # urls = [ tit.text for tit in soup.findAll('cite') ]
        urls = [ tit.a['href'].split('&', 1)[0][7:] for tit in soup.findAll('h3', attrs={'class':'r'}) ]

        track_dur = re.compile(r'Length (\d+:\d+)[;\s]', re.IGNORECASE)
        times = [ track_dur.findall(dur.text)[0] if len(track_dur.findall(dur.text)) > 0  else 'n/a' for dur in soup.findAll('span', attrs={'class':'st'})]
        
        #########################################
        ##### Select the appropriate result #####
        index = 1
        for t, d, u in zip(titles, times, urls):
            print(str(index) + ". " + t + " : " + str(d) + " -> " + u)
            index = index + 1

        str_idx = input("Which search result?...")
        while (not str_idx or str_idx == ''):
            str_idx = input("Which search result?...")
        idx = int(str_idx)
        if idx == 0:
            print("Exiting...")
            sys.exit()
        else:
            INDEX = idx - 1
        url = urls[INDEX]
        #########################################

        #########################################
        #### Query beatport for specific url ####
        track_query = requests.get(url).text
        raw = beat_api.jsonify_id(track_query)
        #########################################
        return raw
# End Google class
#########################################

################ Input ##################
artist = None
track = None
delimiter = None
#########################################
search_google = False
search_str_arg_idx = 1

if sys.argv[1] == 'g':
   search_google = True
   search_str_arg_idx = 2

# If the command line arg has a hypen delimiter seperating artist and track print then set
if sys.argv[search_str_arg_idx].find(" - ") != -1:
    delimiter = " - "
    artist_and_title = [x.strip() for x in sys.argv[search_str_arg_idx].split(delimiter)]
    artist = artist_and_title[0]
    track = artist_and_title[1]

    print("Filename delimiter:\t'" + delimiter + "'")
    print('artist:\t\t\t' + artist )
    print('track:\t\t\t' + track)
else:
    print("No artist info supplied...searching for tracks.")

    artist = ''
    track = sys.argv[search_str_arg_idx].strip()
    print('track:\t\t\t' + track)
print()
print('Searching for "' + artist + '" -> "' + track + '"')
#########################################

########## Search Beatport  #############
## Or search Google with domain filter ##
beat_api = beatport()
data = None
if search_google:
    g_api = google()
    track_query = g_api.query(artist, track)
    raw = g_api.jsonify(track_query)
    data = json.loads(raw)

if not search_google:
    track_query = beat_api.query(artist, track)
    raw = beat_api.jsonify(track_query)
    track_list = json.loads(raw)
    data = beat_api.choose_track(track_list)

###### Write out json data to file ######
# with open('data.json', 'w') as outfile:
#     json.dump(raw, outfile)
#########################################

############ Print metadata #############
print()
print("Title: \t\t" + data['title'])

artist_l = beat_api.get_artists(data)

print("Artist(s): \t" + artist_l)
print("Duration: \t" + data['duration']['minutes'])
print("BPM: \t\t" + str(data['bpm']))
print("Key: \t\t" + str(data['key']))
print("Label: \t\t" + data['label']['name'] )
print("Format: \t" + data['audio_format'] )
print("Released: \t" + data['date']['released'])
print("Genre: \t\t" + data['genres'][0]['name'])
print("ID: \t\t" + str(data['id']))

# Download track art
img_dir = "imgs/" 
img_path = img_dir + data['title'] + ".jpg"
print("Saving albumart...")
response = requests.get(data['images']['large']['url'])
if response.ok:
    with open(img_path, 'wb') as f:
        f.write(response.content)
print("Finished!")
#########################################

########## Open artwork  ############
os.system('open "'+ img_path + '"')
#########################################