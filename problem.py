from BeautifulSoup import BeautifulSoup
import re
import json
from utils import downloadPage, convertToKey


"""
    Scraps problem metadata from the problem data.
    DOES NOT PARSE THE PROBLEM STATEMENT

    To parse the problem statement, use getProblemStatement()
"""
def getProblemData(problemCode):
    attributes = {}

    downloadPage(problemCode, 99999, isProblem = True)
    
    with open('.codechef/problem/' + problemCode) as alp:
        soup = BeautifulSoup(alp.read())

    title = soup.find('h1')
                                    #Removed uneven spacing in the title.
    attributes.update( { 'title' : re.sub(' +', ' ', title.contents[0])[:-1] } )

    #Find the details table.
    table = soup.find('table', {'align' : 'left'} )
    table = table.findAll('tr')
    for tr in table:
        tr = tr.findAll('td')
        key = convertToKey(tr[0].text)
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
    
    print json.dumps(attributes, indent=4)
    return attributes

