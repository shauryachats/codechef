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

from utils import downloadPage, putDataInFile, getDataFromFile
from problem import getProblemData

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

    def __init__(self, contestCode):
        self.contestCode = contestCode
        self.problemList = []

    def fetch(self):
        pass

class Problem:

    def __init__(self, problemCode):
        self.problemCode = problemCode
        self.attributes = {}

    def fetch(self):
        pass



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

def getUserData(username,
                updatePageTime=0,
                dumpToJSON=False,
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

    #
    #  Dumping the attributes into a JSON as requested.
    #
    if (dumpToJSON):
        if (JSONFileReadable):
            putDataInFile(username, attributes, compressed=False)
        else:
            putDataInFile(username, attributes, compressed=True)

    return attributes

"""
    getContestList() parses all the contests from codechef.com/contests
"""
def getContestList(updatePageTime = 0, dumpToJSON=False):

    downloadPage('contests',updatePageTime)
    import sys
    sys.exit(0)
    soup = BeautifulSoup(open(".codechef/contests").read())
    #print soup

    contest_data = {}

    table_list = soup.findAll('div', { 'class' : 'table-questions'})
    for table in table_list[0:2]:
        rows = table.table.findAll('tr')
        #Skipping the first row, which contains the titles.
        for row in rows[1:]:
            row = row.findAll('td')
            temp_data = []
            #The first td here contains the contest code, which we use to make the key.
            for td in row[1:]:
                temp_data.append(td.text)
            contest_data.update( { row[0].text : temp_data } )

    if (dumpToJSON):
        putDataInFile('contests',contest_data,compressed=False)

    return contest_data

def getContestData(contestCode):
    downloadPage(contestCode, 15000)
    with open('.codechef/contest/' + contest_code, "r") as alp:
        soup = BeautifulSoup(alp.read())

    dataTable = soup.find('table', { 'class' : 'problems'} )
    problemRow = dataTable.findAll('tr', { 'class' : 'problemrow'})
    
    problemList = {}

    for problem in problemRow:
        problem = problem.findAll('td')
        tempList = []
        for items in problem[2:]:
            tempList.append(items.text)
        problemList.update( { problem[1].text : tempList } )

    print json.dumps(problemList,indent=4)

    return problemList
