#!/usr/bin/env python3

import json
import datetime
import pytz
import hashlib
import os


def load_db(DBFILE):
#    DBFILE=DIR + ".calcurse/db_file"
    with open(DBFILE) as f:
       DB_JSON_DATA=json.load(f)
    return DB_JSON_DATA

def string_to_timeobject(time_string):
    tz_unaware_time = datetime.datetime.strptime(time_string[0:19], '%Y-%m-%d %H:%M:%S')
    time=tz_unaware_time.replace(tzinfo=pytz.utc)
    return time

def localize_time(time_obj):
    local_tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
    local_time=time_obj.astimezone(tz=local_tz)
    return local_time

def get_time_of_day(time_obj):
    hour=str(time_obj.hour)
    minute=str(time_obj.isoformat()[14:16])
    time_string=hour + ":" + minute
    return time_string

def translate_time(time_string):
    time_obj=string_to_timeobject(time_string)
    local_time=localize_time(time_obj)
    time_string=get_time_of_day(local_time)
    return time_string

def db_to_calcurse_calendar(DBFILE):
    full_calendar=""
    full_notes = {}
    h = hashlib.sha1()
    DB_JSON=load_db(DBFILE)
    for item in DB_JSON:
        full_calendar += "{date} @ {start_time} -> {date} @ {end_time}>{notehash} !{sub} -- location:{location}\n".format(
        date=datetime.datetime.strptime(item['info']['start'][0:10], '%Y-%m-%d').strftime('%m/%d/%Y'),
        start_time=translate_time(item['info']['start']),
        end_time=translate_time(item['info']['end']),
        notehash=item['info']['notes'],
        sub=item['info']['subject'],
        location=item['info']['location'])
#    print(full_calendar)
    with open(".calcurse/test_appt", "w+") as f:
        f.write(full_calendar)

def db_to_calcurse_notes(NOTESDIR, DBFILE):
    DB_JSON=load_db(DBFILE)
    for item in DB_JSON:
        notehash=item['info']['notes']
        text_body=item['info']['text_body']
        with open(str(NOTESDIR + notehash), "w+") as f:
            f.write(text_body)

def main():
    DBFILE=os.environ['DBFILE']
    NOTESDIR=os.environ['NOTESDIR']
    db_to_calcurse_calendar(DBFILE)
    db_to_calcurse_notes(NOTESDIR, DBFILE)
    print("db -> calcurse " + str(datetime.datetime.now()))

main()
