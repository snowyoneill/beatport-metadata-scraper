#!/usr/bin/python

import os
import sys
import requests
import json
# from urllib.parse import urlencode
try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode     

from bs4 import BeautifulSoup
import re

from fake_useragent import UserAgent
ua = UserAgent()

import datetime

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
        search = "https://beatport.com/search?"
        value = urlencode({"q":str(artist + " " + title)})

        print("Request: " + search+value)
        # return requests.get(search+value).text
        headers = {"User-Agent": ua.random}
        return requests.get(search+value, headers=headers).text

    def jsonify(self, html):
        '''
        Beatport returns a script id 'data-objects' containing json of track metadata
        :return:
        Only json string
        '''
        # begin = "window.Playables ="
        # end = "};"
        # soup = BeautifulSoup(html, "html.parser")
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.find('script', type='application/json')

        print("Dumping soup html...")
        with open("soup.html", "w") as file:
            file.write(str(soup))            

        # tag = soup.find("script",attrs={"id":"data-objects"})
        # return tag.string[(tag.string.find(begin)+len(begin)):(tag.string.find(end)+1)]

        return tag.string[0:len(tag.string)]

    def jsonify_id(self, html):
        '''
        Beatport returns a product id containing json of the selected track metadata
        :return:
        Only json string
        '''

        # begin = "window.ProductDetail ="
        soup = BeautifulSoup(html, "html.parser")
        tag = soup.find('script', type='application/json')
        # tag = tag.find_next()
        # return tag.string[(tag.string.find(begin)+len(begin)):]
        return tag.string[0:len(tag.string)]

    def get_artists(self, track_list):
        '''
        Json track data
        :return:
        Concatentated artists string
        '''        
        artist_str = ""
        artists_len = len(track_list['artists'])

        tag = 'name'
        if 'artist_name' in track_list['artists'][0]:
            tag = 'artist_name'

        if artists_len == 1:
            artist_str = track_list['artists'][0][tag]
        elif artists_len > 1:
            for idx, l in enumerate(track_list['artists']):
                artist_str = artist_str + l[tag]
                
                if idx < artists_len - 1:
                    artist_str = artist_str + ", "

        return artist_str

    def choose_track(self, track_list):
        '''
        Json array of track data
        :return:
        Single json string
        '''
        # track_list = track_list['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']
        track_list = [t for t in track_list['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['tracks']['data']]

        # for t in track_list:
        #     print(t)
        #     print("---")
        # print(track_list)
        # exit(0)

        print('Search results:...' + str(len(track_list)))
        index = 1
        for t in track_list:
            artist_l = beat_api.get_artists(t)
            # print(str(index) + "... " + artist_l + ": " + t['name'] + " (" + t['mix'] + ")" + " - " + t['duration']['minutes'] + " - " + t['key'] + " - " + t['label']['name'] + " - " + str(t['id']))
            print(str(index) + "... " + (t['release_date'])[:10] + " - " + ':'.join(str((datetime.timedelta(seconds=t['length']//1000))).split(':')[1:3])  + " - " + str(t['track_id']) + "\t- " + artist_l + " - " + t['track_name'] + "(" + t['mix_name'] + ") -> " + t['label']['label_name'])
            index = index + 1
        #########################################

        ##### Select the appropriate track ######
        validInput = False
        while(not validInput):
            str_idx = input("Which track index?...")
            if str_idx:
                idx = int(str_idx)
                if idx == 0:
                    break
                elif idx <= len(track_list):
                    INDEX = idx - 1
                    validInput = True
                else:
                    print("Invalid index...")
            else:
                break

        if not validInput:
            print("Exiting...")
            sys.exit()            

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
        value = urlencode({"q":str(artist + " " + title) + " site:" + source})

        print("Request: " + search+value)
        # return requests.get(search+value).text
        return requests.get(search+value, {"User-Agent": ua.random}).text

    def jsonify(self, html):
        '''
        Google returns a list of results containing title and track metadata
        :return:
        Only json string
        '''
        soup = BeautifulSoup(html, 'html.parser')
        # soup = BeautifulSoup(html, 'lxml')

        # print("Dumping soup html...")
        # with open("soup.html", "w") as file:
        #     file.write(str(soup))

        #########################################
        ##### Parse Google search results ######
        result_div = soup.find_all('div', attrs = {'class': 'Gx5Zad'})

        noResults = soup(text=re.compile('did not match any documents'))
        if len(noResults) > 0:
            print("NO RESULTS...")
            sys.exit()

        links = [ tit.find('a', href = True)['href'] for tit in result_div ]
        headers = [ header.find('div', attrs={'class':'vvjwJb'})  for header in result_div  ]
        # headers = [ header.get_text() for header in (r.find('div', attrs={'class':'vvjwJb'}) for r in result_div) if header is not None  ]
        descriptions = [ desc.find('div', attrs={'class':'s3v9rd'}) for desc in result_div  ]
        # descriptions = [ desc.get_text() for desc in (r.find('div', attrs={'class':'s3v9rd'}) for r in result_div) if desc is not None  ]

        track_dur = re.compile(r'Length (\d+:\d+)[;\s]', re.IGNORECASE)

        titles = []
        urls = []
        details = []
        times = []
        for i, t in enumerate(headers):
            # if the title node is missing then its not a result tag
            if t is not None:
                details.append(descriptions[i])

                text = t.get_text()
                titles.append(text)
                
                url = re.search('\/url\?q\=(.*)\&sa', links[i]).group(1)
                urls.append(url)
                
                duration = track_dur.findall(descriptions[i].text)
                times.append(duration)

        #########################################
        
        # titles = [ tit.text for tit in soup.findAll('h3', attrs={'class':'r'}) ]
        ## urls = [ tit.text for tit in soup.findAll('cite') ]
        # urls = [ tit.a['href'].split('&', 1)[0][7:] for tit in soup.findAll('h3', attrs={'class':'r'}) ]

        # track_dur = re.compile(r'Length (\d+:\d+)[;\s]', re.IGNORECASE)
        # times = [ track_dur.findall(dur.text)[0] if len(track_dur.findall(dur.text)) > 0  else 'n/a' for dur in soup.findAll('span', attrs={'class':'st'})]

        #########################################
        ##### Select the appropriate result #####
        index = 1
        for t, d, u in zip(titles, times, urls):
            print(str(index) + ". " + t + " : " + str(d) + " -> " + u)
            index = index + 1

        validInput = False
        while(not validInput):
            str_idx = input("Which search result?...")
            if str_idx:
                idx = int(str_idx)
                if idx == 0:
                    break
                elif idx <= len(urls):
                    INDEX = idx - 1
                    url = urls[INDEX]
                    validInput = True
                else:
                    print("Invalid index...")
            else:
                break

        if not validInput:
            print("Exiting...")
            sys.exit()
        #########################################

        #########################################
        #### Query beatport for specific url ####
        # track_query = requests.get(url, {"User-Agent": ua.random}).text
        headers = {"User-Agent": ua.random}
        track_query = requests.get(url, headers=headers).text
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

metadata_log_file = f= open("metadata_log_file.txt", "a+")

if len(sys.argv[1]) == 1:
    if sys.argv[1] == 'g':
        search_google = True
        search_str_arg_idx = 2
    else:
        print("Unknown parameter...")
        sys.exit()

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
    # print(track_list)
    data = beat_api.choose_track(track_list)

###### Write out json data to file ######
# with open('data.json', 'w') as outfile:
#     json.dump(raw, outfile)
#########################################

if search_google:
    data = data['props']['pageProps']['track']
# print(data)

############ Print metadata #############
artist_l = beat_api.get_artists(data)

print()
# print("Title: \t\t" + title)
# print("Artist(s): \t" + artist_l)
# print("Duration: \t" + data['duration']['minutes'])
# print("BPM: \t\t" + str(data['bpm']))
# print("Key: \t\t" + str(data['key']))
# print("Label: \t\t" + data['label']['name'] )
# print("Format: \t" + data['audio_format'] )
# print("Released: \t" + data['date']['released'])
# print("Genre: \t\t" + data['genres'][0]['name'])
# print("ID: \t\t" + str(data['id']))

tag = 'name'
if 'track_name' in data:
    tag = 'track_name'

title = data[tag]
if ('mix_name' in data):
    title = title + " (" + data['mix_name'] + ")"

bpm = str(data['bpm'])

if search_google:
    length = data['length']    
    date = data['publish_date']
    key = data['key']['name']
    label = data['release']['label']['name']
    genre = data['genre']['name']
    track_id = str(data['id'])
    image = data['release']['image']['uri']

if not search_google:
    length = ':'.join(str((datetime.timedelta(seconds=data['length']//1000))).split(':')[1:3]).lstrip('0')
    date = data['publish_date'][:10]
    key = data['key_name']
    label = data['label']['label_name']
    genre = data['genre'][0]['genre_name']
    track_id = str(data['track_id'])
    image = data['release']['release_image_uri']

print("Title : Artist(s): Duration: BPM: Key: Label: Format: Released: Genre: ID")
print(title)
print(artist_l)
print(length)
print(bpm)
print(key)
print(label)
print('mp3')
print(date)
print(genre)
print(track_id)

metadata_log_file.write("{}\n".format(title))
metadata_log_file.write("{}\n".format(artist_l))
metadata_log_file.write("{}\n".format(length))
metadata_log_file.write("{}\n".format(bpm))
metadata_log_file.write("{}\n".format(key))
metadata_log_file.write("{}\n".format(label))
metadata_log_file.write("{}\n".format('mp3' ))
metadata_log_file.write("{}\n".format(date))
metadata_log_file.write("{}\n".format(genre))
metadata_log_file.write("{}\n".format(track_id))
metadata_log_file.write("#-----#\n")

# Download track art
img_dir = "imgs/" 
title = title.replace("/", "-")
img_path = img_dir + artist_l + " - " + title + ".jpg"
print("Saving albumart...")

# IMG_W, IMG_H = 500, 500
# available_params = {'w': IMG_W, 'h': IMG_H }

"https://geo-media.beatport.com/image_size/1400x1400/2520e368-173e-43c4-874a-d42346ffe173.jpg"

dimensions_regex = r"/(\d+x\d+)/"
matches = re.findall(dimensions_regex, image)
if len(matches) > 0:
    image_dimensions = matches[0]

# Replacing the image dimensions in the URI using regex
new_dimensions = "500x500"  # The new dimensions you want to use
new_uri = re.sub(dimensions_regex, f"/{new_dimensions}/", image)

# print(data['images']['dynamic']['url'])
# print(data['images']['dynamic']['url'].format(**available_params))

response = requests.get(new_uri)
# response = requests.get(data['images']['dynamic']['url'].format(**available_params))
# response = requests.get(data['images']['large']['url'])

if response.ok:
    with open(img_path, 'wb') as f:
        f.write(response.content)
print("Finished!")
#########################################

########## Open artwork  ############
# os.system('open "'+ img_path + '"')
#########################################