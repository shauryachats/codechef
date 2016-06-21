"""
   Codechef Unofficial API.

   Parses all the user data in JSON.

   Author: Shaurya Chaturvedi
           shauryachats@gmail.com


    TODO: Create a tester program, which can check if each method is working perfectly or not.
"""

from BeautifulSoup import BeautifulSoup
import os
from collections import OrderedDict
import json
import logging
import re


from utils import *
from problem import getProblemData
from contest import getContestList, getContestData

#
#	Helper function for getUserData() to parse the list of complete and partial problems.
#
def parseProblems(problemsC):
    problemDict = OrderedDict()

    for problemGroup in problemsC:
        problemList = []
        problemGroupList = problemGroup.findAll('a')
        for problem in problemGroupList:
            problemList.append(problem.text)
        
        #Added arbitary contest code "PRACTICE" for practice problems.
        problemDict[ "PRACTICE" if problemGroup.b.text.startswith("Practice") else problemGroup.b.text ] = problemList

    return problemDict

"""
	getUserData() does all the dirty work of parsing the HTML and junxing it altogether
	in a crude 'attributes' dict.
"""

# TODO : Try to parse the SVG image of the rating curve, to extract all data about the contest rating at any time.
# REFACTOR : Split all the parsing methods into seperate, for easy debugging.

def getUserData(username , expiryTime = 0, writeInFile = False):

    # Dictionary returning all the scraped data from the HTML.    
    attributes = OrderedDict()

    #
    #   Firstly, checking if the userdata is already stored in a CJSON file 
    #   which is not yet expired.
    #
    if expiryTime > 0:
        attributes = checkInFile('users/' + username, expiryTime)

    #   Returning the attributes object.
    if attributes is not None:
        print '[*] Found file. Returning object.'
        return attributes
    else:
        attributes = OrderedDict()

    soup = downloadUserPage(username)

    # The profile_tab contains all the data about the user.
    profileTab = soup.find('div', {'class': 'profile'})

    #   This profile consists of four tables.
    #
    #   ->  The first table just contains the real name of the user, and the display picture.
    #   ->  The second table contains the info about the user, and the problems info.
    #   ->  The third table contains the problem statistics.
    #   ->  The fourth table contains the performance graphs, in SVG format.
    #

    #The real name is present in a simple div.user-name-box,
    attributes['realName'] = profileTab.find('div', {'class' : 'user-name-box'}).text

    #The displayPicture link is present in div.user-thumb-pic
    attributes['displayPicture'] = profileTab.find('div', {'class' : 'user-thumb-pic'}).img['src']

    row = profileTab.table.findNext("table").tr
    #
    #	Parsing the personal data of the user.
    #
    while not row.text.startswith("Problems"):
        # Strip the text of unwanted &nbsp, and splitting via the :
        parsedText = row.text.replace("&nbsp;", '').split(':')
        attributes[ camelCase(parsedText[0]) ] = parsedText[1]
        row = row.findNext("tr")

    #
    #	Removing unwanted keys from attributes (for now)
    #
    unwantedKeys = ["student/professional", "teamsList", "link", "motto"]
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
    attributes['completeProblem'] = parseProblems(problemsComplete)

    #
    #	Parsing the partial problem list.
    #
    problemsPartial = row.findNext('tr').td.findNext('td').findAll('p')
    partialProblemDict = OrderedDict()
    attributes['partialProblem'] = parseProblems(problemsPartial)

    #
    #	Parsing the problem_stats table to get the number of submissions, WA, RTE, and the stuff.
    #
    problemStats = soup.find("table", id="problem_stats").tr.findNext('tr').findAll('td')
    problemStats = [item.text for item in problemStats]
    stats = {}
    keys = ['probComplete', 'probPartial', 'probSubmit',
            'acPartial', 'acComplete', 'wa', 'cte', 'rte', 'tle']
    for i in xrange(0, len(problemStats) - 1):
        stats[keys[i]] = int(problemStats[i])
    # print stats
    attributes['problemStats'] = stats

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
        ratingList[ keys[i] ] = [ int(parsedText[0]), int(parsedText[1]), float(tr[1].text.replace('&nbsp;(?)', '')) ] 
    
    attributes['ratingTable'] = ratingList 

    #   Compress and write into the CJSON file as requested.
    if writeInFile:
        print '[*] Writing object to ' + username + '.cjson'
        writeToFile('users/' + username, attributes)

    return attributes
