import os
import requests
import datetime
import json
import zlib
from collections import OrderedDict
from BeautifulSoup import BeautifulSoup

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

    FILE_PATH = '.codechef/' + fileName + '.cjson'
    #Checking for the existance of the file.
    if not os.path.exists(FILE_PATH):
        print '[!] ' + fileName + ' not present.'
        return None

    #Checking time difference of the file.
    downloadedTime = datetime.datetime.fromtimestamp(os.path.getmtime(FILE_PATH))
    timeDifference = datetime.datetime.now() - downloadedTime
    if (int(timeDifference.seconds) > expiryTime):
        return None

    #If the file is in the expiryTime limit, return the python object.
    with open(FILE_PATH, 'rb') as alp:
        return OrderedDict(json.loads(zlib.decompress(alp.read())))

"""
    writeToFile() writes the compressed JSON in the mentioned file.
"""
def writeToFile(fileName, attributes):

    #   Make all the required directories.
    makeAllDirs()

    FILE_PATH = '.codechef/' + fileName + '.cjson'

    with open(FILE_PATH, 'wb') as alp:
        alp.write(zlib.compress(json.dumps(attributes, indent=0)))

""" 
    downloadUserPage() returns the BeautifulSoup object of the username, if found.
    If not, it raises an Exception.
"""
def downloadUserPage(username):

    print '[*] Downloading user ' + username
    URL = "https://www.codechef.com/users/" + username
    web_page = None

    try:
        web_page = requests.get(URL)
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

    URL = "https://www.codechef.com/contests"
    web_page = None

    try:
        web_page = requests.get(URL)
    except IOError:
        raise IOError('Cannot connect to codechef.com')

    if (web_page.status_code != 200):
        raise Exception('Contest List page did not load.')

    return BeautifulSoup(web_page.text.encode('utf-8').strip())

def downloadContestPage(contestCode):

    URL = "https://www.codechef.com/" + contestCode

    web_page = None
    try:
        web_page = requests.get(URL)
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
    URL = "https://www.codechef.com/recent/user"

    param = {'page':pageno , 'user_handle':username }
    web_page = None

    try:
        web_page = requests.get(URL, params=param)
    except IOError:
        raise IOError('Cannot connect to codechef.com')

    data = json.loads(web_page.text)

    if data['max_page'] == 0:
        raise Exception('No data found.')

    return BeautifulSoup(data['content'].strip())


"""
    Converts token into camelCase.
"""
def camelCase(token):

    components = token.lower().split(' ')
    return components[0] + ''.join(x.title() for x in components[1:])
