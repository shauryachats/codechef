from utils import downloadPage, putDataInFile
import json
from BeautifulSoup import BeautifulSoup

"""
    getContestList() parses all the contests from codechef.com/contests
"""
def getContestList(timeOutTime = 0):

    soup = downloadPage('contests', timeOutTime)

    #soup = BeautifulSoup(open(".codechef/contests").read())
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

    return contest_data

"""
    Returns the list of Problem and other data from the contest page.
"""
def getContestData(contestCode):
    
    soup = downloadPage(contestCode, 15000)
    
    dataTable = soup.find('table', { 'class' : 'problems'} )
    problemRow = dataTable.findAll('tr', { 'class' : 'problemrow'})
    
    problemList = {}

    for problem in problemRow:
        problem = problem.findAll('td')
        tempList = []
        for items in problem[2:]:
            tempList.append(items.text)
        problemList.update( { problem[1].text : tempList } )

    return problemList
