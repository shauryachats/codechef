from BeautifulSoup import BeautifulSoup
import re
import json
from utils import *

"""
    Scraps data from CodeChef's sneaky API ( which it runs on AJAX, I just happened to scan XHR requests :P)

    If problemBody is True, returns the body in HTML.
"""
def getProblemData(problemCode, expiryTime = None, writeInFile = None, problemBody = False):

    expiryTime, writeInFile = getGlobals(expiryTime, writeInFile)
    #print expiryTime, writeInFile

    attributes = {}

    if expiryTime > 0:
        attributes = checkInFile('problems/' + problemCode, expiryTime)
        if attributes is not None:
            return attributes
        else:
            attributes = {}

    URL = 'https://www.codechef.com/api/contests/PRACTICE/problems/'
    
    attributes = json.loads(requests.get(URL + problemCode).text)
    attributes['problem_code'] = problemCode    

    if attributes['status'] == 'error':
        raise Exception('Invalid problem.')

    if problemBody == False:
        attributes.pop('body', None)
    
    soup = BeautifulSoup(attributes['tags'])
    attributes['tags'] = [b.text for b in soup.findAll('a')]

    if writeInFile:
        writeToFile('problems/' + problemCode, attributes)    

    return attributes

"""

"""
def getProblemSets():
    pass