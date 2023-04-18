import time
#import pygraphviz as pgv
import sys
import sqlite3
from pathlib import Path

def shift():
	return sys.argv.pop(0)

pyPath = shift()
dbPath = shift()
textPath = shift()
textName = shift()
textDesc = shift()
textLang = shift()
needSetup=True

def setup():
	for q in ['CREATE TABLE IF NOT EXISTS "groups" (groupId INTEGER PRIMARY KEY AUTOINCREMENT, "group" TEXT);',
'CREATE TABLE IF NOT EXISTS sents (sentId INTEGER PRIMARY KEY AUTOINCREMENT, sourceId INTEGER REFERENCES sources (sourceId), sentText TEXT);',
'CREATE TABLE IF NOT EXISTS sentsTocens (sentId INTEGER REFERENCES sents (sentId), tocenId INTEGER REFERENCES tocens (tocenId), tocenPos INTEGER);',
'CREATE TABLE IF NOT EXISTS sources (sourceId INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, "desc" TEXT, lang TEXT, size INTEGER, content TEXT);',
'CREATE TABLE IF NOT EXISTS tocenGroups (tocenId INTEGER REFERENCES tocens (tocenId), groupId INTEGER REFERENCES "groups" (groupId));',
'CREATE TABLE IF NOT EXISTS tocens (tocenId INTEGER PRIMARY KEY AUTOINCREMENT, tocen TEXT UNIQUE);',
'CREATE TABLE IF NOT EXISTS processedSources (sourceId INTEGER REFERENCES sources (sourceId));']:
		cur.execute(q)

#if not Path(dbPath).is_file(): # but don't setup file that is not db or empty db? TODO
#	needSetup = True
db = sqlite3.connect(dbPath)
cur = db.cursor()
if needSetup:
	setup()

with open(textPath, "r", encoding='utf-8') as f:
    text = f.read()
    textSize = len(text)
    
cur.execute("INSERT OR IGNORE INTO sources (name, desc, lang, size, content) VALUES (?,?,?,?,?)", [textName, textDesc, textLang, textSize, text])
textId = cur.execute("SELECT sourceId FROM sources WHERE name = ?", [textName]).fetchone()[0]
db.commit()
print(f"{textSize} chars")
print(f"{textId} id assigned")
