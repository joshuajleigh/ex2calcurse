#!/usr/bin/env python

import argparse
import configparser
import requests
import datetime
import exchangelib
import hashlib
import os
import subprocess
import json

WORKING_DIR=(os.path.abspath(os.path.dirname(__file__)))

REPORT=""
VALUES={
    "username": False,
    "password": False,
    "owa": False,
    "interval": False,
    "before": False,
    "future":False,
    "warning": False,
    "directory": False}

def args():
    """Get arguments from command line."""
    p = argparse.ArgumentParser(description="Exchange to Remind script")
    p.add_argument("--config", "-c", help="path to config file")
    p.add_argument("--future", "-f", help="how many days in the future to pull", type=int, default=30)
    p.add_argument("--before", "-b", help="how many days in the past to pull", type=int, default=15)
    p.add_argument("--interval", "-i", help="time in minutes between notifications", default=3)
    p.add_argument("--warning", "-a", help="time in minutes, how far warning to start warning", default=15)
    p.add_argument("--owa", "-o", type=str, help="exchange owa address")
    p.add_argument("--username", "-u", type=str, help="exchange usename in form of <domain>\\\<username>")
    p.add_argument("--password", "-p", type=str, help="exchange password")
    p.add_argument("--directory", "-d", help="directory for calcurse folders", default="~/.calcurse")
    return p.parse_args()

def read_config_file(conf):
    """Load config from config file."""
    try:
        c = configparser.RawConfigParser()
        c.read(conf)
        return c
    except:
        print("did not read a config file, is {} a file?".format(conf))
        return "filler"

def validate_args(arg, REPORT):
    """verify input(s) from config file and command line flags"""
    conf=read_config_file(arg.config)
    for i in VALUES:
        try:
            VALUES[i]=conf.get('ex2calcurse', i)
        except:
            continue

    for key, value in VALUES.items():
        if not value:
           try:
               VALUES[key]=eval('arg.{}'.format(key))
           except:
               print("something went wrong with input!")
               exit()

    if not VALUES['username']:
        REPORT+="please provide username in flag, -u whatever\n"
        REPORT+="or config file, username=whatever\n"
    if not VALUES['password']:
        REPORT+="please provide password in flag, -p password\n"
        REPORT+="or config file, password=whatever\n"
    if not VALUES['owa']:
        REPORT+="please provide owa url in flag, -o whatever\n"
        REPORT+="or config file, owa=whatever\n"
    if not VALUES['username'] or not VALUES['password'] or not VALUES['owa']:
        print(REPORT)
        exit()
    return VALUES

def validateURL(URL):
    """verify the URL provided is (close) to a valid owa url"""
    endpoint = "http://" + URL
    try:
        request = requests.get(endpoint)
        if request.status_code == 200:
            print('url is a valid site, but not exchange link')
            quit()
        if request.reason == 'Unauthorized':
            global REPORT
            REPORT+="url valid - "
            return REPORT
    except(requests.exceptions.ConnectionError):
        print('Website {} not resolving'.format(URL))
        quit()
    except(requests.exceptions.MissingSchema):
        print('Invalid URL \'{}\': No schema supplied. Perhaps you meant https://{}?'.format(URL,URL))
        quit()

def ex2db(username, password, owa, before, future, directory):
    ENV={
        'username': username,
        'password': password,
        'owa': owa,
        'before': before,
        'future': future,
        'directory': directory
        }
    PYTHON=str(WORKING_DIR + "/env/bin/python")
    EX2DB=str(WORKING_DIR + "/ex2db.py")
#    print("subprocess.call([{PYTHON}, {EX2DB}], env={ENV})".format(PYTHON=PYTHON, EX2DB=EX2DB, ENV=ENV))
    subprocess.call([PYTHON, EX2DB], env=ENV)

def db2cal(DBFILE, NOTESDIR):
    ENV={
        'DBFILE': DBFILE,
        'NOTESDIR': NOTESDIR
        }
    PYTHON=str(WORKING_DIR + "/env/bin/python")
    DB2CAL=str(WORKING_DIR + "/db2cal.py")
#    print("subprocess.call([{PYTHON}, {DB2CAL}])".format(PYTHON=PYTHON, DB2CAL=DB2CAL))
    subprocess.call([PYTHON, DB2CAL], env=ENV)

def main():
    """ get args, confirm them, pull calendar data, write to a file"""
    ARGS=args()
    VALUES=validate_args(ARGS, REPORT)
    validateURL(VALUES['owa'])
    ex2db(
        str(VALUES['username']),
        str(VALUES['password']),
        str(VALUES['owa']),
        str(VALUES['before']),
        str(VALUES['future']),
        str(VALUES['directory']))
    db2cal(
        str(VALUES['directory'] + ".calcurse/db_file"),
        str(VALUES['directory'] + ".calcurse/notes")
        )

main()
