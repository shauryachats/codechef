from utils import *
import json
import datetime
import time
from BeautifulSoup import BeautifulSoup

def getContestInList(contestList, present, past, future):
    bucket = []
    if future:
        bucket += contestList['future']
    if present:
        bucket += contestList['present']
    if past:
        bucket += contestList['past']
    return bucket

"""
    getContestList() parses all the contests from codechef.com/contests
    It can also return data of a particular contest, if findContest is not None
    It can also return contest list according to Future, Present, or Past contests.
"""
def getContestList(expiryTime = 0, writeInFile = False, present = False, past = False, future = False):

    contestList = {}

    if expiryTime > 0:
        contestList = checkInFile('contests', expiryTime)
        if contestList is not None:
            return getContestInList(contestList, present, past, future)
        else:
            contestList = {}

    if not present and not past and not future:
        present = True
        past = True
        future = True
    
    soup = downloadContestList()

    tableList = soup.find('div', { 'class' : 'content-wrapper'})

    #
    #   Since "Present Contests", "Future Contests" and the like 
    #   are encapsulated in a <h3>, we can use that to find which
    #   all contests are present.
    #
    for contestType in tableList.findAll('h3'):

        key = None
        if str(contestType.text).startswith('Present'):
            key = "present"
        elif str(contestType.text).startswith('Future'):
            key = "future"
        elif str(contestType.text).startswith('Past'):
            key = "past"

        bucket = []
        #The div containing the contest list is next to the h3 tag.
        for tr in contestType.findNext('div').table.tbody.findAll('tr'):
        
            #
            #   'tr' contains a row containing the contestcode, contestname, start
            #   and end time of all the contests.
            #
            contestData = {}
            
            tdList = tr.findAll('td')
            
            contestData['code'] = tdList[0].text
            contestData['name'] = tdList[1].text
            a = datetime.datetime.strptime(tdList[2].text, "%Y-%m-%d %H:%M:%S")
            contestData['start_time'] = int(time.mktime(a.timetuple()))
            b = datetime.datetime.strptime(tdList[3].text, "%Y-%m-%d %H:%M:%S")
            contestData['end_time'] = int(time.mktime(b.timetuple()))

            bucket.append(contestData)

        contestList[ key ] = bucket

    if writeInFile:
        writeToFile('contests', contestList)

    return getContestInList(contestList, present, past, future)
        
#
#   Parses contest data using CodeChef's sneaky Internal API.
#
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