"""
   Codechef Unofficial API.

   Parses all the user data in JSON.

   Author: Shaurya Chaturvedi
           shauryachats@gmail.com

"""

from BeautifulSoup import BeautifulSoup
import os
from collections import OrderedDict
import json
import logging
import re
import datetime
import time

from utils import *
import globals
from problem import getProblemData
from contest import getContestList, getContestData



#
#   Helper function for getUserData() to parse the list of complete and partial problems.
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

def getUserData(username , expiryTime = None, writeInFile = None):

    #Fetching global variables from globals.py
    expiryTime, writeInFile = getGlobals(expiryTime, writeInFile)

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

    #Add the username too, for convinenece.
    attributes['username'] = username

    #The real name is present in a simple div.user-name-box,
    attributes['realname'] = profileTab.find('div', {'class' : 'user-name-box'}).text

    #The displayPicture link is present in div.user-thumb-pic
    attributes['display_picture'] = profileTab.find('div', {'class' : 'user-thumb-pic'}).img['src']

    if (attributes['display_picture'].startswith('/sites/')):
        attributes['display_picture'] = "https://www.codechef.com/" + attributes['display_picture']    

    row = profileTab.table.findNext("table").tr
    #
    #   Parsing the personal data of the user.
    #
    while not row.text.startswith("Problems"):
        # Strip the text of unwanted &nbsp, and splitting via the :
        parsedText = row.text.replace("&nbsp;", '').split(':')
        attributes[ convertToKey(parsedText[0]) ] = parsedText[1]
        row = row.findNext("tr")

    #
    #   Removing unwanted keys from attributes (for now)
    #
    unwantedKeys = ["studentprofessional", "teams_list", "link", "motto"]
    attributes = removeKeys(attributes, unwantedKeys)

    #
    #   Parsing the complete problem list.
    #
    problemsComplete = row.td.findNext('td').findAll('p')
    completeProblemDict = OrderedDict()
    attributes['complete_problem'] = parseProblems(problemsComplete)

    #
    #   Parsing the partial problem list.
    #
    problemsPartial = row.findNext('tr').td.findNext('td').findAll('p')
    partialProblemDict = OrderedDict()
    attributes['partial_problem'] = parseProblems(problemsPartial)

    #
    #   Parsing the problem_stats table to get the number of submissions, WA, RTE, and the stuff.
    #
    problemStats = soup.find("table", id="problem_stats").tr.findNext('tr').findAll('td')
    problemStats = [item.text for item in problemStats]

    #
    #   Parsing the problem submission statistics.
    #
    stats = {}
    keys = ['pc', 'pp', 'ps', 'acp', 'acc', 'wa', 'cte', 'rte', 'tle']
    for i in xrange(0, len(problemStats)):
        stats[keys[i]] = int(problemStats[i])
    attributes['stats'] = stats

    #
    #   Parsing the rating table to get the current ratings of the user.
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
    
    attributes['rating'] = ratingList 

    #   Compress and write into the CJSON file as requested.
    if writeInFile:
        print '[*] Writing object to ' + username + '.cjson'
        writeToFile('users/' + username, attributes)

    return attributes

#
#   Returns the most recent submittions by a user.
#
def getRecent(username, numberOfSub = 10):

    content = [] 
    pageno = 0

    while (len(content) < numberOfSub):
        soup = downloadRecentPage(username, pageno)

        for tr in soup.table.tbody.findAll('tr'):
            tds = tr.findAll('td')
            data = {}

            #TODO: Try to reduce timestamp conversion module.
            subTime = tds[0].text
            #Try to parse it as a strptime object.
            try:
                a = datetime.datetime.strptime(subTime, "%I:%M %p %d/%m/%y")
                subTime = int(time.mktime(a.timetuple()))
            except ValueError:
                #This was submitted less than 24 hours ago.
                texts = subTime.split(' ')
                val = int(texts[0]) #Get the numeric part.
                if texts[1] == 'min':
                    val *= 60
                elif texts[1] == 'hours':
                    val *= 3600
                else:
                    pass
                subTime = int(time.mktime((datetime.datetime.now().timetuple()))) - val
            
            data['sub_time'] = subTime
            data['problem_code'] = tds[1].a['href'].split('/')[-1]
            data['type'] = tds[2].span['title']
            data['points'] = tds[2].text
            if data['points'] != '':
                data['type'] = 'accepted'
            data['language'] = tds[3].text

            content.append( data )

        pageno += 1

    #Truncating
    return content[:numberOfSub]

#
#   Returns all the problems (complete/partial) solved by the username, in a list.
#
def getAllProblems(username, expiryTime = None, writeInFile = None, completeProblems = False, partialProblems = False):

    if not completeProblems and not partialProblems:
        completeProblems = True
        partialProblems = True

    userdata = getUserData(username, expiryTime, writeInFile)

    bucket = []
    if completeProblems:
        bucket += [problem for contest in userdata['complete_problem'] for problem in userdata['complete_problem'][contest]]
    if partialProblems:
        bucket += [problem for contest in userdata['partial_problem'] for problem in userdata['partial_problem'][contest]]

    return bucket    

#
#   Returns all the contests (complete/partial) attempted by the user, in a list.
#
def getAllContests(username, expiryTime = None, writeInFile = None):

    userdata = getUserData(username, expiryTime, writeInFile)

    bucket = set() #Since some contest might have partially solved and completely solved problems.
    for contest in userdata['complete_problem']:
        bucket.add(contest)
    for contest in userdata['partial_problem']:
        bucket.add(contest)

    return list(bucket)