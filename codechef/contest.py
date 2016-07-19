from utils import *
import json
import datetime
import time
from BeautifulSoup import BeautifulSoup
from collections import OrderedDict

"""
    getContestList() parses all the contests from codechef.com/contests

    It can also return data of a particular contest, if findContest is not None

    It can also return contest list according to Future, Present, or Past contests.

"""
def getContestList(findContest = None, expiryTime = 0, writeInFile = False):

    contestList = OrderedDict()

    if expiryTime > 0:
        contestList = checkInFile('contests', expiryTime)
        if contestList is not None:
            return contestList
        else:
            contestList = OrderedDict()

    soup = downloadContestList()

    tableList = soup.find('div', { 'class' : 'content-wrapper'})

    #
    #   Since "Present Contests", "Future Contests" and the like 
    #   are encapsulated in a <h3>, we can use that to find which
    #   all contests are present.
    #
    for contestType in tableList.findAll('h3'):

        #The div containing the contest list is next to the h3 tag.
        for tr in contestType.findNext('div').table.tbody.findAll('tr'):
        
            #
            #   'tr' contains a row containing the contestcode, contestname, start
            #   and end time of all the contests.
            #
            contestData = OrderedDict()
            
            tdList = tr.findAll('td')
            
            contestCode = tdList[0].text

            contestData['name'] = tdList[1].text
            a = datetime.datetime.strptime(tdList[2].text, "%Y-%m-%d %H:%M:%S")
            #print a
            contestData['startTime'] = int(time.mktime(a.timetuple()))
            b = datetime.datetime.strptime(tdList[3].text, "%Y-%m-%d %H:%M:%S")
            #print b
            contestData['endTime'] = int(time.mktime(b.timetuple()))

            contestList[ contestCode ] = contestData


    if writeInFile:
        writeToFile('contests', contestList)

    #
    #   Looking for the findContest contest.
    #
    if (findContest is not None):
        #Search through contestList for the findContest key and return its data.
        if findContest in contestList:
            return contestList[findContest]
        else:
            raise Exception('Contest not found in contest list.')
    else:
        return contestList
        

"""
    Returns the list of Problem and other data from the contest page.
"""
def getContestDataOld(contestCode, expiryTime = 0, writeInFile = False):

    attributes = OrderedDict()

    if expiryTime > 0:
        attributes = checkInFile('contest/' + contestCode, expiryTime)

        if attributes is not None:
            return attributes
        else:
            attributes = OrderedDict()

    soup = downloadContestPage(contestCode)
    #soup = downloadPage(contestCode, expiryTime=expiryTime, isContest = True)
    attributes = getContestList(findContest = contestCode, expiryTime = expiryTime)



    dataTable = soup.find('table', { 'class' : 'dataTable' } )
    problemRow = dataTable.findAll('tr', { 'class' : 'problemrow'})

    #
    #   Parsing the list of problems and the basic stats.
    #   
    problemList = {}
    
    for problem in problemRow:
        problem = problem.findAll('td')
        tempList = {}
        tempList['name'] = problem[0].text
        tempList['solved'] = problem[2].text
        tempList['accuracy'] = problem[3].text
        
        problemList[ problem[1].text ] = tempList 

    attributes['problemList'] = problemList

    #
    #   Checking if the contest is a Team Contest or not.
    #   Using the naive assumption that "Team Registration Link" appears only in a team contest.
    #
    if (len(soup.body.findAll(text='Team Registration Link')) > 0):
        attributes['team'] = True
    else:
        attributes['team'] = False

    if writeInFile:
        writeToFile('contest/' + contestCode, attributes)

    return attributes


def getContestData(contestCode, expiryTime = 0, writeInFile = False):

    data = {}

    if expiryTime > 0:
        data = checkInFile('contest/' + contestCode, expiryTime)
        if data is not None:
            return data
        else:
            data = {}

    URL = "https://www.codechef.com/api/contests/" + contestCode

    data = json.loads(requests.get(URL).text)

    #Make start_time and end_time keys directly in data
    data['start_time'] = data['time']['start']
    data['end_time'] = data['time']['end']

    #Removing unnecessary keys.
    keysToRemove = ['problems_data','time','problemsstats', 'user', 'announcements', 'rules', 'autoRefresh', 'banner', 'todos']
    data = removeKeys(data, keysToRemove)

    #From here too.
    for contest in data['problems']:
        data['problems'][contest] = removeKeys(data['problems'][contest], ['status_url','submit_url','problem_url','allow_submission'])

    if writeInFile:
        writeToFile('contest/' + contestCode, data)

    return data