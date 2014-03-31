#!/usr/bin/env python
import email
import os
import os.path
import csv
import string
import sqlite3
import json
import collections

__DATASETLOCATION__ = "/Users/James/Documents/Enron Email Corpus/Edited Enron Email Dataset/maildir/"
__RESULTLOCATION__ = "/Users/James/Dropbox/Final Year Project/Technical Investigations/Analysis Scripts/"
__CSVLOCATION__ = __RESULTLOCATION__ + "EnronData.csv"

__LIWC__ = "/Users/James/Documents/Enron Email Corpus/LIWC/"
__BODYOUTPUT__ = __LIWC__ + "Input/"
__LIWCDATA__ = __LIWC__ + "Output/"

__DATABASELOCATION__ = "/Users/James/Documents/Enron Email Corpus/Enron.db"

__CSVHEADERS__ = ["Email_ID","Parent_Folder","User","Date","Subject","Email_From","Email_To","Body","Cc","Bcc","Number_of_Recipients","Length_of_Email_Body","Message_ID","Importance_Statement"]#,"FilePath"]
__LIWCHEADERS__ = ['WC', 'WPS', 'Sixltr', 'Dic', 'Numerals','funct', 'pronoun', 'ppron', 'i', 'we', 'you', 'shehe', 'they', 'ipron', 'article', 'verb', 'auxverb', 'past', 'present', 'future', 'adverb', 'preps', 'conj', 'negate', 'quant', 'number', 'swear', 'social', 'family', 'friend', 'humans', 'affect', 'posemo', 'negemo', 'anx', 'anger', 'sad', 'cogmech', 'insight', 'cause', 'discrep', 'tentat', 'certain', 'inhib', 'incl', 'excl', 'percept', 'see', 'hear', 'feel', 'bio', 'body', 'health', 'sexual', 'ingest', 'relativ', 'motion', 'space', 'time', 'work', 'achieve', 'leisure', 'home', 'money', 'relig', 'death', 'assent', 'nonfl', 'filler','Period', 'Comma', 'Colon', 'SemiC', 'QMark', 'Exclam', 'Dash', 'Quote', 'Apostro', 'Parenth', 'OtherP', 'AllPct']
__WEKAHEADERS__ = ["Email_ID","Importance_Statement","Number_of_Recipients","Length_of_Email_Body"] + __LIWCHEADERS__
__OUTPUT__ = "WEKA"

__CATEGORYMAPPINGLOCATION__ = "/Users/James/Dropbox/Final Year Project/Technical Investigations/Analysis Scripts/IDCategoryMapping.txt"
__NORMALISED__ = True

def parseEmail(emailPath):
	# INPUT: File location
	# OUTPUT: Dictionary of Email Headers -> Values. Body has been added to this separately.
	try:
		message = open(emailPath)
	except:
		print "Failed to open: " + emailPath

	fileObject = email.message_from_file(message)
	headers = fileObject.items()
	emailInfo = dict(headers)
	emailInfo['Body'] = str(fileObject.get_payload())
	message.close()
	return emailInfo

def initialiseCSV():
	# INPUT: None
	# OUTPUT: Creates new CSV, with headings below
	try:
		results = open(__CSVLOCATION__,'w')
	except IOError:
		print "Failed to open csv in: " + __CSVLOCATION__

	writer = csv.writer(results,dialect="excel")
	if (__OUTPUT__ == "CSV"):
		writer.writerow(__CSVHEADERS__+__LIWCHEADERS__)
	elif (__OUTPUT__ == "WEKA"):
		writer.writerow(__WEKAHEADERS__)
	results.close()

