import json
import os
import random
import ffmpegio
import requests
from pprint import pprint
from datetime import timedelta

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class Bot:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
        self.service = Service('/Users/rhillx/Downloads/chromedriver')
        self.options = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome(service=self.service, options=self.options)

        
    def durationToSeconds(self, duration):
        m,s = duration.split(':')
        return int(timedelta(minutes=int(m), seconds=(int(s))).total_seconds())
    
    def removeClipFromJson(self, topic, _id):
        #OPEN JSON FILE
        with open(f'Topics/{topic}.json', 'r') as f:
            clips = json.loads(f.read())
        #LOOP THRU FILE AND FIND OBJ ID, REMOVE FROM LIST   
        for i in range(len(clips)-1):
            if clips[i]['id'] == _id:
                clips.pop(i)
        #WRITE NEW CONTENTS BACK TO JSON FILE
        with open(f'Topics/{topic}.json', 'w') as f:
            f.write(json.dumps(clips,indent=2))

    # This function will return a single story object
    def fetchClip(self):
        # GET A TOPIC FROM LIST OF TOPICS
        with open('items.txt', 'r') as f:
            topicss = f.readlines()
            topic = random.choice(topicss).split("\n")[0]
            print(topic)
        # CHECK IF TOPIC JSON FILE EXISTS
        stories = []
        try:
            with open('Topics/{}.json'.format(topic), 'r') as f:
                stories = json.loads(f.read())
            # self.driver.quit()
            return stories[0]            
        except:
            self.driver.get("https://search.audioburst.com/playlist/{}".format(topic))
            # FIND ALL THE SUB CATEGORIES
            clips = self.driver.find_elements(By.CLASS_NAME, 'burst-card')
            # # LOOP THROUGH SUBs and CLICK TO GOTO SUB PAGE
            for clip in clips:
                dur = clip.find_element(By.TAG_NAME, 'span').text.split(' ')[0]
                if self.durationToSeconds(dur) <= 300:
                    story = {}
                    story['id'] = clip.get_attribute('href').split('/')[4]
                    story['topic'] = topic
                    story['title'] = clip.find_element(By.TAG_NAME, 'h4').text
                    story['sub_title'] = clip.find_element(By.TAG_NAME, 'h3').text
                    story['duration'] = clip.find_element(By.TAG_NAME, 'span').text.split(' ')[0]
                    story['imgURL'] = clip.find_element(By.TAG_NAME, 'img').get_attribute('src')
                    stories.append(story)
                else:
                    continue
            with open('Topics/{}.json'.format(topic), 'w') as f:
                f.write(json.dumps(stories, indent=2))
            self.driver.quit()
            return stories[0]


        
    # FUNCTION convertAudio(string clipId) 
    # PLACE FFMPEG EXECUTABLE IN EXEC FOLDER
    def transcodeAudio(self, clipId):
        file = '{}.mp3'.format(clipId)
        stream_url ='https://storageaudiobursts.azureedge.net/stream/{}/outputlist.m3u8'.format(clipId)
        ffmpegio.set_path(ffmpeg_path='./exec/ffmpeg', ffprobe_path='./exec/ffprobe')
        ffmpegio.transcode(stream_url, file)
        return file

    # This function takes the image url and returns the image file for use
    def transcodeImage(self, url):
        resp = requests.get(url, stream=True)
        with open('clip.png', 'wb') as f:
            f.write(resp.content)
        
    # This function will delete the img file created for firebase
    def discardFiles(self, files):
        try:
            os.remove(files[0])
            os.remove(files[1])
        except:
            print('File does not exists.')
            return
        
    def quitDriver(self):
        self.driver.quit()
