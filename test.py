#!/usr/bin/env python

#import codechef.contest
import codechef.user
#import codechef.problem
import codechef.utils
import json
import sys

print str(sys.argv)

#Testing user.getUserData()
if 'a' in str(sys.argv):
	a = codechef.user.getUserData('shauryachats', expiryTime = 1000, writeInFile = True)
	print json.dumps(a, indent = 4)

#Testing contest.getContestData()
if 'b' in str(sys.argv):
	b = codechef.contest.getContestData('LTIME30', timeOutTime = 1000000)
	print json.dumps(b, indent = 4)

#Testing contest.getContestList()
if 'c' in str(sys.argv):
	c = codechef.contest.getContestList(timeOutTime = 100000)
	print json.dumps(c, indent = 4)

#Testing problem.getProblemData()
if 'd' in str(sys.argv):
	d = codechef.problem.getProblemData('TEST', timeOutTime = 0)
	print json.dumps(d, indent = 4)
