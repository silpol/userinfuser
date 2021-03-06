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
from django.utils import simplejson
from serverside.dao import badges_dao
from entities.accounts import Accounts
from entities.badges import *
from entities.users import *
from google.appengine.ext import db, webapp
from google.appengine.ext.webapp import template
from serverside import constants
from serverside.constants import TEMPLATE_PATHS
from serverside.session import Session
from tools.utils import account_login_required
from tools.xss import XssCleaner, XssCleaner
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore
import google.appengine.api.images
import cgi
import logging
import os
import wsgiref.handlers
import string
json = simplejson

def is_valid_image(filename, filecontents):
  return True 

def get_file_ext(filename):
  ii = filename.rfind(".")
  if ii == -1:
    # assume its png
    return "png"
  else:
    return filename[ii + 1:] 

class UploadBadge(blobstore_handlers.BlobstoreUploadHandler):
  def redirect_error(reason):
    # redirect to badge download for viewing
    values = {"badge_upload_success": False,
              "fail_reason": reason}

    self.response.out.write(template.render(TEMPLATE_PATHS.CONSOLE_DASHBOARD, values))
    return

  @account_login_required
  def post(self):
    #TODO
    # IN the future we should try to move this logic to data access utility layer
    # and have the handler portion be in console.py
    current_session = Session().get_current_session(self)
    account = current_session.get_account_entity()
    if not account:
      self.response.out.write("Problem with your account. Please email support.")
      return  

    #TODO make sure badge name is not taken, or warn if overwritting
    badge_name = self.request.get("badgename")
    badge_name = string.replace(badge_name, " ", "_")
    badge_name = string.replace(badge_name, "-", "_")

    badge_theme = self.request.get("badgetheme")
    badge_theme= string.replace(badge_theme, "-", "_")
    badge_theme = string.replace(badge_theme, " ", "_")

    badge_des = self.request.get("badgedescription")

    upload_files = self.get_uploads('file')
    blob_info = upload_files[0]

    badge_file_name = blob_info.filename
    badge_ext = get_file_ext(badge_file_name)     
    if badge_ext not in constants.IMAGE_PARAMS.VALID_EXT_TYPES:
      self.redirect_error("Image must be png, jpeg, or gif")
      return 
      
    logging.info("File ext:"+badge_ext)
    if not badge_name:
      self.redirect_error("No name given")
      return 
    if not badge_des:
      self.redirect_error("No description given")
      return 
    if not badge_theme: 
      self.redirect_error("No theme given")
      return 
    if not blob_info:
      self.redirect_error("No file given")
      return 
    if blob_info.size > constants.MAX_BADGE_SIZE:
      self.redirect_error("File is too large. Must be smaller than " + str(constants.MAX_BADGE_SIZE) + " bytes")
      return 
    perm = "private"
    if account.email == constants.ADMIN_ACCOUNT:
      perm = "public" 

    badge_key = badges_dao.create_badge_key(account.email, badge_theme, badge_name, perm)

    badge = badges_dao.create_badge_type(badge_key,
                      badge_name,
                      badge_des,
                      account,
                      badge_theme,
                      badge_ext,
                      blob_info=blob_info)
    self.redirect('/adminconsole/badges')
    return
    # redirect to badge download for viewing
    values = {"badge_upload_success": True,
              "account_name": account.email,
              "badgekey": badge_key,
              "badgeLink": badge.downloadLink,
              "badgedescription": badge_des,
              "badgealt": badge_des,
              "badgename": badge_name,
              "badgeperm": perm}

    self.response.out.write(template.render(TEMPLATE_PATHS.CONSOLE_DASHBOARD, values))

  def get(self):
    self.redirect('/adminconsole/badges')

class DownloadBadge(webapp.RequestHandler):
  def get(self):
    badge_id = self.request.get("bk")
    if not badge_id:
      self.redirect('/images/default.jpg')
      return 
    badge = badges_dao.get_badge_image(badge_id)
    if not badge:
      logging.error("Download badge: %s key not found"%badge_id) 
      self.redirect('/images/default.jpg')
      return 
    self.response.headers['Content-Type'] = "image/" + str(badge.imgType)
    self.response.out.write(badge.image)

class SeeTheme(webapp.RequestHandler):
  @account_login_required
  def get(self):
    clean = XssCleaner()
    badge_theme = self.request.get("theme")
    clean_badge_theme = clean.strip(badgeTheme)
    if badge_theme != clean_badge_theme:
      logging.info("Cleaning: %s to %s"%(badge_theme, clean_badge_theme))
    badges = db.GqlQuery("SELECT * FROM Badges where theme=:1", 
                         clean_badge_theme)
    badgeset = []
    for b in badges:
      item = {"name": b.name, 
       "description": b.description, 
       "alt":b.altText, 
       "key":b.key().name(),
       "perm":b.permissions }
      badgeset.append(item)

    values = {"badgetheme":clean_badge_theme,
              "badges": badgeset}
    path = os.path.join(os.path.dirname(__file__), 'templates/badgetheme.html')
    # TODO fix this for when you hit refresh, dont go 404 on them
    self.response.out.write(template.render(path, values))
             
