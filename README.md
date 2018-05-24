# ex2caldav
python scripts to sync exchange and caldav

current setup:
ex2db.py
---
pulls exchange stuff, places into json db file

db2cal.py
---
brings in new items from db into apts

watcher.py
---
currently just runs passes args and runs ex2db.py, db2cal.py

TODO:
Currently this is one way syncing, I'd like 2 way syncing
* parse differences between calcurse and db file and based on this
** if item exists in db but not calcurse, add it to calcurse
** if item exists in calcurse but not db add to db with last_modified
matching the last touched of calcurse file
** if item is added to db_file from calcurse push it to exchange
* setup as a long running process
** write systemd service and timer
** setup logic to pull from exchange in days, weeks, months in an
order of more frequent to less frequent respectively for more
efficient syncing
