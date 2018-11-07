#!/usr/bin/env python
# =================================================================
# Python program: application.py
# - Main Python Program entry point for
#   Flask/SQLAlchemy Web Server Application for Udacity FSND
#   Project No. 4. 'item_catalog'
# =================================================================

from flask import Flask, render_template, request, redirect, \
     jsonify, url_for, flash, abort, g

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, relationship, exc
from db_models import Base, User, Category, Item
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
from flask_httpauth import HTTPBasicAuth
import sys

auth = HTTPBasicAuth()


app = Flask(__name__)


# ###################################################################
# Connect to Database and create database session
# - incorp param to disable 'check_same_thread' default functionality
#   - This is to avoid the SQLAlchemy programmingError Thread Error
#     encountered (intermittent failures ...)
# ###################################################################
engine = create_engine('sqlite:///itemcatalog.db',
                       connect_args={'check_same_thread': False},
                       echo=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# For Google login: load client_id from Google-supplied JSON data file
# - Trap case where file does not exist
try:
    CLIENT_ID = json.loads(
        open('client_secrets.json', 'r').read())['web']['client_id']
except IOError as reason:
        print "Program Error Exit: ", reason
        # Close DB before exiting
        session.close()
        print "Database closed."
        sys.exit(1)
# ###################################################
# Caution: Application Name must match the registered
#          Google OAuth Client ID Name shown under
#          the 'Credentials' section
# ###################################################
APPLICATION_NAME = "Item Catalog Application"


# =======================================
# ======== E N D P O I N T S ============
# =======================================

# Include creation of anti-forgery state token
@app.route('/login')
def showLogin():
    # return "Endpoint: /login"  # Endpoint Stub verification
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state

    # Render the Login Template
    return render_template('login.html', STATE=state)


# Facebook Login connect
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # return "Endpoint: /fbconnect"  # Endpoint Stub verification
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "Access Token received %s " % access_token

    # Load Facebook-supplied data
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']

    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (  # NOQA
        app_id, app_secret, access_token)  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "result=%s" % result

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting of the result from the server token exchange we
        have to split the token first on commas and select the first index
        which gives us the key : value for the server access token then we
        split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used
        directly in the graph api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')
    # print "token=%s" % token

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    print(login_session)

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # Determine if user exists - if not Create New User
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
                  -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


# Facebook Login disconnect
@app.route('/fbdisconnect')
def fbdisconnect():
    # return "Endpoint: /fbdisconnect"  # Endpoint Stub verification
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)  # NOQA
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "You have been successfully logged out."


# Google Login connect
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # return "Endpoint: /gconnect"  # Endpoint Stub verification

    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    response = h.request(url, 'GET')[1]
    str_response = response.decode('utf-8')
    result = json.loads(str_response)

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's User ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's Client ID does not match app's."), 401)
        print "Token's Client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
          'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print(data)

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # If User exists, use Info
    # - Else create new User
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px; \
                -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print "Done!"
    return output


# Google Login disconnect
@app.route('/gdisconnect')
def gdisconnect():
    # return "Endpoint: /gdisconnect"  # Endpoint Stub verification
    access_token = login_session.get('access_token')
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' \
          % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['provider']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
          'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    # return "Endpoint: /disconnect"  # Endpoint Stub verification
    print "login_session: %s" % login_session
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            # del login_session['gplus_id']
            # del login_session['access_token']
        elif login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            del login_session['provider']
            del login_session['access_token']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCategories'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCategories'))


# Show all Categories - ##### Main Entry Endpoint #####
@app.route('/')
@app.route('/categories/')
def showCategories():
    # return "Endpoint: /categories"  # Endpoint Stub verification
    categories = session.query(Category).order_by(asc(Category.name))
    if categories.count() == 0:
        flash("No Categories Found. Please add a New Category.\n")
        flash("(Login Required)\n")
    return render_template('showcategories.html', categories=categories)


# Create a new Category
@app.route('/categories/new/', methods=['GET', 'POST'])
def newCategory():
    # return "Endpoint: /categories/new"  # Endpoint Stub verification

    # #################################################################
    # Although a Non-Loggedin User should not be able to
    # access this function through the web interface, this is a
    # safeguard to block execution that uses an Endpoint URL
    # #################################################################
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        new_category = Category(
            name=request.form['name'],
            user_id=login_session['user_id'])
        session.add(new_category)
        session.commit()
        flash("New Category: '%s' Successfully Created" % new_category.name)
        return redirect(url_for('showCategories'))
    else:
        return render_template('newcategory.html')


