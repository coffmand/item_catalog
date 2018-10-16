#!/usr/bin/env python
# =================================================================
# Python program: application.py
# - Main Python Program entry point for
#   Flask/SQLAlchemy Web Server Application for Udacity FSND
#   Project No. 4. 'item_catalog'
# =================================================================

from flask import Flask, render_template, request, redirect, \
     jsonify, url_for, flash

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

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


# ###########################
# ###########################
# ####    M  A  I  N    #####
# ###########################
# ###########################
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
