#!/usr/bin/env python

import codechef.contest
import codechef.user
import codechef.problem
import codechef.utils
import json
import sys

print str(sys.argv)

#Testing user.getUserData()
if 'a' in str(sys.argv[1]):
	a = codechef.user.getUserData('shauryachats', expiryTime = 0, writeInFile = True)
	print json.dumps(a, indent = 4)

#Testing contest.getContestData()
if 'b' in str(sys.argv[1]):
	b = codechef.contest.getContestData('LTIME30', expiryTime = 0, writeInFile = True)
	print json.dumps(b, indent = 4)

#Testing contest.getContestList()
if 'c' in str(sys.argv[1]):
	c = codechef.contest.getContestList(expiryTime = 0, writeInFile = True)
	print json.dumps(c, indent = 4)

#Testing problem.getProblemData()
if 'd' in str(sys.argv[1]):
	d = codechef.problem.getProblemData('COMPILER', expiryTime = 0, writeInFile = True)
	print json.dumps(d, indent = 4)


if 'f' in str(sys.argv[1]):
	codechef.utils.downloadProblemPage('JAN16')
	codechef.utils.downloadProblemPage('TEST')

if 'g' in str(sys.argv[1]):
	g = codechef.user.getRecent('shauryachats')
	print json.dumps(g, indent = 4)