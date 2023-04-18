import time
#import pygraphviz as pgv
import sys
import sqlite3

def shift():
	return sys.argv.pop(0)

def inRange(ch, *ranges):
    for r in ranges:
        if ch >= r[0] and ch <= r[1]:
            return True
    return False

def normalize(t):
    return t.lower().strip('.,:;!?"\'«»–()') # handle synonyms? TODO

pyPath = shift()
dbPath = shift()
textsNames = sys.argv

db = sqlite3.connect(dbPath)
cur = db.cursor()

def process(textName):
	textId, text = cur.execute("SELECT sourceId, content FROM sources WHERE name = ?", [textName]).fetchone()
	if cur.execute("SELECT * FROM processedSources WHERE sourceId = ?", [textId]).fetchone():
		print(f'already processed text №{textId} {textName}')
		return
		
	filters = [lambda i: not inRange(text[i - 1], 'АЯ'),  lambda i: text[i + 1] in [' ', '\n']] # for Russian only for now... TODO
	dotPos = [i for i in range(len(text)) if text[i] in ['.','!','?'] and all((f(i) for f in filters))] # not dotpos anyway lol TODO?
	#context = [text[i - 10 : i + 10] for i in dotPos]
	dotPosFixed = [0, *dotPos]
	sents = [text[dotPosFixed[i] : dotPosFixed[i + 1]] for i in range(len(dotPosFixed) - 1)]
	
	words = set()
	unnormalized=[]
	totalTocens=0
	for s in sents:
		v = [normalize(x) for x in s.split()]
		totalTocens+=len(v)
		words.update(v)
		unnormalized.append(v)
	
	lastSentId = int(cur.execute("SELECT MAX(sentId) FROM sents").fetchone()[0] or 0) # hope there're no shuffle of any cind uhh; or -1 to handle case then db is empty fo fetchone returns (None, )
	cur.executemany("INSERT INTO sents (sourceId, sentText) VALUES (?, ?)", [[textId, t] for t in sents])
	
	words = list(words)
	
	qData = [[t] for t in words]
	tocensCount = cur.execute('SELECT COUNT(*) FROM tocens').fetchone()[0]
	cur.executemany('INSERT OR IGNORE INTO tocens (tocen) VALUES (?)', qData) # made tocen field unique, as well as sourceName (needed?)
	newTocensCount = cur.execute('SELECT COUNT(*) FROM tocens').fetchone()[0]
	wordsIds = {}
	for v in cur.execute("SELECT * FROM tocens"):
		w = v[1]
		id=v[0]
		if w in words: # determine what % of tocens is new to requests old tocens throught queries or that method? TODO
			wordsIds[w] = id
	
	cur.executemany("INSERT INTO sentsTocens VALUES (?, ?, ?)", [[lastSentId + 1 + sentI, wordsIds[unnormalized[sentI][wordI]], wordI] for sentI in range(len(unnormalized)) for wordI in range(len(unnormalized[sentI]))])
	
	db.commit()
	print(f'{newTocensCount - tocensCount} new tocens. {len(sents)} total sents. {totalTocens} total tocens. for text №{textId} {textName}')

for name in textsNames:
	process(name)


