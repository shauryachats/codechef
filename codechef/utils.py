import os
import requests
import datetime
import json
import zlib
from collections import OrderedDict
from BeautifulSoup import BeautifulSoup


"""
    Downloads the respective HTML file, checks if the page hasn't timed out,
    and returns the BeautifulSoup object of the webpage.
"""
def downloadPage(username, 
                 expiryTime=0,
                 isProblem = False,
                 isContest = False,
                 isUser = False,
                 baseDirectory = None ):

    #If custom base directory is set. 
    if baseDirectory:
        os.chdir( baseDirectory )

    filePath = ".codechef/"
    urlPath = "http://www.codechef.com/" 

    #Only the contest list uses the "username" contests.
    if (username == 'contests'):
        filePath += "contests"
        urlPath += "contests"
    elif (isProblem):
        filePath += "problem/" + username
        urlPath += "problems/" + username
        #else the code is a contest code.
    elif (isContest):
        filePath += "contest/" + username
        urlPath += username
    elif (isUser):
        filePath += "user/" + username
        urlPath += "users/" + username

    # Create the paths, if not already present.
    pathsToCreate = ['.codechef', '.codechef/contest', '.codechef/problem', '.codechef/user']
    for path in pathsToCreate:
        if (not os.path.exists(path)):
            os.makedirs(path)


    # Check if the webpage is there.
    # If not, download.
    # If yes, check for the expiryTime and if time_diff > expiryTime, redownload.
    # Else, do nothing.

    shouldWeDownloadPage = False

    if (not os.path.exists(filePath)):
        shouldWeDownloadPage = True
        print "[*] Page does not exist. Downloading..."

    else:
        downloadedTime = datetime.datetime.fromtimestamp(os.path.getmtime(filePath))
        timeDifference = datetime.datetime.now() - downloadedTime

        if (int(timeDifference.seconds) > expiryTime):
            os.remove(filePath)
            shouldWeDownloadPage = True
            print "[*] Downloaded page is expired. Redownloading..."

    if (shouldWeDownloadPage == True):
        
        web_page = None

        #
        #   For usernames,
        #   correct usernames take only one redirection.
        #   wrong usernames take two redirections. 
        #   Hence, we invalidate all >= 2 redirections.
        #
        if (isUser):
            try:
                web_page = requests.get(urlPath)
            except IOError:
                raise IOError('Cannot connect to codechef.com')

            if len(web_page.history) > 1:
                raise Exception('Username not found.')

        #
        #   For contest list,
        #   it takes only one redirection.
        #   so we raise an Exception if the status code is not 200 OK.
        #
        elif (username == 'contests'):
            try:
                web_page = requests.get(urlPath)
            except IOError:
                raise IOError('Cannot connect to codechef.com')

            if (web_page.status_code != 200):
                raise Exception('Status Error Code : ' + web_page.status_code)
        #
        #   For problems,
        #   correct problems take only one redirection.
        #   wrong problems take two redirections.
        #   Hence we invalidate >= 2 redirections.
        #
        elif (isProblem):
            try:
                web_page = requests.get(urlPath)
            except IOError:
                raise IOError('Cannot connect to codechef.com')

            if len(web_page.history) > 1:
                raise Exception('Problem not found.')

        #
        #   For contests,
        #   both wrong and correct contests take only one redirection.
        #   Hence, if error code 404 is returned, it is a wrong contest.
        #
        elif (isContest):
            try:
                web_page = requests.get(urlPath)
            except IOError:
                raise IOError('Cannot connect to codechef.com')

            if (web_page.status_code == 404):
                raise Exception('Contest not found.')

        # If correct user's page is downloaded, save it to the page.
        page = open(filePath, "wb")
        page.write(web_page.text.encode('utf-8').strip())
        page.close()

    return BeautifulSoup(open(filePath).read())

#
#
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

def downloadProblemPage(problemCode):

    URL = "https://www.codechef.com/problems/" + problemCode

    web_page = None
    try:
        web_page = requests.get(URL)
    except IOError:
        raise IOError('Cannot connect to codechef.com')

    for response in web_page.history:
        if response.status_code == 302:
            raise Exception('Problem not found.')

    return BeautifulSoup(web_page.text.encode('utf-8').strip())


"""
    Converts token into camelCase.
"""
def camelCase(token):

    components = token.lower().split(' ')
    return components[0] + ''.join(x.title() for x in components[1:])
