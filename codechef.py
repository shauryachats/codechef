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


from utils import downloadPage, putDataInFile, getDataFromFile, convertToKey
from problem import getProblemData
from contest import getContestList, getContestData

"""
    
"""

class User:

    def __init__(self, username, timeOutTime = 0):
        self.username = username
        self.realName = None
        self.country = None
        self.institution = None
        #A dict of 'Contest'
        self.completeProblems = None
        #A dict of 'Contest'
        self.partialProblems = None

        self.timeOutTime = timeOutTime

    def fetch(self):
        attributes = getUserData(self.username, self.timeOutTime)

        self.username = attributes['username']
        self.realName = attributes['real_name']
        self.country = attributes['country']
        self.institution = attributes['institution']

        self.completeProblems = attributes['complete_problem']
        self.partialProblems = attributes['partial_problem']

    def __repr__(self):
        pass

class Contest:

    def __init__(self, contestCode, timeOutTime = 0):
        self.contestCode = contestCode
        self.problemList = []
        self.timeOutTime = timeOutTime
    
    def fetch(self):
        pass

"""
    The Problem class denotes
"""
class Problem:

    def __init__(self, problemCode, timeOutTime = 0, getProblemStatement = False):
        self.problemCode = problemCode
        self.attributes = {}
        self.timeOutTime = timeOutTime
        self.getProblemStatement = getProblemStatement
        self.problemStatement = None

    def fetch(self):
        self.attributes = getProblemData(self)
        if (self.getProblemStatement):
            attributes.update( {'problem_statement' : getProblemStatement(self) } )

    def __repr__(self):
        return "<%s instance with problemCode:%s , timeOutTime:%s>" % (self.__class__, self.problemCode, self.timeOutTime)

#
#	Helper function for getUserData() to parse the list of complete and partial problems.
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

def getUserData(username , timeOutTime=0):
    # Dictionary returning all the scraped data from the HTML.
    attributes = OrderedDict()

    soup = downloadPage(username, timeOutTime)

    # The profile_tab contains all the data about the user.
    profileTab = soup.find("div", {'class': "profile"})

    attributes.update(
        {"real_name": profileTab.table.text.replace("&nbsp;", '')})

    row = profileTab.table.findNext("table").tr

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
    attributes.update({'partial_problem': parseProblems(problemsPartial)})

    #
    #	Parsing the problem_stats table to get the number of submissions, WA, RTE, and the stuff.
    #
    problemStats = soup.find("table", id="problem_stats").tr.findNext('tr').findAll('td')
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
    
    attributes.update( {'rating_table': ratingList } )

    return attributes
