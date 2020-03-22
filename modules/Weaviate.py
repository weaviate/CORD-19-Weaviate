""" This module contains the REST interface to Weaviate """

from os.path import expanduser
import re
import json
import time
import random
import datetime
import requests
import yaml


def logMessage(message):
    """ This function outputs the string to the log output """
    print(datetime.datetime.now().isoformat() + " | " + str(message))


def removeSpecialCharactersFromText(text):
    """ This function cleans text from unwanted characters """
    cleartext = ""
    if text != "":
        cleanr = re.compile('<.*?>')
        cleartext = re.sub(cleanr, '', text)
        cleartext = cleartext.replace('\n', ' ')
        cleartext = cleartext.replace('\r', ' ')
        cleartext = cleartext.replace('\\', '')
    return cleartext


def getWeaviateUrlFromConfigFile():
    """ See if there is a Weaviate running by checking the config file """
    url = ""
    # Try to collect the Weaviate URL from the weaviate-cli config
    try:
        weaviateYaml = yaml.load(open(expanduser("~") + "/.weaviate.conf"), Loader=yaml.FullLoader)
        url = weaviateYaml['url']
    # If the URL can't be collected from the weaviate-cli config file, request it via de CLI
    except yaml.YAMLError:
        print("please specify the weaviate including port [default = ", url, "]:", end=' ')
        url = input()
        if url == "":
            url = "http://localhost:8080"
    return url


class Weaviate:
    """ This class contains the REST interface to Weaviate """

    def __runREST(self, restUrl, weaviateObj, tryTimes, restType):
        if restType == "GET":
            try:
                result = requests.get(url=restUrl, headers=self.header)
            except requests.ConnectionError:
                # sleep for 2 sec, wait to come back and run again
                logMessage("WARNING - GET - Some kind of timeout, sleep and wait, try again or fail")
                logMessage("WARNING - REQUEST WAS: " + restUrl + " " + json.dumps(weaviateObj))
                time.sleep(2)
                result = requests.get(url=restUrl, headers=self.header)
        elif restType == "POST":
            try:
                result = requests.post(url=restUrl+"?rnd="+str(random.randint(1, 9999999)), data=json.dumps(weaviateObj), headers=self.header)
            except requests.ConnectionError:
                # sleep for 2 sec, wait to come back and run again
                logMessage("WARNING - POST - Some kind of timeout, sleep and wait, try again or fail")
                logMessage("WARNING _ REQUEST WAS: " + restUrl + " " + json.dumps(weaviateObj))
                time.sleep(2)
                result = requests.post(url=restUrl, data=json.dumps(weaviateObj), headers=self.header)
        elif restType == "PATCH":
            try:
                result = requests.patch(url=restUrl, data=json.dumps(weaviateObj), headers=self.header)
            except requests.ConnectionError:
                # sleep for 30 sec, wait to come back and run again
                logMessage("WARNING - PATCH - Some kind of timeout, sleep and wait, try again or fail")
                logMessage("WARNING - REQUEST WAS: " + restUrl + " " + json.dumps(weaviateObj))
                time.sleep(2)
                result = requests.patch(url=restUrl, data=json.dumps(weaviateObj), headers=self.header)
        else:
            logMessage("ERROR: wrong restType is set")
            exit(1)

        if result.status_code != 200:
            logMessage("WARNING: STATUS CODE WAS NOT 200 but " + str(result.status_code) + " | " + str(result.content))

            # weaviate needs some time
            time.sleep(1)

            if tryTimes < 10:
                tryTimes += 1
                return self.__runREST(restUrl, weaviateObj, tryTimes, restType)
            logMessage("ERROR: Could not add this thing or action")
            logMessage("ERROR: STATUS CODE WAS NOT 200 but " + str(result.status_code))
            logMessage("ERROR: " + result.text)
            logMessage("ERROR: request URL" + restUrl)
            logMessage("ERROR: request body: " + json.dumps(weaviateObj))
            return None
        return result


    def checkIfWeaviateIsRunning(self):
        """ This function checks if a weaviate is running at the argument ulr """
        try:
            requests.get(url=self.weaviateUrl + "/v1/meta")
        except requests.exceptions.RequestException:
            print("WARNING: no Weaviate detected at ", self.weaviateUrl, " Trying locahost ...")
            url = "http://localhost:8080"
            try:
                requests.get(url=url)
            except requests.exceptions.RequestException:
                self.weaviateUrl = ""
            else:
                self.weaviateUrl = "http://localhost:8080"


    def runREST(self, restUrl, weaviateObj, tryTimes, restType):
        """ This function makes the REST call  """
        return self.__runREST(self.weaviateUrl + restUrl, weaviateObj, tryTimes, restType)


    def __init__(self, url):
        self.header = {'Content-type': 'application/json'}
        self.weaviateUrl = url
        self.checkIfWeaviateIsRunning()