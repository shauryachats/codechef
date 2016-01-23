"""
   Codechef Unofficial API.

   Parses all the user data in JSON.

   Author: Shaurya Chaturvedi
           shauryachats@gmail.com

"""

import requests
from BeautifulSoup import BeautifulSoup
import os
import datetime
from collections import OrderedDict
import json
import zlib
import logging

# To convert text into 'key' format: i.e. "About me" becomes 'about_me'


def convertToKey(token):
    return token.lower().replace(' ', '_')

#
#	Helper function to parse the list of complete and partial problems.
#


def parseProblems(problemsC):
    problemDict = {}

    for problemGroup in problemsC:
        problemList = []
        problemGroupList = problemGroup.findAll('a')
        for problem in problemGroupList:
            problemList.append(problem.text)
        problemDict.update({problemGroup.b.text: problemList})

    return problemDict

"""
	getUserDataFromNet() does all the dirty work of parsing the HTML and junxing it altogether
	in a crude 'attributes' dict.
"""
# TODO : Try to parse the SVG image of the rating curve, to extract all data about the contest rating at any time.
# REFACTOR : Split all the parsing methods into seperate, for easy debugging.


def getUserDataFromNet(username,
                updatePageTime=0,
                dumpToJSON=False,
                JSONFileName=None,
                JSONFileReadable=False,
                debug=False):
    # Dictionary returning all the scraped data from the HTML.
    attributes = OrderedDict()

    downloadPage(username, updatePageTime)

    soup = BeautifulSoup(open(".codechef/" + username, "r").read())

    # The profile_tab contains all the data about the user.
    profileTab = soup.find("div", {'class': "profile"})
    # print profileTab
    attributes.update(
        {"real_name": profileTab.table.text.replace("&nbsp;", '')})

    row = profileTab.table.findNext("table").tr
    # print mainDataTable

    #
    #	Parsing the personal data of the user.
    #
    while not row.text.startswith("Problems"):
        # Strip the text of unwanted &nbsp, and splitting via the :
        parsedText = row.text.replace("&nbsp;", '').split(':')
        attributes.update({convertToKey(parsedText[0]): parsedText[1]})
        row = row.findNext("tr")
    #
    #	Removing unwanted keys from attributes
    #
    unwantedKeys = ["student/professional", "teams_list", "link", "motto"]
    for key in unwantedKeys:
        try:
            attributes.pop(key, None)
        except KeyError:
            pass

    #
    #	Parsing the complete problem list.
    #
    problemsComplete = row.td.findNext('td').findAll('p')
    completeProblemDict = OrderedDict()
    attributes.update({'complete_problem': parseProblems(problemsComplete)})

    #
    #	Parsing the partial problem list.
    #
    problemsPartial = row.findNext('tr').td.findNext('td').findAll('p')
    partialProblemDict = OrderedDict()
    attributes.update({'partial_problem': parseProblems(problemsComplete)})

    #
    #	Parsing the problem_stats table to get the number of submissions, WA, RTE, and the stuff.
    #
    problemStats = soup.find(
        "table", id="problem_stats").tr.findNext('tr').findAll('td')
    problemStats = [item.text for item in problemStats]
    stats = {}
    keys = ['prob_complete', 'prob_partial', 'prob_submit',
            'ac_partial', 'ac_complete', 'wa', 'cte', 'rte', 'tle']
    for i in xrange(0, len(problemStats) - 1):
        stats[keys[i]] = problemStats[i]
    # print stats
    attributes.update({'problem_stats': stats})

    #
    #	Parsing the rating table to get the current ratings of the user.
    #
    ratingTable = soup.find("table", {'class': "rating-table"}).findAll('tr')[1:4]
    ratingList = {}
    keys = ['long', 'short', 'ltime']
    for i, tr in enumerate(ratingTable):
        tr = tr.findAll('td')[1:3]
        parsedText = tr[0].text
        # If the user has not yet got a rank, set it to 0.
        if (parsedText == "NA"):
            parsedText = "0/0"
        parsedText = parsedText.split('/')
        ratingList.update( { keys[i]: [ parsedText[0], parsedText[1], tr[1].text.replace('&nbsp;(?)', '') ] } )
    # print ratingList
    attributes.update( {'rating_table': ratingList } )
    # print ratingList

    #
    #  Utility to dump the parsed 'attributes' dict in a JSON file for readability/compression.
    #
    if (dumpToJSON):
        if (debug):
            print "Dumping 'attributes' dict into a JSON file."

        # If no name for JSON file is passed, name the file as the username.
        if (JSONFileName is None):
            JSONFileName = username

        # JSON file should not be compressed.
        if (JSONFileReadable):
            with open(JSONFileName + '.json', 'w') as alp:
                alp.write(json.dumps(attributes, indent=4))
        else:
            #Compressed JSON files to be denoted by cjson
            with open(JSONFileName + '.cjson', 'wb') as alp:
                # Use zlib library to compress JSON.
                alp.write(zlib.compress(json.dumps(attributes, indent=0)))

    return attributes

"""
    getUserDataFromFile() returns the 'attributes' from a .json or a .cjson file.
"""
def getUserDataFromFile (filename):

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
	downloadPage() method downloads the respective HTML file, and returns the error code.
"""
def downloadPage(username, time_out_time=0):
    file_path = ".codechef/" + username
    url_path = "http://www.codechef.com/users/" + username

    # Check if .codechef is there. If not, create it.
    if (not os.path.exists(".codechef")):
        os.makedirs(".codechef")

    # Check if the webpage is there.
    # If not, download.
    # If yes, check for the time_out_time and if time_diff > time_out_time, redownload.
    # Else, do nothing.

    download_page = False

    if (not os.path.exists(file_path)):
        download_page = True
        print "Page does not exist. Downloading..."

    else:
        downloaded_time = datetime.datetime.fromtimestamp(
            os.path.getmtime(file_path))
        time_difference = datetime.datetime.now() - downloaded_time

        if (int(time_difference.seconds) > time_out_time):
            os.remove(file_path)
            download_page = True
            print "Downloaded page is expired. Redownloading..."

        else:
            return "ALREADY_DOWNLOADED"

    if (download_page == True):

        # If username exists, only 1 redirection will follow.
        # Else, 2 redirections. Hence, we invalidate >= 2 requests.
        request = requests.Session()
        request.max_redirects = 1

        try:
            web_page = request.get(url_path).text
        except requests.TooManyRedirects:
            raise Exception('Username not found.')
        # When the network is down i.e. WiFi is not connected or bleh.
        except IOError:
            raise Exception('Cannot connect to codechef.com')

        # If correct user's page is downloaded, save it to the page.
        page = open(file_path, "wb")
        page.write(web_page)
        page.close()
        return "SUCCESS"
