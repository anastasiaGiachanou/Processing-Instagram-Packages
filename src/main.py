from data import data
from textualInformation import textualInformation
import pandas as pd
import os
from sentiment import sentiment
import json
import csv, re
from datetime import datetime

#boolean that shows if you want to generate or load features
generateFeatures = True
timeThreshold = True

if timeThreshold:
    dateAfter = datetime(2019, 11, 21)
    dateBefore = datetime(2020, 7, 1)

outputFolder = "outputFiles/"
path = 'DDP_dump/'
path = '/Users/anastasia/Documents/research-awesome-uva-uu/DDPs_text/'

if __name__ == '__main__':

    if generateFeatures:
        """Unzip files in case they are not"""
        # pathToZipped = '/Users/anastasia/Documents/research-awesome-uva-uu/DDPs_text/'
        # data.unzipFiles(pathToZipped)

        """Loading data"""


        loaded_data = data()
        loaded_data.load_data(path)

        textMeassages = loaded_data.messages["texts"]
        textMedia = loaded_data.media["texts"]

        # delete the text for privacy reasons
        # del loaded_data.messages['texts']
        # del loaded_data.media['texts']

        """Exporting data without the text column"""

        loaded_data.messages.to_csv(outputFolder + 'messages.csv')
        loaded_data.media.to_csv(outputFolder + 'media.csv')
        rslt_df = loaded_data.media[loaded_data.media['typeOfMedia'] == 'photos']
        rslt_df = rslt_df[rslt_df['texts'] != ""]

        rslt_df["createdDate"]=pd.to_datetime(rslt_df["createdDate"])
        rslt_df = rslt_df.loc[(rslt_df['createdDate'] < datetime.strptime('2019-11-21', '%Y-%m-%d'))]

        rslt_df.to_csv(outputFolder + 'mediaPhotos.csv')


        # export the text file in a seperate file if necessary
        textMeassages.to_csv(outputFolder + 'messagesOnlyText.csv')
        textMedia.to_csv(outputFolder + 'mediaOnlyText.csv')

        """Generate the textual statistics of the data"""

        print()
        print("Generate the textual statistics of the data")
        textProcessor = textualInformation()
        dfTextualMessages = textProcessor.one_vector_stylistic(textMeassages)
        dfTextualMedia = textProcessor.one_vector_stylistic(textMedia)

        dfTextualMessages.to_csv(outputFolder + 'messagesTextualFeatures.csv')
        dfTextualMedia.to_csv(outputFolder + 'mediaTextualFeatures.csv')

        # """Generate the sentimental features of the data"""
        # print()
        # print("Generate the sentimental features of the data")
        # # this code requires connection to VADER API and can take long because of the waiting time between the requests
        # sentimentProcessor = sentiment()
        # dfSentimentMessages = sentimentProcessor.one_vector_sentiment(textMeassages)
        # dfSentimentMedia = sentimentProcessor.one_vector_sentiment(textMedia)
        #
        # dfSentimentMessages.to_csv(outputFolder + 'messagesSentimentFeatures.csv')
        # dfSentimentMedia.to_csv(outputFolder + 'mediaSentimentFeatures.csv')

    else:
        """Loading features from the files"""
        loaded_data = data()

        if (os.path.isfile(outputFolder + 'messages.csv')):
            loaded_data.messages = pd.read_csv(outputFolder + 'messages.csv')
        if (os.path.isfile(outputFolder + 'media.csv')):
            loaded_data.media = pd.read_csv(outputFolder + 'media.csv')

        if (os.path.isfile(outputFolder + 'messagesTextualFeatures.csv')):
            dfTextualMessages = pd.read_csv(outputFolder + 'messagesTextualFeatures.csv')
        if (os.path.isfile(outputFolder + 'mediaTextualFeatures.csv')):
            dfTextualMedia = pd.read_csv(outputFolder + 'mediaTextualFeatures.csv')

        if (os.path.isfile(outputFolder + 'messagesSentimentFeatures.csv')):
            dfSentimentMessages = pd.read_csv(outputFolder + 'messagesSentimentFeatures.csv')
        if (os.path.isfile(outputFolder + 'mediaSentimentFeatures.csv')):
            dfSentimentMedia = pd.read_csv(outputFolder + 'mediaSentimentFeatures.csv')

    """Descriptive statistics of the data"""
    print(loaded_data.messages.info())
    print(loaded_data.media.info())

    print(dfTextualMessages.info())
    print(dfTextualMedia.info())

    # print(dfSentimentMessages.info())
    # print(dfSentimentMedia.info())

    loaded_data.messages['createdDate'] = pd.to_datetime(loaded_data.messages['createdDate'])
    loaded_data.media['createdDate'] = pd.to_datetime(loaded_data.media['createdDate'])

    messaged_temporalThresold = loaded_data.messages[(loaded_data.messages['createdDate'] >= dateAfter) & (loaded_data.messages['createdDate'] <= dateBefore)]
    mediaThresold = loaded_data.media[(loaded_data.media['createdDate'] >= dateAfter) & (loaded_data.media['createdDate'] <= dateBefore)]

    print(messaged_temporalThresold.head())

    loaded_data.messages.groupby(['username', 'typeOfMessage']).size().reset_index(name='counts').to_csv(outputFolder + 'countsPerUserPerTypeMessages.csv')
    loaded_data.media.groupby(['username', 'typeOfMessage']).size().reset_index(name='counts').to_csv(outputFolder + 'countsPerUserPerTypeMedia.csv')


    #if you want the statistics of a certain period of time
    if timeThreshold:

        messaged_temporalThresold.groupby(['username', 'typeOfMessage']).size().reset_index(name='counts').to_csv(outputFolder + 'countsPerUserPerTypeMessagesThreshold.csv')
        mediaThresold.groupby(['username', 'typeOfMessage']).size().reset_index(name='counts').to_csv(outputFolder + 'countsPerUserPerTypeMediaThreshold.csv')