def initialiseDatabase():
	#delete if database already exists
	if os.path.exists(__DATABASELOCATION__):
		os.remove(__DATABASELOCATION__)

	database = sqlite3.connect(__DATABASELOCATION__)
	db = database.cursor()
	db.execute("CREATE TABLE enron (Email_ID INTEGER PRIMARY KEY,Parent_Folder TEXT,User TEXT,Date TEXT,Subject TEXT,Email_From TEXT,Email_To TEXT,Body TEXT,Cc TEXT,Bcc TEXT,Number_of_Recipients INTEGER,Length_of_Email_Body INTEGER,Message_ID TEXT,Subjective_Importance DOUBLE,Importance_Statement TEXT)")
	db.execute("CREATE TABLE LIWC (Email_ID INTEGER, WC DOUBLE, WPS DOUBLE, Sixltr DOUBLE, Dic DOUBLE, Numerals DOUBLE,funct DOUBLE, pronoun DOUBLE, ppron DOUBLE, i DOUBLE, we DOUBLE, you DOUBLE, shehe DOUBLE, they DOUBLE, ipron DOUBLE, article DOUBLE, verb DOUBLE, auxverb DOUBLE, past DOUBLE, present DOUBLE, future DOUBLE, adverb DOUBLE, preps DOUBLE, conj DOUBLE, negate DOUBLE, quant DOUBLE, number DOUBLE, swear DOUBLE, social DOUBLE, family DOUBLE, friend DOUBLE, humans DOUBLE, affect DOUBLE, posemo DOUBLE, negemo DOUBLE, anx DOUBLE, anger DOUBLE, sad DOUBLE, cogmech DOUBLE, insight DOUBLE, cause DOUBLE, discrep DOUBLE, tentat DOUBLE, certain DOUBLE, inhib DOUBLE, incl DOUBLE, excl DOUBLE, percept DOUBLE, see DOUBLE, hear DOUBLE, feel DOUBLE, bio DOUBLE, body DOUBLE, health DOUBLE, sexual DOUBLE, ingest DOUBLE, relativ DOUBLE, motion DOUBLE, space DOUBLE, time DOUBLE, work DOUBLE, achieve DOUBLE, leisure DOUBLE, home DOUBLE, money DOUBLE, relig DOUBLE, death DOUBLE, assent DOUBLE, nonfl DOUBLE, filler DOUBLE, Period DOUBLE, Comma DOUBLE, Colon DOUBLE, SemiC DOUBLE, QMark DOUBLE, Exclam DOUBLE, Dash DOUBLE, Quote DOUBLE, Apostro DOUBLE, Parenth DOUBLE, OtherP DOUBLE, AllPct DOUBLE)")
	database.commit()
	database.close()

def determineNumberOfRecipients(recipients):
	# INPUT: list containing to, cc and bcc fields as the 3 elements
	# OUTPUT: number of unique recipients
	parsedRecipients = []
	for field in recipients:
		if field is not None:
			split = string.split(field,',')
			for potentialRecipient in split:
				if (potentialRecipient not in parsedRecipients) and (potentialRecipient != ""):
					parsedRecipients.append(potentialRecipient)
	if (__NORMALISED__):
		return (len(parsedRecipients)/913.0) #max recipients = 913, min = 0
	else:
		return len(parsedRecipients)

def prepareDataForWrite(emailId,path,emailData):
	# Structure of emailData: [Date,Subject,From,To,Body,Cc,Bcc,Re,Origin,Folder,MessageID]

	#Generated info
	stub = string.split(path,"/")
	user = stub[7]
	parentFolder = stub[8]

	recipients = [emailData[3]] + emailData[5:6]
	numberOfRecipients = determineNumberOfRecipients(recipients)
	
	if (__NORMALISED__):
		lengthOfEmail = (len(emailData[4])-1.0)/2011421.0 #Max email length = 2011422, min = 1
	else:
		lengthOfEmail = len(emailData[4])

	if emailData[11] is None: #This needs to be changed to be more statistically correct.
		importanceStatement = None
	elif float(emailData[11]) < 0.76:
		importanceStatement = "Non Important"
	elif float(emailData[11]) >= 0.76:
		importanceStatement = "Important"
	else:
		importanceStatement = "Neutrally Important"

	return [emailId] + [parentFolder] + [user] + emailData[0:7] + [numberOfRecipients] + [lengthOfEmail] + emailData[10:12] + [importanceStatement]

