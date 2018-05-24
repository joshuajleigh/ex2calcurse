#!/usr/bin/python3

import requests
import datetime
import exchangelib
import hashlib
import os
import json

REPORT=""
VALUES={
    "username": os.environ['username'],
    "password": os.environ['password'],
    "owa": os.environ['owa'],
    "before": os.environ['before'],
    "future": os.environ['future'],
    "directory": os.environ['directory']}

def getEvents(VALUES):
    """get events from exchange and write them to file"""
    url = VALUES['owa']
    username = VALUES['username']
    password = VALUES['password']
    BEFORE = int(VALUES['before'])
    FUTURE = int(VALUES['future'])

    try:
        credentials = exchangelib.Credentials(username=username, password=password)
        config = exchangelib.Configuration(server=url, credentials=credentials)
        account = exchangelib.Account(primary_smtp_address=username, credentials=credentials, config=config)
        total_number = str(account.calendar.total_count)
        tz = exchangelib.EWSTimeZone.localzone()
        right_now = tz.localize(exchangelib.EWSDateTime.now())

        start = right_now - datetime.timedelta(days=BEFORE)
        end = right_now + datetime.timedelta(days=FUTURE)

        allEvents = account.calendar.view(start=start, end=end)

        return allEvents
    except Exception as inst:
        print(inst)
        quit()

def convertList(allEvents):
    """converts times from universal to local time"""
    tz = exchangelib.EWSTimeZone.localzone()
    full_notes = {}
    h = hashlib.sha1()
    db_list = []
    event_number = 0
    for item in allEvents:
        NOTES=str(item.text_body).encode('utf-8')
        h.update(NOTES)
        NOTEHASH=h.hexdigest()
        full_notes[h.hexdigest()]=NOTES.decode("utf-8")
        db_list.insert(event_number, {
            'uid': str(item.uid),
            'info': {
                'start': str(item.start),
                'end': str(item.end),
                'subject': str(item.subject),
                'location': str(item.location),
                'notes': NOTEHASH,
                'last_modified': str(item.last_modified_time),
                'text_body': str(item.text_body) }
            })
        event_number += 1
#    print(full_calendar)
    return full_notes, db_list

def ensuredir(directory):
    try:
        os.stat(directory)
    except:
        os.mkdir(directory)

def main():
    """ pull calendar data, write to db"""
    allEvents=getEvents(VALUES)
    new_notes, db_events=convertList(allEvents)
    print(REPORT + "exchange -> db file replication " + str(datetime.datetime.now()))
    APTFILE=VALUES['directory'] + ".calcurse/apts"
    NOTESDIR=VALUES['directory'] + ".calcurse/notes/"
    DBFILE=VALUES['directory'] + ".calcurse/db_file"
    ensuredir(VALUES['directory'])
    ensuredir(NOTESDIR)

    with open(DBFILE, 'w') as f:
            json.dump(db_events, f, indent=2)


main()
