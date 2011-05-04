# Copyright (C) 2011, CloudCaptive
# 
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
#
'''
Created on Feb 1, 2011

@author: shan

Console class that will render the user console and provide additional functionality if needed.
'''
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.api import mail
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore 

from serverside import constants
from serverside.session import Session
from serverside.tools.utils import account_login_required
from serverside.dao import widgets_dao
from serverside.dao import badges_dao
from serverside.dao import accounts_dao
from serverside import messages

import logging
import wsgiref.handlers

class Console(webapp.RequestHandler):
  @account_login_required
  def get(self):
    """ Render dashboard """
    current_session = Session().get_current_session(self)
    
    account = current_session.get_account_entity()
    api_key = account.apiKey
    
    template_values = {'dashboard_main' : True,
                       'account_name': current_session.get_email(),
                       'api_key': api_key}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))

class ConsoleUsers(webapp.RequestHandler):
  @account_login_required
  def get(self):
    """ Render users template """
    current_session = Session().get_current_session(self)
    email = current_session.get_email()
    
    template_values = {'users_main': True,
                       'account_name': email }
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))

class ConsoleBadges(webapp.RequestHandler):
  @account_login_required
  def get(self):
    current_session = Session().get_current_session(self)
    email = current_session.get_email()
    account = current_session.get_account_entity()
    
    badgeset = badges_dao.get_rendereable_badgeset(account)
    upload_url = blobstore.create_upload_url('/badge/u')
    template_values = {'badges_main': True,
                       'account_name': email,
                       'badges': badgeset,
                       'upload_url': upload_url}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))

class ConsoleEditUser(webapp.RequestHandler):
  @account_login_required
  def get(self):
    """
    Verify that specified user exists for given account
    """
    current_session = Session().get_current_session(self)
    email = current_session.get_email()
    edit_user = self.request.get("name")
    
    """ Generate links to see each widget for user """
    import hashlib
    userhash = hashlib.sha1(email + '---' + edit_user).hexdigest()
    
    trophy_case_widget_url = "/api/1/getwidget?widget=trophy_case&u=" + userhash
    points_widget_url = "/api/1/getwidget?widget=points&u=" + userhash
    rank_widget_url = "/api/1/getwidget?widget=rank&u=" + userhash 
    
    template_values = {'users_edit' : True,
                       'account_name' : current_session.get_email(),
                       'editusername': edit_user,
                       'view_trophy_case':trophy_case_widget_url,
                       'view_points':points_widget_url,
                       'view_rank':rank_widget_url}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))

class ConsoleUsersFetch(webapp.RequestHandler):
  @account_login_required
  def get(self):
    """ Params page, limit """
    page = self.request.get("page")
    limit = self.request.get("limit")
    order_by = self.request.get("orderby")
    
    if page == None or page == "" or limit == None or page == "":
      self.response.out.write("Error")
      return
      
    try:
      page = int(page)
      limit = int(limit)
    except:
      self.response.out.write("Error, args must be ints. kthxbye!")
      return
      
    current_session = Session().get_current_session(self)
    
    asc = "ASC"
    if order_by == "points":
      asc = "DESC"
    
    offset = page*limit
    from serverside.dao import users_dao
    users = users_dao.get_users_by_page_by_order(current_session.get_account_entity(), offset, limit, order_by, asc)
    
    ret_json = "{ \"users\" : ["
    first = True
    for user in users:
      if not first:
        ret_json += ","
      first = False
      ret_json += "{"
      ret_json += "\"userid\" : \"" + user.userid + "\","
      ret_json += "\"points\" : \"" + str(user.points) + "\","
      ret_json += "\"rank\" : \"" + str(user.rank) + "\""
      ret_json += "}"
    ret_json+= "]}"
    
    self.response.out.write(ret_json)
    
  
class ConsoleFeatures(webapp.RequestHandler):
  @account_login_required
  def get(self):
    current_session = Session().get_current_session(self)
    email = current_session.get_email()
    
    """ Get widgets values """
    trophy_case_values = widgets_dao.get_trophy_case_properties_to_render(email)
    rank_values = widgets_dao.get_rank_properties_to_render(email)
    points_values = widgets_dao.get_points_properties_to_render(email)
    leaderboard_values = widgets_dao.get_leaderboard_properties_to_render(email)
    notifier_values = widgets_dao.get_notifier_properties_to_render(email)
    
    """ Preview urls """
    trophy_case_preview_url = ""
    rank_preview_url = ""
    points_preview_url = ""
    
    template_values = {'features_main' : True,
                       'account_name' : current_session.get_email(),
                       'trophy_case_values' : trophy_case_values,
                       'rank_values':rank_values,
                       'points_values':points_values,
                       'notifier_values': notifier_values,
                       'leaderboard_values':leaderboard_values,
                       'trophy_case_preview_url':trophy_case_preview_url,
                       'rank_preview_url':rank_preview_url,
                       'points_preview_url':points_preview_url}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))  

class ConsoleFeaturesUpdate(webapp.RequestHandler):
  @account_login_required
  def post(self):
    """ Ajax call handler to save trophycase features """
    current_session = Session().get_current_session(self)
    
    property = self.request.get("property")
    new_value = self.request.get("propertyValue")
    entity_type = self.request.get("entityType")
    success = widgets_dao.update_widget_property(current_session.get_email(), entity_type, property, new_value)
    
    if success:
      self.response.out.write("Success")
    else:
      self.response.out.write("Failed")