def normaliseData(features,normalisationData):
	i=0
	while i<len(features):
		if (float(features[i]) != 0.0):
			features[i] = float(features[i])/float(normalisationData[i])
		i += 1
	return features

#def trimLIWCinput(liwcvalues):
	#['WC', 'WPS', 'Sixltr', 'Dic', 'Numerals','funct', 'pronoun', 'ppron', 'i', 'we', 'you', 'shehe', 'they', 'ipron', 'article', 'verb', 'auxverb', 'past', 'present', 'future', 'adverb', 'preps', 'conj', 'negate', 'quant', 'number', 'swear', 'social', 'family', 'friend', 'humans', 'affect', 'posemo', 'negemo', 'anx', 'anger', 'sad', 'cogmech', 'insight', 'cause', 'discrep', 'tentat', 'certain', 'inhib', 'incl', 'excl', 'percept', 'see', 'hear', 'feel', 'bio', 'body', 'health', 'sexual', 'ingest', 'relativ', 'motion', 'space', 'time', 'work', 'achieve', 'leisure', 'home', 'money', 'relig', 'death', 'assent', 'nonfl', 'filler','Period', 'Comma', 'Colon', 'SemiC', 'QMark', 'Exclam', 'Dash', 'Quote', 'Apostro', 'Parenth', 'OtherP', 'AllPct']
	#return [liwcvalues[3]]+[liwcvalues[]]+[liwcvalues[]]+[liwcvalues[]]+[liwcvalues[]]+[liwcvalues[]]+[liwcvalues[]]+[liwcvalues[]]+[liwcvalues[]]+[liwcvalues[]]+[liwcvalues[]]+[liwcvalues[]]+[liwcvalues[]]

def writeToCSV(emailId,path,emailData,normalisedData): #This is un-normalised.
	# INPUT: Unique ID of Email, Location of email, List containing the header values.
	# OUTPUT: Writes details to file.
	try:
		results = open(__CSVLOCATION__,'a')
	except IOError:
		print "Failed to open csv in: " + __CSVLOCATION__
	
	writer = csv.writer(results,dialect='excel')

	preparedData = prepareDataForWrite(emailID,path,emailData)

	if (__OUTPUT__ == "CSV"):
		#overwriting 
		preparedData[4] = None
		preparedData[5] = None
		preparedData[6] = None
		preparedData[7] = None
		preparedData[8] = None
		preparedData[9] = None

	elif (__OUTPUT__ == "WEKA"):
		#emaildata: [Date,Subject,From,To,Body,Cc,Bcc]
		preparedData = [preparedData[0]] + [preparedData[-1]] + [preparedData[-5]] + [preparedData[-4]] 
	
	sql = loadLIWCData(emailId)
	if (__NORMALISED__):
		sql = normaliseData(sql,normalisedData)

	data = preparedData + sql
	if (preparedData[-1] is not None):
		try: 
			writer.writerow(data)
		except:
			print "Could not write email: " + str(emailId)
			print data
			raise
	results.close

def writeBodyToFile(emailID,body):
	# INPUT: Headers list [Date,Subject,From,To,Body,Cc,Bcc,Attachment,Re,Origin,Folder]
	# OUTPUT: Writes just the body field to the CSV, separated by #SEG#
	try:
		output = open(__BODYOUTPUT__ + str(emailID),'w')
	except IOError:
		print "Failed to open: " + __BODYOUTPUT__ + str(emailID)
	output.write(body)
	output.close

