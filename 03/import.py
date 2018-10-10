import sys
import parseHelper
import sqlite3

textFilename = sys.argv[1]
dbFilename = sys.argv[2]

qry = open('scorelib.sql', 'r').read()
conn = sqlite3.connect( dbFilename )
cur = conn.cursor()
cur.executescript(qry)
conn.commit()

def load(filename):
	prints = []
	file = open(filename, 'r', encoding='utf-8')
	
	printLinesArray = []
	for line in file:
		if line in ['\n', '\r\n']:
			if(len(printLinesArray) > 0):
				prints.append(parseHelper.processPrintLines(printLinesArray))
				printLinesArray = []
		else:
			printLinesArray.append(line)
	prints.append(parseHelper.processPrintLines(printLinesArray))
	return prints

def addPersonToDb(person):
	born = person.born
	died = person.died
	cur.execute('SELECT * FROM person WHERE name=?', (person.name,))
	row = cur.fetchone()
	if(row != None):
		if(row[1] != None):
			born = row[1]
		if(row[2] != None):
			died = row[2]		
		cur.execute('UPDATE person SET born=?, died=? WHERE name=?', (born, died, person.name))
	else:
		cur.execute('INSERT INTO person (born, died, name) VALUES (?, ?, ?)', (born, died, person.name))
	
	return cur.lastrowid

def addCompositionToDb(c):
	cur.execute('SELECT * FROM score WHERE name=? AND genre=? AND key=? AND incipit=? AND year=?',(c.name, c.genre, c.key, c.incipit, c.year))
	row = cur.fetchone()
	if(row != None):
		return 0
		
	cur.execute('INSERT INTO score (name, genre, key, incipit, year) VALUES (?, ?, ?, ?, ?)', (c.name, c.genre, c.key, c.incipit, c.year))
	return cur.lastrowid

def addVoiceToDb(v, compId, number):
	cur.execute('SELECT * FROM voice WHERE number=? AND score=? AND range=? AND name=?',(number, compId, v.range, v.name))
	row = cur.fetchone()
	if(row != None):
		return
		
	cur.execute('INSERT INTO voice (number, score, range, name) VALUES (?, ?, ?, ?)',(number, compId, v.range, v.name))
	
def addEditionToDb(e, compId):
	cur.execute('SELECT * FROM edition WHERE score=? AND name=?',(compId, e.name))
	row = cur.fetchone()
	if(row != None):
		return 0
	else:
		cur.execute('INSERT INTO edition (score, name, year) VALUES (?, ?, ?)',(compId, e.name, None))
	return cur.lastrowid

def fillScoreAuthor(authId, compId):
	cur.execute('INSERT INTO score_author (score, composer) VALUES (?, ?)',(compId, authId))
	
def fillEditionAuthor(authId, editId):
	cur.execute('INSERT INTO edition_author (edition, editor) VALUES (?, ?)',(editId, authId))

def addPrintToDb(p, editId):
	partiture = "Y" if p.partiture else "N"
	cur.execute('INSERT INTO print (partiture, edition) VALUES (?, ?)',(partiture, editId))
	
for Print in load(textFilename):
	compId = addCompositionToDb(Print.composition())
	editId = addEditionToDb(Print.edition, compId)
	
	for person in Print.composition().authors:
		authId = addPersonToDb(person)
		fillScoreAuthor(authId, compId)
		
	for person in Print.edition.authors:
		authId = addPersonToDb(person)
		fillEditionAuthor(authId, editId)
	
	if(compId > 0):
		counter = 1
		for voice in Print.composition().voices:
			if(voice != None):
				addVoiceToDb(voice, compId, counter)
			counter = counter + 1
	
	addPrintToDb(Print, editId)
		
	
		
conn.commit()