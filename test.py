#!/usr/bin/env python

import codechef.contest
import codechef.user
import codechef.problem
import codechef.utils
import codechef.globals
import json
import sys

print str(sys.argv)

#Testing globals variables.
codechef.globals.EXPIRY_TIME = 200000
codechef.globals.WRITE_IN_FILE = True

#Testing user.getUserData()
if 'a' in str(sys.argv[1]):
	a = codechef.user.getUserData('shauryachats')
	print json.dumps(a, indent = 4)

#Testing contest.getContestData()
if 'b' in str(sys.argv[1]):
	b = codechef.contest.getContestData('IOIPRAC')
	print json.dumps(b, indent = 4)

#Testing contest.getContestList()
if 'c' in str(sys.argv[1]):
	c = codechef.contest.getContestList(present = True, future = True)
	print json.dumps(c, indent = 4)

#Testing problem.getProblemData()
if 'd' in str(sys.argv[1]):
	d = codechef.problem.getProblemData('CHEFTET')
	print json.dumps(d, indent = 4)

#Testing user.getRecent()
if 'e' in str(sys.argv[1]):
	e = codechef.user.getRecent('shauryachats')
	print json.dumps(e, indent = 4)

#Testing user.getAllProblems()
if 'f' in str(sys.argv[1]):
	f = codechef.user.getAllProblems('shauryachats', completeProblems = True)
	print f

#Testing user.getAllContests()
if 'g' in str(sys.argv[1]):
	g = codechef.user.getAllContests('anta0')
	print g