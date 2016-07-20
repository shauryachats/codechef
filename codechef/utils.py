import os
import requests
import datetime
import json
import zlib
from collections import OrderedDict
from BeautifulSoup import BeautifulSoup
import logging

import globals

#
#   Creates the directories to initialise.
#
def makeAllDirs():

    dirsToCreate = {'.codechef/', '.codechef/users/', '.codechef/problems/', '.codechef/contest/'}

    for dir in dirsToCreate:
        if (not os.path.exists(dir)):
            os.makedirs(dir)


"""
    checkInFile() checks the pointed file for JSON compressed by zlib.

    If it founds the correct file which is not yet expired, it returns the JSON in a python object.
    Otherwise, it returns None.
"""

def checkInFile(fileName, expiryTime):

    logging.debug("In checkInFile("+fileName+')')
    FILE_PATH = '.codechef/' + fileName + '.cjson'
    #Checking for the existance of the file.
    if not os.path.exists(FILE_PATH):
        logging.info(fileName + "not found!")
        print '[!] ' + fileName + ' not present.'
        return None

    #Checking time difference of the file.
    downloadedTime = datetime.datetime.fromtimestamp(os.path.getmtime(FILE_PATH))
    timeDifference = datetime.datetime.now() - downloadedTime
    if (int(timeDifference.seconds) > expiryTime):
        logging.info("File expired.")
        return None

    logging.info("Reading " + fileName)
    #If the file is in the expiryTime limit, return the python object.
    with open(FILE_PATH, 'rb') as alp:
        return OrderedDict(json.loads(zlib.decompress(alp.read())))

"""
    writeToFile() writes the compressed JSON in the mentioned file.
"""
def writeToFile(fileName, attributes):

    #   Make all the required directories.
    logging.info("Writing to " + fileName)   
    makeAllDirs()

    FILE_PATH = '.codechef/' + fileName + '.cjson'

    with open(FILE_PATH, 'wb') as alp:
        alp.write(zlib.compress(json.dumps(attributes, indent=0)))

""" 
    downloadUserPage() returns the BeautifulSoup object of the username, if found.
    If not, it raises an Exception.
"""
def downloadUserPage(username):

    logging.info("In downloadUserPage(%s)" % (username))
    URL = "https://www.codechef.com/users/" + username
    web_page = None

    try:
        web_page = requests.get(URL,headers={'User-Agent': 'Mozilla/5.0'})
    except IOError:
        raise IOError('Cannot connect to codechef.com')

    #
    #   Apparently, if the username is not present, a 302 response is returned.
    #
    for response in web_page.history:
        if response.status_code == 302:
            raise Exception('User not found.')

    return BeautifulSoup(web_page.text.encode('utf-8').strip())

"""
    downloadContestList() returns the BeautifulSoup object of the All Contest list page.
    If not, it raises an Exception.
"""

def downloadContestList():

    logging.info("In downloadContestList()")
    URL = "https://www.codechef.com/contests"
    web_page = None

    try:
        web_page = requests.get(URL,headers={'User-Agent': 'Mozilla/5.0'})
    except IOError:
        raise IOError('Cannot connect to codechef.com')

    if (web_page.status_code != 200):
        raise Exception('Contest List page did not load.')

    return BeautifulSoup(web_page.text.encode('utf-8').strip())

def downloadContestPage(contestCode):

    URL = "https://www.codechef.com/" + contestCode

    web_page = None
    try:
        web_page = requests.get(URL,headers={'User-Agent': 'Mozilla/5.0'})
    except IOError:
        raise IOError('Cannot connect to codechef.com')

    if web_page.status_code != 200:
        raise Exception('Contest not found.')

    return BeautifulSoup(web_page.text.encode('utf-8').strip())

#
#   Downloads the recent submittions page of the user.
#
def downloadRecentPage(username, pageno):

    print '[*] Downloading recent page ' + str(pageno) + ' of ' + str(username)
    logging.info("Downloading recent page %d of %s", pageno, username )
    URL = "https://www.codechef.com/recent/user"

    param = {'page':pageno , 'user_handle':username }
    web_page = None

    try:
        web_page = requests.get(URL,headers={'User-Agent': 'Mozilla/5.0'}, params=param)
    except IOError:
        raise IOError('Cannot connect to codechef.com')

    data = json.loads(web_page.text)

    if data['max_page'] == 0:
        raise Exception('No data found.')

    return BeautifulSoup(data['content'].strip())


#
#   Converts To ken into to_ken
#
def convertToKey(token):
    temp = token.lower().replace(' ', '_')
    return ''.join(ch for ch in temp if ch.isalnum() or ch == '_')

#
#   Utility to remove a list of keys from a dictionary.
#
def removeKeys(attr, keyList):
    
    for key in keyList:
        try:
            attr.pop(key, None)
        except KeyError:
            pass

    return attr

#
#   Assigns the value of globals
#
def getGlobals(expiryTime, writeInFile):

    if expiryTime is None:
        expiryTime = globals.EXPIRY_TIME
    if writeInFile is None:
        writeInFile = globals.WRITE_IN_FILE

    return expiryTime, writeInFile