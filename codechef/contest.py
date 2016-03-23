from utils import downloadPage, dumpData
import json
from BeautifulSoup import BeautifulSoup
from collections import OrderedDict

"""
    getContestList() parses all the contests from codechef.com/contests

    It can also return data of a particular contest, if findContest is not None

    It can also return contest list according to Future, Present, or Past contests.

"""
def getContestList(findContest = None, timeOutTime = 0, futureContest = False, presentContest = False, pastContest = False):

    soup = downloadPage('contests', timeOutTime = timeOutTime)

    #OrderedDict for easy visualisation, but it is kind of slow.
    contestData = {}

    tableList = soup.findAll('div', { 'class' : 'table-questions'})
    
    """
        If there are two tableList divs, the first one will be future contests,
        and the second one will be past contests.

        If there are three tableList divs, the first one will be present contests,
        the second one will be future contests and the third one will be past contests.
    
    """

    #If by default, none of the contests is marked True, return details of ALL the contests.
    if not(futureContest or presentContest or pastContest):
        futureContest = True
        presentContest = True
        pastContest = True

    variables = []

    if len(tableList) == 3:
        variables.append('presentContest')
        variables.append('futureContest')
        variables.append('pastContest')
    elif len(tableList) == 2:
        variables.append('futureContest')
        variables.append('pastContest')        
    else:
        variables.append('pastContest')

    i = 0

    for table in tableList:
        if eval(variables[i]) == True:
            rows = table.table.findAll('tr')        
                
            #Skipping the first row, which contains the titles.
            for row in rows[1:]:
                row = row.findAll('td')
                tempData = []
                
                #The first td here contains the contest code, which we use to make the key.
                for td in row[1:]:
                    tempData.append(td.text)
                         
                contestData.update( { row[0].text : tempData } )
        
        i += 1


    #
    #   Looking for the findContest contest.
    #
    if (findContest is not None):
        #Search through contestData for the findContest key and return its data.
        if findContest in contestData:
            return contestData[findContest]
        else:
            raise Exception('Contest not found in contest list.')
    else:
        return contestData


"""
    Returns the list of Problem and other data from the contest page.
"""
def getContestData(contestCode, timeOutTime = 0):
    attributes = {}

    soup = downloadPage(contestCode, timeOutTime=timeOutTime, isContest = True)
    
    contestData = getContestList(findContest = contestCode, timeOutTime = timeOutTime)

    attributes['title'] = contestData[0]
    #TODO: Parse timestamps out of strings using datetime module.
    attributes['start_time'] = contestData[1]
    attributes['end_time'] = contestData[2]

    dataTable = soup.find('table', { 'class' : 'problems'} )
    problemRow = dataTable.findAll('tr', { 'class' : 'problemrow'})

    #
    #   Parsing the list of problems and the basic stats.
    #   
    problemList = {}
    for problem in problemRow:
        problem = problem.findAll('td')
        tempList = {}
        tempList.update({"problem_name" : problem[0].text})
        tempList.update({"solved" : problem[2].text})
        tempList.update({"accuracy" : problem[3].text})
        problemList[ problem[1].text ] = tempList 

    attributes['problem_list'] = problemList

    #
    #   Checking if the contest is a Team Contest or not.
    #   Using the naive assumption that "Team Registration Link" appears only in a team contest.
    #
    if (len(soup.body.findAll(text='Team Registration Link')) > 0):
        attributes['team'] = True
    else:
        attributes['team'] = False

    return attributes
