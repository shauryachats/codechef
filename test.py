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
	a = codechef.user.getUserData('sid02', expiryTime = 0, writeInFile = True)
	print json.dumps(a, indent = 4)

#Testing contest.getContestData()
if 'b' in str(sys.argv):
	b = codechef.contest.getContestData('LTIME30', expiryTime = 0, writeInFile = True)
	print json.dumps(b, indent = 4)

#Testing contest.getContestList()
if 'c' in str(sys.argv):
	c = codechef.contest.getContestList(expiryTime = 0, writeInFile = True)
	print json.dumps(c, indent = 4)

#Testing problem.getProblemData()
if 'd' in str(sys.argv):
	d = codechef.problem.getProblemData('CUBTOWER', expiryTime = 0, writeInFile = True)
	print json.dumps(d, indent = 4)


if 'f' in str(sys.argv):
	codechef.utils.downloadProblemPage('JAN16')
	codechef.utils.downloadProblemPage('TEST')