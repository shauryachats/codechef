from utils import downloadPage, putDataInFile
import json
from BeautifulSoup import BeautifulSoup

"""
    getContestList() parses all the contests from codechef.com/contests

    It can also return data of a particular contest, if findContest is not None
"""
def getContestList(findContest = None, timeOutTime = 0):

    soup = downloadPage('contests', timeOutTime = timeOutTime)

    contestData = {}

    tableList = soup.findAll('div', { 'class' : 'table-questions'})
    for table in tableList:
        rows = table.table.findAll('tr')
        #Skipping the first row, which contains the titles.
        for row in rows[1:]:
            row = row.findAll('td')
            tempData = []
            #The first td here contains the contest code, which we use to make the key.
            for td in row[1:]:
                tempData.append(td.text)
            contestData.update( { row[0].text : tempData } )

    if (findContest is not None):
        #Search through contestData for the findContest key and return its data.
        if findContest in contestData:
            return contestData[findContest]
        else:
            raise Exception('Contest not found.')
    else:
        return contestData


"""
    Returns the list of Problem and other data from the contest page.
"""
def getContestData(contestCode, timeOutTime = 0):
    attributes = {}

    soup = downloadPage(contestCode, timeOutTime=timeOutTime)
    
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
        tempList = []
        for items in problem[2:]:
            tempList.append(items.text)
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
