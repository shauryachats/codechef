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
def downloadPage(username, timeOutTime=0, isProblem = False):
    file_path = ".codechef/"
    url_path = "http://www.codechef.com/" 

    if (username == 'contests'):
        file_path += "contests"
        url_path += "contests"
    #Uppercase strings are considered to be problem codes as well as contest codes.
    elif (username.isupper()):
        #if the code is a problem code.
        if isProblem:
            file_path += "problem/" + username
            url_path += "problems/" + username
        #else the code is a contest code.
        else:
            file_path += "contest/" + username
            url_path += username
    #The username is a user's.
    else:
        file_path += "user/" + username
        url_path += "users/" + username

    # Create the paths, if not already present.
    pathsToCreate = ['.codechef', '.codechef/contest', '.codechef/problem', '.codechef/user']
    for path in pathsToCreate:
        if (not os.path.exists(path)):
            os.makedirs(path)


    # Check if the webpage is there.
    # If not, download.
    # If yes, check for the timeOutTime and if time_diff > timeOutTime, redownload.
    # Else, do nothing.

    download_page = False

    if (not os.path.exists(file_path)):
        download_page = True
        print "Page does not exist. Downloading..."

    else:
        downloaded_time = datetime.datetime.fromtimestamp(
            os.path.getmtime(file_path))
        time_difference = datetime.datetime.now() - downloaded_time

        if (int(time_difference.seconds) > timeOutTime):
            os.remove(file_path)
            download_page = True
            print "Downloaded page is expired. Redownloading..."

    if (download_page == True):

        # If username exists, only 1 redirection will follow.
        # Else, 2 redirections. Hence, we invalidate >= 2 requests.
        request = requests.Session()
        request.max_redirects = 1
        
        if (username == 'contests'):
            request.max_redirects = 2

        try:
            web_page = request.get(url_path).text
        except requests.TooManyRedirects:
            raise Exception('Username not found.')
        # When the network is down i.e. WiFi is not connected or bleh.
        except IOError:
            raise Exception('Cannot connect to codechef.com')

        # If correct user's page is downloaded, save it to the page.
        page = open(file_path, "wb")
        page.write(web_page.encode('utf-8').strip())
        page.close()

    return BeautifulSoup(open(file_path).read())


"""
    Writes the data in JSON format in two modes:
        * Readable -> The file is written with an extension of '.json'
        * Compressed -> The file is written with an extension of '.cjson'
"""
def putDataInFile (username, attributes, compressed=False):
    if (not compressed):
        with open(username + '.json', 'w') as alp:
            alp.write(json.dumps(attributes, indent=4))
    else:
        #Compressed JSON files to be denoted by cjson
        with open(username + '.cjson', 'wb') as alp:
        # Use zlib library to compress JSON.
            alp.write(zlib.compress(json.dumps(attributes, indent=0)))

"""
    Returns the data from the file written by putDataInFile().
"""
def getDataFromFile (filename):

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
def convertToKey(token):
    temp = token.lower().replace(' ', '_')
    return ''.join(ch for ch in temp if ch.isalnum() or ch == '_')