def writeToDatabase(emailId,path,emailData,normalisedData):
	# INPUT: Unique ID of Email, Location of email, List containing the header values.
	# OUTPUT: Writes details to database.
	database = sqlite3.connect(__DATABASELOCATION__)
	db = database.cursor()
	preparedData = prepareDataForWrite(emailId,path,emailData)
	values = tuple(preparedData)
	db.execute("insert into enron values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",values)
	
	sql = loadLIWCData(emailId)
	if (__NORMALISED__):
		sql = normaliseData(sql,normalisedData)
	sql = tuple([emailId]) + tuple(sql)
	db.execute("insert into LIWC values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",sql)
	
	database.commit()
	database.close()

def attemptToSet(key,source):
	# INPUT: key: header key. source: Dictionary of header
	# OUTPUT: value of that key if exists. "" if doesn't
	try:
		headerField = unicode(source[key],'utf-8','replace')
		return headerField
	except KeyError:
		headerField = None #unicode("",'utf-8','replace')
		return headerField

def processData(headerList):
	# INPUT: Dictionary of headers
	# OUTPUT: Ordered list of header values
	Date = attemptToSet('Date',headerList)
	Subject = attemptToSet('Subject',headerList)
	Folder = attemptToSet('X-Folder',headerList)
	Origin = attemptToSet('X-Origin',headerList)
	Subject = attemptToSet('Subject',headerList)
	Re = attemptToSet('Re',headerList)
	Body = attemptToSet('Body',headerList)

	From = attemptToSet('From',headerList)
	To = attemptToSet('To',headerList)
	Cc = attemptToSet('Cc',headerList)
	Bcc = attemptToSet('Bcc',headerList)

	MessageID = attemptToSet('Message-ID',headerList)
	ImportanceRating = attemptToSet('Importance_Rating',headerList)

	return [Date,Subject,From,To,Body,Cc,Bcc,Re,Origin,Folder,MessageID,ImportanceRating]

def loadIDMappings():
	try:
		mappings = open(__CATEGORYMAPPINGLOCATION__,'r')
	except IOError:
		print "Failed to open mappings"
	IDtoImportanceMappings = json.load(mappings)
	mappings.close()
	return IDtoImportanceMappings

def loadLIWCData(emailID):
	try:
		liwc = open(__LIWCDATA__ + str(emailID),'r')
	except IOError:
		print "Failed to open: " + __LIWCDATA__ + str(emailID)
	data = json.load(liwc, object_pairs_hook=collections.OrderedDict)
	liwc.close()
	return data.values()

def loadNormalisedData():
	try:
		f = open("/Users/James/Dropbox/Final Year Project/Technical Investigations/Analysis Scripts/MinMax.txt",'r')
	except IOError:
		print "Failed to open: /Users/James/Dropbox/Final Year Project/Technical Investigations/Analysis Scripts/MinMax.txt"
	data = json.load(f, object_pairs_hook=collections.OrderedDict)
	f.close()
	return data.values() #max no for each LIWC data

if __name__ == "__main__":

	if (__OUTPUT__ == "CSV") or (__OUTPUT__ == "WEKA"):
		initialiseCSV()
	elif __OUTPUT__ == "DATABASE":
		initialiseDatabase()

	importanceMappings = loadIDMappings()
	minMax = loadNormalisedData()
	for root, dirs, files in os.walk(__DATASETLOCATION__):
		if len(files) > 0: #If files actually present
			for element in files:
				
				emailID = int(element)
				filePath = root + "/" + element

				if emailID%1000 == 0: #No of files processed
					print emailID
				
				data = parseEmail(filePath)

				if (data['Message-ID'] in importanceMappings):
					data['Importance_Rating'] = str(importanceMappings[data['Message-ID']])

				processedData = processData(data)

				if (__OUTPUT__ == "CSV") or (__OUTPUT__ == "WEKA"):
					writeToCSV(emailID,filePath,processedData,minMax)
				elif __OUTPUT__ == "DATABASE":
					writeToDatabase(emailID,filePath,processedData,minMax)
				elif __OUTPUT__ == "LIWC":
					writeBodyToFile(emailID,processedData[4])