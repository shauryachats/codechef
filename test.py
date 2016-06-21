#!/usr/bin/env python

import codechef.contest
import codechef.user
import codechef.problem
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
	b = codechef.contest.getContestData('LTIME30', expiryTime = 1000000, writeInFile = True)
	print json.dumps(b, indent = 4)

#Testing contest.getContestList()
if 'c' in str(sys.argv):
	c = codechef.contest.getContestList(expiryTime = 100000, writeInFile = True)
	print json.dumps(c, indent = 4)

#Testing problem.getProblemData()
if 'd' in str(sys.argv):
	d = codechef.problem.getProblemData('TEST', expiryTime = 10000, writeInFile = True)
	print json.dumps(d, indent = 4)


elif 'e' in str(sys.argv):
	codechef.utils.downloadProblemPage('JAN16')
	codechef.utils.downloadProblemPage('TEST')