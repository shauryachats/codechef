import codechef.contest
import codechef.user
import codechef.problem
import json

#Testing user.getUserData()
a = codechef.user.getUserData('shauryachats', timeOutTime = 86400)
print json.dumps(a, indent = 4)

#Testing contest.getContestData()
b = codechef.contest.getContestData('LTIME20', timeOutTime = 86400)
print json.dumps(b, indent = 4)

#Testing contest.getContestList()
c = codechef.contest.getContestList(timeOutTime = 86400)
print json.dumps(c, indent = 4)

#Testing problem.getProblemData()
d = codechef.problem.getProblemData('TEST', timeOutTime = 86400)
print json.dumps(d, indent = 4)