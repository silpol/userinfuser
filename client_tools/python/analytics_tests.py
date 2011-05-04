# Copyright (C) 2011, CloudCaptive
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import time
import sys
import inspect
from userinfuser.ui_api import *
from userinfuser.ui_constants import *
pwd = os.getcwd()
# Test to make sure it can read the API key from the env
prime_path = "http://localhost:8080/api/1/test"
delete_path = "http://localhost:8080/api/1/testcleanup"
IS_LOCAL = True
# ID settings for testing
account = "test@test.c"
testId = "testuserid"
testId2 = "anotheruser"
testId3 = "anotheruserxxxx"
testSecret = "8u8u9i9i"
# Set API key
apiKey = "ABCDEFGHI"
DEFAULT_DEBUG = True
# Turn this off/on to leave or delete data from the db 
cleanup = False
# TODO test async calls
def __url_post(url, argsdic):
  import urllib
  import urllib2
  import socket
  socket.setdefaulttimeout(30) 
  if argsdic:
    url_values = urllib.urlencode(argsdic)

  req = urllib2.Request(url, url_values)
  response = urllib2.urlopen(req)
  output = response.read()

  return output  

""" Make sure what we received is what we expected """
def checkerr(line_num, received, expected):
  if expected != received:
    print "Failed for test at " + sys.argv[0] + ": " + str(line_num) + \
          " with a return of: " + str(received) + " while expecting: " + str(expected)
    exit(1)

""" Make sure the item is not what we received """
def notcheckerr(line_num, received, shouldnotbe):
  if shouldnotbe == received:
    print "Failed for test at " + sys.argv[0] + ": " + str(line_num) \
        + " with a return of: " + str(received) + \
        " while it should not be but was: " + str(shouldnotbe)
    exit(1)

""" See if the given string is contained in the response """
def checkstr(line_num, received, searchstr):
  if searchstr not in str(received):
    print "Failed for test at " + sys.argv[0] + ":" + str(line_num) \
        + " with a return of: " + str(received) + \
        " while searching for: " + searchstr
    exit(1)

""" See if the given string is not contained in the response """
def checknotstr(line_num, received, searchstr):
  if searchstr not in received:
    return
  else:
    print "Failed for test at " + sys.argv[0] + ":" + str(line_num) \
        + " with a return of: " + str(received) + \
        " while searching for: " + searchstr + " where it should not be"
    exit(1)
      
def lineno():
  return inspect.currentframe().f_back.f_lineno
badgetheme1 = "music"
badgetheme2 = "birds"


badgeId1 = "1-badge1-private"
# Prime the DB with an account and badges
argsdict = {"apikey":apiKey,
           "accountid":account,
           "badgeid":badgeId1,
           "secret":testSecret,
           "user":testId,
           "theme":badgetheme1}

ret = __url_post(prime_path, argsdict)
checkstr(lineno(), ret, "success")
ret = __url_post(delete_path, argsdict)
checkstr(lineno(), ret, "success")
ret = __url_post(prime_path, argsdict)
checkstr(lineno(), ret, "success")

badge_name1, badge_theme1, description1, link1 = "badge1", "1", "badge", "http://cdn1.iconfinder.com/data/icons/DarkGlass_Reworked/128x128/actions/emoticon.png"
badge_name2, badge_theme2, description2, link2 = "badge2", "2", "badge", "http://cdn1.iconfinder.com/data/icons/DarkGlass_Reworked/128x128/actions/emoticon.png"
badge_name3, badge_theme3, description3, link3 = "badge3", "3", "badge", "http://cdn1.iconfinder.com/data/icons/DarkGlass_Reworked/128x128/actions/emoticon.png"
ui_good = UserInfuser(account, apiKey, debug=DEFAULT_DEBUG, local=IS_LOCAL, sync_all=True)

badgeId1 = "1-badge1-private"
badgeId2 = "2-badge2-private"
badgeId3 = "3-badge3-private"

checkstr(lineno(), ui_good.create_badge(badge_name1, badge_theme1, description1, link1), "True")
checkstr(lineno(), ui_good.create_badge(badge_name2, badge_theme2, description2, link2), "True")
checkstr(lineno(), ui_good.create_badge(badge_name3, badge_theme3, description3, link3), "True")

for ii in range(0,1000):
  checkerr(lineno(), ui_good.update_user(str(ii), "Raj", "http://facebook.com/nlake44", "http://imgur.com/AK9Fw"), True)
  checkerr(lineno(), ui_good.award_badge(str(ii), badgeId1, reason="Star Power"), True)
  checkerr(lineno(), ui_good.award_badge(str(ii), badgeId2, reason="Star Power"), True)
  checkerr(lineno(), ui_good.award_badge(str(ii), badgeId3, reason="Star Power"), True)
  
# Now set off the analytics for counting badges and see if the count equals 30
