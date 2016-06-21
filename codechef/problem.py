from BeautifulSoup import BeautifulSoup
import re
import json
from utils import *

"""
    Scraps problem metadata from the problem data.
    DOES NOT PARSE THE PROBLEM STATEMENT

    To parse the problem statement, use getProblemStatement()
"""
def getProblemData(problemCode, expiryTime = 0, writeInFile = False):
    attributes = {}

    if expiryTime > 0:
        attributes = checkInFile('problems/' + problemCode, expiryTime)

        if attributes is not None:
            return attributes
        else:
            attributes = {}

    #soup = downloadPage(problemCode, expiryTime, isProblem = True)
    soup = downloadProblemPage(problemCode)

    title = soup.find('h1')
                                    #Removed uneven spacing in the title.
    attributes.update( { 'title' : re.sub(' +', ' ', title.contents[0])[:-1] } )

    #Find the details table.
    table = soup.find('table', {'align' : 'left'} )
    table = table.findAll('tr')
    
    for tr in table:
        tr = tr.findAll('td')
        key = camelCase(tr[0].text)
        #For tags, we need to seperate the tags from the <a>
        if (key == 'tags'):
            temp = tr[1].findAll('a')
            lis = [a.text for a in temp]
            attributes.update( { key : lis } )
        #For languages, we have to split the string into a list.
        elif (key == 'languages'):
            attributes.update( { key : tr[1].text.split(', ')})
        else:
            attributes.update( { key : tr[1].text } )

    if writeInFile:
        writeToFile('problems/' + problemCode, attributes)
    
    return attributes

"""
    
"""