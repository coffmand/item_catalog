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
from sqlalchemy.orm import sessionmaker, relationship
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

auth = HTTPBasicAuth()


app = Flask(__name__)


# ###################################################################
# Connect to Database and create database session
# - incorp param to disable 'check_same_thread' default functionality
#   - This is to avoid the SQLAlchemy programmingError Thread Error
#     encountered (intermittent failures ...)
# ###################################################################
engine = create_engine('sqlite:///sqlite:///itemcatalog.db',
                       connect_args={'check_same_thread': False},
                       echo=True)
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# =======================================
# ======== E N D P O I N T S ============
# =======================================

# User verification
@auth.verify_password
def verify_password(username_or_token, password):
    # Try to see if it's a token first
    user_id = User.verify_auth_token(username_or_token)
    if user_id:
        user = session.query(User).filter_by(id=user_id).one()
    else:
        user = session.query(User).filter_by(
            username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


# Token generation
@app.route('/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    return "Endpoint: /login"


# Facebook Login connect
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    return "Endpoint: /fbconnect"


# Facebook Login disconnect
@app.route('/fbdisconnect')
def fbdisconnect():
    return "Endpoint: /fbdisconnect"


# Google Login connect
@app.route('/gconnect', methods=['POST'])
def gconnect():
    return "Endpoint: /gconnect"


# Google Login disconnect
@app.route('/gdisconnect')
def gdisconnect():
    return "Endpoint: /gdisconnect"


# Show all Categories
@app.route('/')
@app.route('/categories/')
def showCategories():
    return "Endpoint: /categories"


# Create a new Category
@app.route('/categories/new/', methods=['GET', 'POST'])
def newRestaurant():
    return "Endpoint: /categories/new"


# Edit a Category
@app.route('/categories/<int:category_id>/edit', methods=['GET', 'POST'])
def editCategory(category_id):
    return "Endpoint: /categories/%s/edit" % category_id


# Delete a Category
@app.route('/categories/<int:category_id>/delete', methods=['GET', 'POST'])
def deleteCategory(category_id):
    return "Endpoint: /categories/%s/delete" % category_id


# Show Items for a Category
@app.route('/categories/<int:category_id>')
@app.route('/categories/<int:category_id>/items')
def showItems(category_id):
    return "Endpoint: /categories/%s/items" % category_id


# Create a new Item
@app.route('/categories/<int:category_id>/items/new',
           methods=['GET', 'POST'])
def newItem(category_id):
    return "Endpoint: /categories/%s/items/new" % category_id


# Edit an Item
@app.route('/categories/<int:category_id>/items/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    return "Endpoint: /categories/%s/items/%s/edit" % (category_id, item_id)


# Delete an Item
@app.route('/categories/<int:category_id>/items/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    return "Endpoint: /categories/%s/items/%s/delete" % (category_id, item_id)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    return "Endpoint: /disconnect"


# ######################
# ###### A P I s  ######
# ###################### ######################################################

# JSON API to view All Catalog Categories
@app.route('/api/v1/categories/JSON')
def allCategoriesJSON():
    return "API JSON Endpoint: /api/v1/categories/JSON"


# JSON API to view selected Category Information
@app.route('/api/v1/categories/<int:category_id>/JSON')
def categoryJSON(category_id):
    return "API JSON Endpoint: /api/v1/categories/%s/JSON" \
            % category_id


# JSON API to view Items for a Category
@app.route('/api/v1/categories/<int:category_id>/items/JSON')
def itemsByCategoryJSON(category_id):
    return "API JSON Endpoint: /api/v1/categories/%s/items/JSON" \
            % category_id


# JSON API to view selected Item Information
@app.route('/api/v1/categories/<int:category_id>/items/<int:item_id>/JSON')
def itemJSON(category_id, item_id):
    return "API JSON Endpoint: /api/v1/categories/%s/items/%s/JSON" \
            % (category_id, item_id)

# ###################### ######################################################


# ###########################
# ###########################
# ####    M  A  I  N    #####
# ###########################
# ###########################
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)

    # Close DB
    session.close()
    print "Database closed."