# Edit a Category
@app.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    # return "Endpoint: /categories/%s/edit" % category_id  # Endpoint
    #         Stub verification
    edited_category = session.query(Category).filter_by(
      id=category_id).one()

    # #################################################################
    # Although a Non-Owner or Non-Loggedin User should not be able to
    # access this function through the web interface, this is a
    # safeguard to block execution that uses an Endpoint URL
    # #################################################################
    if 'username' not in login_session:
        return redirect('/login')
    if edited_category.user_id != login_session['user_id']:
        return "<script>function myFunction() \
          {alert('You are not authorized to edit this Category. \
          Please create your own Category in order to edit.');} \
          </script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            edited_category.name = request.form['name']
        session.add(edited_category)
        session.commit()
        flash("Category: '%s' Successfully Edited" % edited_category.name)
        return redirect(url_for('showCategories'))
    else:
        return render_template('editcategory.html',
                               category=edited_category,
                               category_id=category_id)


# Delete a Category
@app.route('/categories/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    # return "Endpoint: /categories/%s/delete" % category_id
    #         Endpoint Stub verification
    category_to_delete = session.query(Category).filter_by(
      id=category_id).one()

    # #################################################################
    # Although a Non-Owner or Non-Loggedin User should not be able to
    # access this function through the web interface, this is a
    # safeguard to block execution that uses an Endpoint URL
    # #################################################################
    if 'username' not in login_session:
        return redirect('/login')
    if category_to_delete.user_id != login_session['user_id']:
        return "<script>function myFunction() \
          {alert('You are not authorized to delete this Category. \
          Please create your own Category in order to delete.');} \
          </script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(category_to_delete)
        session.commit()
        flash("Category: '%s' Successfully Deleted" % category_to_delete.name)
        return redirect(url_for('showCategories'))
    else:
        return render_template('deleteCategory.html',
                               category=category_to_delete,
                               category_id=category_id)


# Show Items for a Category
@app.route('/categories/<int:category_id>')
@app.route('/categories/<int:category_id>/items')
def showItems(category_id):
    # return "Endpoint: /categories/%s/items" % category_id  # Endpoint Stub
    #     verification
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(
        category_id=category_id).order_by(asc(Item.name))
    if items.count() == 0:
        flash("No Items Found. Please add a New Item.\n")
        flash("(Login and Category Ownership Required)\n")
    return render_template('showitems.html',
                           category_id=category_id,
                           category=category,
                           items=items)


# Create a new Item
@app.route('/categories/<int:category_id>/items/new',
           methods=['GET', 'POST'])
def newItem(category_id):
    # return "Endpoint: /categories/%s/items/new" % category_id
    #         Endpoint Stub verification
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()

    # #################################################################
    # Although a Non-Owner or Non-Loggedin User should not be able to
    # access this function through the web interface, this is a
    # safeguard to block execution that uses an Endpoint URL
    # #################################################################
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() \
        {alert('You are not authorized to add Items to this Category. \
        Please create your own Category in order to add items.');} \
        </script><body onload='myFunction()''>"
    if request.method == 'POST':
        new_item = Item(name=request.form['name'],
                        description=request.form['description'],
                        picture=request.form['picture'],
                        category_id=category_id,
                        user_id=login_session['user_id'])
        session.add(new_item)
        session.commit()
        flash("New Item: '%s' Successfully Created" % (new_item.name))
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('newitem.html',
                               category_id=category_id,
                               category=category)


# Show an Item
@app.route('/categories/<int:category_id>/items/<int:item_id>',
           methods=['GET'])
def showItem(category_id, item_id):
    # return "Endpoint: /categories/%s/items/%s" % (category_id, item_id)
    category = session.query(Category).filter_by(id=category_id).one()
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('showitem.html',
                           category_id=category_id,
                           category=category,
                           item_id=item_id,
                           item=item)


# Edit an Item
@app.route('/categories/<int:category_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    # return "Endpoint: /categories/%s/items/%s/edit" % (category_id, item_id)
    #         Endpoint Stub verification

    # #################################################################
    # Although a Non-Owner or Non-Loggedin User should not be able to
    # access this function through the web interface, this is a
    # safeguard to block execution that uses an Endpoint URL
    # #################################################################
    if 'username' not in login_session:
        return redirect('/login')
    edited_item = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if login_session['user_id'] != category.user_id:
        return "<script>function myFunction() \
        {alert('You are not authorized to edit Items for this Category.\
        Please create your own Category in order to edit Items.');} \
        </script><body onload='myFunction()''>"
    if request.method == 'POST':
        if request.form['name']:
            edited_item.name = request.form['name']
        if request.form['description']:
            edited_item.description = request.form['description']
        if request.form['picture']:
            edited_item.picture = request.form['picture']
        if request.form['cat_id_sel']:
            new_category = session.query(Category).filter_by(
                id=request.form['cat_id_sel']).one()
            edited_item.category_id = request.form['cat_id_sel']
            edited_item.category = new_category
        session.add(edited_item)
        session.commit()
        flash("Item: '%s' Successfully Edited" % edited_item.name)
        if edited_item.category_id == category_id:
            # Category ref in Item has NOT Changed
            return redirect(url_for('showItem',
                                    category_id=category_id,
                                    category=category,
                                    item_id=item_id,
                                    item=edited_item))
        else:
            # Category ref in Item HAS Changed
            return redirect(url_for('showItem',
                                    category_id=request.form['cat_id_sel'],
                                    category=new_category,
                                    item_id=item_id,
                                    item=edited_item))
    else:
        category_list = session.query(Category).filter_by(
            user_id=login_session['user_id']).order_by(asc(Category.id))
        return render_template('edititem.html',
                               category_id=category_id,
                               category=category,
                               item_id=item_id,
                               item=edited_item,
                               category_list=category_list)


# Delete an Item
@app.route('/categories/<int:category_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    # return "Endpoint: /categories/%s/items/%s/delete" %
    # (category_id, item_id)  # Endpoint Stub verification

    # #################################################################
    # Although a Non-Owner or Non-Loggedin User should not be able to
    # access this function through the web interface, this is a
    # safeguard to block execution that uses an Endpoint URL
    # #################################################################
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(id=category_id).one()
    item_to_delete = session.query(Item).filter_by(id=item_id).one()
    if login_session['user_id'] != item_to_delete.user_id:
        return "<script>function myFunction() \
        {alert('You are not authorized to delete Items from this \
        Category. Please create your own Category in order to delete \
        items.');}</script><body onload='myFunction()''>"
    if request.method == 'POST':
        session.delete(item_to_delete)
        session.commit()
        flash("Item: '%s'' Successfully Deleted" % item_to_delete.name)
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('deleteitem.html',
                               category_id=category_id,
                               category=category,
                               item_id=item_id,
                               item=item_to_delete)


# ######################
# User Helper Functions
# ###################### ######################################################
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except exc.NoResultFound:
        return None


# ######################
# ###### A P I s  ######
# ###################### ######################################################

# JSON API to view All Catalog Categories
@app.route('/api/v1/categories/JSON')
def allCategoriesJSON():
    # return "API JSON Endpoint: /api/v1/categories/JSON"
    # Endpoint Stub verification
    categories = session.query(Category).order_by(asc(Category.name))
    if categories.count() != 0:
        return jsonify(Categories=[c.serialize for c in categories])
    else:
        response = make_response(json.dumps('No Category Records found.'), 404)
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON API to view selected Category Information
@app.route('/api/v1/categories/<int:category_id>/JSON')
def categoryJSON(category_id):
    # return "API JSON Endpoint: /api/v1/categories/%s/JSON" \
    #         % category_id
    # Endpoint Stub verification
    try:
        category = session.query(Category).filter_by(id=category_id).one()
        return jsonify(Category=category.serialize)
    except exc.NoResultFound:
        response = make_response(json.dumps(
            "No Category Record found with id Field = %s" % category_id), 404)
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON API to view Items for a Category
@app.route('/api/v1/categories/<int:category_id>/items/JSON')
def itemsByCategoryJSON(category_id):
    # return "API JSON Endpoint: /api/v1/categories/%s/items/JSON" \
    #         % category_id  # Endpoint Stub verification
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except exc.NoResultFound:
        return "No Category Record found with id Field = %s" \
            % category_id
    items = session.query(Item).filter_by(
        category_id=category_id).order_by(asc(Item.name))
    if items.count() != 0:
        return jsonify(Items=[i.serialize for i in items])
    else:
        response = make_response(json.dumps(
            "No Item Records found with category_id Field = %s"
            % category_id), 404)
        response.headers['Content-Type'] = 'application/json'
        return response


# ===========================================
# JSON API to view selected Item Information
# ===========================================
# - Generate a descriptive error_str to help User understand
#   which part of API URL is causing the problem (ie:
#   a valid Category ID and a valid Item ID are necessarily valid when
#   combined ...)
# ======================================================================
@app.route('/api/v1/categories/<int:category_id>/items/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    # return "API JSON Endpoint: /api/v1/categories/%s/items/%s/JSON" \
    #        % (category_id, item_id)   # Endpoint Stub verification
    error_str = ""
    try:
        category = session.query(Category).filter_by(id=category_id).one()
    except exc.NoResultFound:
        error_str += "No Category Record found with id Field = %s, " \
            % category_id
    try:
        item_pre = session.query(Item).filter_by(
            id=item_id).one()
    except exc.NoResultFound:
            error_str += "No Item Record found with id Field = %s, " \
                % item_id
    try:
        item = session.query(Item).filter_by(
            id=item_id, category_id=category_id).one()
        return jsonify(Item=item.serialize)
    except exc.NoResultFound:
        error_str += "No Item Record found with category_id Field" \
            " = %s and item_id Field = %s" \
            % (category_id, item_id)
        response = make_response(json.dumps(error_str), 404)
        response.headers['Content-Type'] = 'application/json'
        return response


# ###################### ######################################################


# ###########################
# ###########################
# ####    M  A  I  N    #####
# ###########################
# ###########################
if __name__ == '__main__':
    # Use for flash messaging
    flash_secret_key = ''.join(random.choice(
                               string.ascii_uppercase + string.digits)
                               for x in xrange(32))
    app.secret_key = flash_secret_key
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

    # Close DB
    session.close()
    print "Database closed."
