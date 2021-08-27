import re, sys, os
from zipfile import ZipFile
import json, yaml
from datetime import datetime
import pandas as pd
import csv

class data:

    def __init__(self):

        #create empty dataframes for messages and media
        self.messages = pd.DataFrame({'username':[],
                                      'createdDate': [],
                                      'typeOfMessage': [],
                                      'texts': []
                                    })

        self.media = pd.DataFrame({'username':[],
                                      'createdDate': [],
                                      'typeOfMedia': [],
                                      'texts': []
                                    })
    #function to unzip the files
    def unzipFiles(pathToUnzipped):

        listOfFolders = os.listdir(pathToUnzipped)

        for f in listOfFolders:
            file_name =  pathToUnzipped + f

            # opening the zip file in READ mode
            try:
                with ZipFile(file_name, 'r') as zip:

                    # printing all the contents of the zip file
                    zip.printdir()

                    # extracting all the files
                    print('Extracting all the files now...')
                    zip.extractall(pathToUnzipped)
                    print('Done!')
            except:
                print("Couldn't extract" + file_name)

                #if the zip file could's be extracted, continue to the next one
                pass

    # function to analyse the messages file
    def analyseMessagesFile(self, pathToFolder, username):

        usernamesList, createdDatesList, typeOfMessagesList, messagesDataList = [],[],[], []

        with open(pathToFolder, errors='ignore') as f:
            txt_data=f.read()

            #correct errors that have occured after the anonymisation script
            txt_data=re.sub(r'is_verified": __[a-z0-9]+','is_verified": true',txt_data)
            txt_data=re.sub(r'is_random": __[a-z0-9]+','is_random": true',txt_data)

            #load the json file
            messagesData = json.loads(txt_data,strict=False)

            for i in range(0,len(messagesData)):
                if 'conversation' in messagesData[i]:
                    s = len(messagesData[i]['conversation'])
                    for j in range(0,s):
                        jsonConversation = messagesData[i]['conversation'][j]

                        text=""
                        typeOfMessage=''

                        # we focus only on outgoing messages
                        if jsonConversation['sender']==username:

                            if 'text' in jsonConversation:
                                text = (str(jsonConversation['text']))
                            if 'story_share' in jsonConversation:
                                typeOfMessage = 'outStoryShareMessage'
                            elif 'media_share_url' in jsonConversation or 'media' in jsonConversation:
                                typeOfMessage = 'outMediaShareMessage'
                            elif 'heart' in jsonConversation:
                                typeOfMessage = 'heartMessage'
                            else:
                                typeOfMessage = 'outTextMessage'

                            date = jsonConversation['created_at']
                            date = str(date).replace("+00:00","")

                            createdDatesList.append(date)
                            messagesDataList.append(text.replace(",", " "))
                            typeOfMessagesList.append(typeOfMessage)
                            usernamesList.append(username)




        messages_new = pd.DataFrame({'username':usernamesList,
                                      'createdDate': createdDatesList,
                                      'typeOfMessage': typeOfMessagesList,
                                      'texts': messagesDataList
                                    })

        self.messages = pd.concat([self.messages, messages_new], ignore_index=True)



    # function to analyse the media file
    def analyseMediaFile(self, pathToFolder, username):

        usernamesMediaList, createdDatesMediaList, typeOfMediaList, textsMediaList = [],[],[], []
        caption = ""
        prev_created_at=datetime(2020, 5, 4, 18, 24, 0)

        with open(pathToFolder) as f:
            txt_data=f.read()
            txt_data=re.sub(r'is_active_profile": __[a-z0-9]+','is_active_profile": true',txt_data)

            data = json.loads(txt_data,encoding='utf-8')
            listOfMedia = ['photos', 'videos', 'stories']

            for typeOfMedia in listOfMedia:
                if typeOfMedia in data:
                    for i in range(0,len(data[typeOfMedia])):
                        date = data[typeOfMedia][i]['taken_at']
                        date = str(date).replace("+00:00","")
                        date = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')

                        if ((((prev_created_at - date).total_seconds())  < 60) and ((prev_created_at - date).total_seconds())  > -60):
                            prev_created_at = date

                        else:
                            prev_created_at = date

                            #created_at = datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                            if 'caption' in data[typeOfMedia][i]:
                                caption = data[typeOfMedia][i]['caption']

                                textsMediaList.append(caption.replace(",", " "))
                                createdDatesMediaList.append(date)
                                typeOfMediaList.append(typeOfMedia)
                                usernamesMediaList.append(username)


        media_new = pd.DataFrame({'username':usernamesMediaList,
                                      'createdDate': createdDatesMediaList,
                                      'typeOfMedia': typeOfMediaList,
                                      'texts': textsMediaList
                                    })

        self.media = pd.concat([self.media, media_new], ignore_index=True)


    def load_data(self, path):

        # list the folders that contain the data download packages of the users

        # list all the folders at the path
        listOfFolders = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name)) ]

        for f in listOfFolders:
            # initial value to the username is known to cover the cases that a username will not be extracted
            username = 'unknown'
            listOfUsernames = []
            pathOfUserFolder=path + f

            jsonFiles = os.listdir(pathOfUserFolder)

            if 'profile.json' in jsonFiles:
                with open(pathOfUserFolder+'/profile.json') as f:
                    profileData = yaml.load(f.read())

                    if 'username' in profileData:
                        username=profileData['username']
                    else:
                        username=profileData['name']

            else:
                print('folder name will be used because there was no profile json file for: ', pathOfUserFolder)
                username = (pathOfUserFolder.split("/")[-1]).split("_")[0]
            listOfUsernames.append(username)

            if 'messages.json' in jsonFiles:
                self.analyseMessagesFile(pathOfUserFolder+'/messages.json', username)
                print('processing json file: messages.json of user ', username)
            else:
                print('there was no messages json file at: ', pathOfUserFolder)

            # check and process additional messages files
            for i in range(1,10):
                filename = 'messages_' + str(i) + '.json'
                if filename in jsonFiles:
                    self.analyseMessagesFile(pathOfUserFolder+'/' + filename, username)
                    print('processing json file: ', filename, 'of user ', username)

            if 'media.json' in jsonFiles:
                self.analyseMediaFile(pathOfUserFolder+'/media.json', username)
                print('processing json file: media.json of user ', username)
            else:
                print('there was no media json file at: ', pathOfUserFolder, username)

            # check and process additional media files
            for i in range(1,10):
                filename = 'media_' + str(i) + '.json'
                if filename in jsonFiles:
                    self.analyseMediaFile(pathOfUserFolder+'/' + filename, username)
                    print('processing json file: ', filename, 'of user ', username)

        print('Finished processing folder:' + username)

