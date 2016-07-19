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
	b = codechef.contest.getContestData('IOIPRAC', expiryTime = 0, writeInFile = True)
	print json.dumps(b, indent = 4)

#Testing contest.getContestList()
if 'c' in str(sys.argv[1]):
	c = codechef.contest.getContestList(expiryTime = 000000, writeInFile = True)
	print json.dumps(c, indent = 4)

#Testing problem.getProblemData()
if 'd' in str(sys.argv[1]):
	d = codechef.problem.getProblemData('CHEFTET', expiryTime = 0, writeInFile = True)
	print json.dumps(d, indent = 4)

#Testing user.getRecent()
if 'e' in str(sys.argv[1]):
	e = codechef.user.getRecent('shauryachats')
	print json.dumps(e, indent = 4)