class ConsoleFeaturesPreview(webapp.RequestHandler):
  @account_login_required
  def get(self):
    """ Ask for which widget, and then render that widget """
    widget = self.request.get("widget")
    current_session = Session().get_current_session(self)
    account = current_session.get_account_entity()
    
    widget_ref = account.trophyWidget
    render_path = constants.TEMPLATE_PATHS.RENDER_TROPHY_CASE
    if widget == "rank":
      widget_ref = account.rankWidget
      render_path = constants.TEMPLATE_PATHS.RENDER_RANK
    elif widget == "points":
      widget_ref = account.pointsWidget
      render_path = constants.TEMPLATE_PATHS.RENDER_POINTS
    elif widget == "leaderboard":
      widget_ref = account.leaderWidget
      render_path = constants.TEMPLATE_PATHS.RENDER_LEADERBOARD
    elif widget == "notifier":
      widget_ref = account.notifierWidget
      render_path = constants.TEMPLATE_PATHS.RENDER_NOTIFIER  
      
    values = {"status":"success"}
    properties = widget_ref.properties()
    for property in properties:
      values[property] = getattr(widget_ref, property)
    
    self.response.out.write(template.render(render_path, values))

class ConsoleFeaturesGetValue(webapp.RequestHandler):
  @account_login_required
  def get(self):
    """ Look up value of "of" """
    current_session = Session().get_current_session(self)
    requested_value = self.request.get("of")
    entity_type = self.request.get("entityType")
    value = widgets_dao.get_single_widget_value(current_session.get_email(), entity_type, requested_value)
    self.response.out.write(value)
    

class ConsoleAnalytics(webapp.RequestHandler):
  @account_login_required
  def get(self):
    current_session = Session().get_current_session(self)
    template_values = {'analytics_main' : True,
                       'account_name' : current_session.get_email()}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))

class ConsoleDownloads(webapp.RequestHandler):
  @account_login_required
  def get(self):
    current_session = Session().get_current_session(self)
    template_values = {'downloads_main' : True,
                       'account_name' : current_session.get_email()}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))
    
class ConsolePreferences(webapp.RequestHandler):
  @account_login_required
  def get(self):
    """ handler for change password template """
    current_session = Session().get_current_session(self)
    template_values = {'preferences_main' : True,
                       'account_name' : current_session.get_email()}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))
    
  @account_login_required
  def post(self):
    """ will handle change of password request, will return success/fail """
    current_session = Session().get_current_session(self)
    email = current_session.get_email()
    
    old_password = self.request.get("oldpassword")
    new_password = self.request.get("newpassword")
    new_password_again = self.request.get("newpasswordagain")
    
    error_message = ""
    success = False
    if new_password != new_password_again:
      error_message = "Passwords do not match."
    else:
      """ Make sure that the account authenticates... this is a redundant check """
      if accounts_dao.authenticate_web_account(email, old_password):
        changed = accounts_dao.change_account_password(email, new_password)
        if changed:
          success = True
      else:
        error_message = "Old password incorrect."
  
    template_values = {"preferences_main" : True,
                       "password_change_attempted" : True,
                       'account_name' : email,
                       "error_message": error_message,
                       "password_changed" : success}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_DASHBOARD, template_values))

class ConsoleForgottenPassword(webapp.RequestHandler):
  def get(self):
    """ handle forgotten password request """
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_FORGOTTEN_PASSWORD, None))

  def post(self):
    """ email posted, send a temporary password there """
    email = self.request.get("email")
    new_password = accounts_dao.reset_password(email)
    
    success = False
    logging.info("Reset email to: " + email + " temp password: " + new_password)
    if new_password:
      """ send an email with new password """
      try:
        mail.send_mail(sender="UserInfuser <raj@cloudcaptive.com>",
                         to=email,
                         subject="UserInfuser Password Reset",
                         body= messages.get_forgotten_login_email(new_password))
        success = True
      except:
        logging.error("FAILED to send password reset email to: " + email)
        pass
    
    values = {"success" : success,
              "response" : True}
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_FORGOTTEN_PASSWORD, values))
    
class ConsoleSignUp(webapp.RequestHandler):
  def get(self):
    self.response.out.write(template.render(constants.TEMPLATE_PATHS.CONSOLE_SIGN_UP, None))
    
    
      
class ReturnUserCount(webapp.RequestHandler):
  def get(self):
    # TODO
    self.response.out.write("800")

application = webapp.WSGIApplication([
  ('/adminconsole', Console),
  ('/adminconsole/users', ConsoleUsers),
  ('/adminconsole/users/edit', ConsoleEditUser),
  ('/adminconsole/users/count', ReturnUserCount),
  ('/adminconsole/users/fetch', ConsoleUsersFetch),
  ('/adminconsole/downloads', ConsoleDownloads),
  ('/adminconsole/features', ConsoleFeatures),
  ('/adminconsole/features/update', ConsoleFeaturesUpdate),
  ('/adminconsole/features/preview', ConsoleFeaturesPreview),
  ('/adminconsole/features/getvalue', ConsoleFeaturesGetValue),
  ('/adminconsole/badges', ConsoleBadges),
  ('/adminconsole/preferences', ConsolePreferences),
  ('/adminconsole/forgot', ConsoleForgottenPassword),
  ('/adminconsole/signup', ConsoleSignUp),
  ('/adminconsole/analytics', ConsoleAnalytics)
], debug=constants.DEBUG)


def main():
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
