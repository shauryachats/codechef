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
                 timeOutTime=0,
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
    # If yes, check for the timeOutTime and if time_diff > timeOutTime, redownload.
    # Else, do nothing.

    shouldWeDownloadPage = False

    if (not os.path.exists(filePath)):
        shouldWeDownloadPage = True
        print "Page does not exist. Downloading..."

    else:
        downloadedTime = datetime.datetime.fromtimestamp(os.path.getmtime(filePath))
        timeDifference = datetime.datetime.now() - downloadedTime

        if (int(timeDifference.seconds) > timeOutTime):
            os.remove(filePath)
            shouldWeDownloadPage = True
            print "Downloaded page is expired. Redownloading..."

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


"""
    Writes the data in JSON format in two modes:
        * Readable -> The file is written with an extension of '.json'
        * Compressed -> The file is written with an extension of '.cjson'
"""
def dumpData (attributes, filename, compressed = False):
    if (not compressed):
        with open(filename + '.json', 'w') as alp:
            alp.write(json.dumps(attributes, indent=4))
    else:
        #Compressed JSON files to be denoted by cjson
        with open(filename + '.cjson', 'wb') as alp:
        # Use zlib library to compress JSON.
            alp.write(zlib.compress(json.dumps(attributes, indent=0)))

"""
    Returns the data from the file written by putDataInFile().
"""
def getData (filename):

    attributes = OrderedDict()
    
    #If the JSON file is compressed,
    if (filename.endswith('.cjson')): 
        with open(filename, 'rb') as alp:
            attributes = json.loads(zlib.decompress(alp.read()))
    elif (filename.endswith('.json')):
        with open(filename, 'r') as alp:
            attributes = json.loads(alp.read())
    else:
        raise IOError('Invalid file type.')

    return attributes


"""
    Converts text into 'key' format: i.e. "About me" becomes 'about_me'

    It replaces spaces with underscore and strips all the non alphanumeric characters.
"""
def camelCase(token):
    #temp = token.lower().replace(' ', '_')
    components = token.lower().split(' ')
    return components[0] + ''.join(x.title() for x in components[1:])
    #return ''.join(ch for ch in temp if ch.isalnum() or ch == '_')