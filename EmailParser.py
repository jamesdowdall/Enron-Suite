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
__JSONLOCATION__ = __RESULTLOCATION__ + "EnronData.json"

__LIWC__ = "/Users/James/Documents/Enron Email Corpus/LIWC/"
__BODYOUTPUT__ = __LIWC__ + "Input/"
__LIWCDATA__ = __LIWC__ + "Output/"

__DATABASELOCATION__ = "/Users/James/Documents/Enron Email Corpus/Enron.db"

__CSVHEADERS__ = ["Email_ID","Parent_Folder","User","Date","Subject","Email_From","Email_To","Body","Cc","Bcc","Number_of_Recipients","Length_of_Email_Body","Message_ID","Importance_Statement"]#,"FilePath"]
__LIWCHEADERS__ = ['WC', 'WPS', 'Sixltr', 'Dic', 'Numerals','funct', 'pronoun', 'ppron', 'i', 'we', 'you', 'shehe', 'they', 'ipron', 'article', 'verb', 'auxverb', 'past', 'present', 'future', 'adverb', 'preps', 'conj', 'negate', 'quant', 'number', 'swear', 'social', 'family', 'friend', 'humans', 'affect', 'posemo', 'negemo', 'anx', 'anger', 'sad', 'cogmech', 'insight', 'cause', 'discrep', 'tentat', 'certain', 'inhib', 'incl', 'excl', 'percept', 'see', 'hear', 'feel', 'bio', 'body', 'health', 'sexual', 'ingest', 'relativ', 'motion', 'space', 'time', 'work', 'achieve', 'leisure', 'home', 'money', 'relig', 'death', 'assent', 'nonfl', 'filler','Period', 'Comma', 'Colon', 'SemiC', 'QMark', 'Exclam', 'Dash', 'Quote', 'Apostro', 'Parenth', 'OtherP', 'AllPct']
__WEKAHEADERS__ = ["Email_ID","Importance_Statement","Number_of_Recipients","Length_of_Email_Body","Number_of_Tos","Number_of_Ccs","Number_of_Bccs"] + __LIWCHEADERS__
__OUTPUT__ = "WEKA"

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
				if (potentialRecipient not in parsedRecipients) and (potentialRecipient != ""): #Unique & Not Empty
					parsedRecipients.append(potentialRecipient)
	return len(parsedRecipients)

def prepareDataForWrite(emailId,user,parentFolder,emailData):
	# Structure of emailData: [Date,Subject,From,To,Body,Cc,Bcc,Re,Origin,Folder,MessageID]

	To = [emailData[3]]
	Cc = [emailData[5]]
	Bcc = [emailData[6]]
	recipients = To + Cc + Bcc
	numberOfRecipients = determineNumberOfRecipients(recipients)
	numberOfTos = determineNumberOfRecipients(To)
	numberOfCcs = determineNumberOfRecipients(Cc)
	numberOfBccs = determineNumberOfRecipients(Bcc)
	
	lengthOfEmail = len(emailData[4])

	if emailData[11] is None: #This needs to be changed to be more statistically correct.
		importanceStatement = None
	elif float(emailData[11]) < 0.75:
		importanceStatement = "Non Important"
	elif float(emailData[11]) >= 0.75:
		importanceStatement = "Important"
	else:
		importanceStatement = "Neutrally Important"

	#emailData[0:7] = [Date,Subject,From,To,Body,Cc,Bcc]
	#emailData[10:12] = [MessageID,ImportanceRating]
	return [emailId] + [parentFolder] + [user] + emailData[0:7] + [numberOfRecipients] + [lengthOfEmail] + emailData[10:12] + [importanceStatement] + [numberOfTos] + [numberOfCcs] + [numberOfBccs]

def normaliseLIWC(features,normalisationData):
	i = 0
	while i<len(features):
		if (float(features[i]) != 0.0):
			features[i] = float(str(features[i]))/float(normalisationData[i])
		i += 1
	return features

def normaliseResults(results, lower, upper):
	#INPUT: Results - List of lists containing values, lower = lower bound values, upper = upper values
	i = 0
	upperminuslower = []
	while i < len(lower):
		upperminuslower.append(upper[i] - lower[i])
		i += 1

	for result in results:
		j = 2
		#print result
		while j < len(result):
			if upperminuslower[j-2] == 0.0: #If denom is 0
				result[j] = 0.0
			else: 
				result[j] = (float(result[j]) - lower[j-2])/upperminuslower[j-2]
			j += 1 

	return results

def writeAllToCSV(emailData):
	try:
		results = open(__CSVLOCATION__,'a')
	except IOError:
		print "Failed to open csv in: " + __CSVLOCATION__
	writer = csv.writer(results,dialect='excel')
	for data in emailData:
		try: 
			writer.writerow(data)
		except:
			print "Could not write email: " + str(emailId)
			print data
			raise
	results.close

# def writeToCSV(emailId,user,parentFolder,emailData,normalisedData): #This is un-normalised.
# 	# INPUT: Unique ID of Email, Location of email, List containing the header values.
# 	# OUTPUT: Writes details to file.
# 	try:
# 		results = open(__CSVLOCATION__,'a')
# 	except IOError:
# 		print "Failed to open csv in: " + __CSVLOCATION__
	
# 	writer = csv.writer(results,dialect='excel')

# 	preparedData = prepareDataForWrite(emailID,user,parentFolder,emailData)

# 	if (__OUTPUT__ == "CSV"):
# 		#overwriting 
# 		preparedData[4] = None
# 		preparedData[5] = None
# 		preparedData[6] = None
# 		preparedData[7] = None
# 		preparedData[8] = None
# 		preparedData[9] = None

# 	elif (__OUTPUT__ == "WEKA"):
# 		#emaildata: [Date,Subject,From,To,Body,Cc,Bcc]
# 		print len(preparedData)
# 		#preparedData = [preparedData[0]] + [preparedData[-1]] + [preparedData[-5]] + [preparedData[-4]]
# 		#EmailID, Importance Statement, Number of Recipients, Email Length 
# 		preparedData = [preparedData[0]] + [preparedData[14]] + [preparedData[10]] + [preparedData[11]] 
	

# 	sql = loadJSONOrderedDict(__LIWCDATA__ + str(emailId)).values()
# 	if (__NORMALISED__):
# 		sql = normaliseLIWC(sql,normalisedData)

# 	data = preparedData + sql
# 	if (preparedData[-1] is not None):
# 		try: 
# 			writer.writerow(data)
# 		except:
# 			print "Could not write email: " + str(emailId)
# 			print data
# 			raise
# 	results.close

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
	
	#sql = loadLIWCData(emailId)
	sql = loadJSONOrderedDict(__LIWCDATA__ + str(emailId)).values()
	if (__NORMALISED__):
		sql = normaliseLIWC(sql,normalisedData)
	sql = tuple([emailId]) + tuple(sql)
	db.execute("insert into LIWC values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",sql)
	
	database.commit()
	database.close()

def attemptToSet(key,source):
	# INPUT: key: header key. source: Dictionary of header
	# OUTPUT: value of that key if exists. "" if doesn't
	try:
		headerField = source[key]#unicode(source[key],'utf-8','replace')
		return headerField
	except KeyError:
		headerField = None #unicode("",'utf-8','replace')
		return headerField

def processData(headerList): #This can probably be improved 
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

def writeResultsJSON(results,filepath):
	try:
		f = open(filepath,'w')
	except IOError:
		print "Failed to open: " + str(filepath)
	json.dump(results,f)
	f.close()

def loadJSONOrderedDict(filepath):
	try:
		f = open(filepath,'r')
	except IOError:
		print "Failed to open:" + str(filepath)
	data = json.load(f, object_pairs_hook=collections.OrderedDict)
	f.close()
	return data

if __name__ == "__main__":

	if (__OUTPUT__ == "CSV") or (__OUTPUT__ == "WEKA"):
		initialiseCSV()
	elif __OUTPUT__ == "DATABASE":
		initialiseDatabase()

	
	output = []
	#ANLP Category Data
	importanceMappings = loadJSONOrderedDict("/Users/James/Dropbox/Final Year Project/Technical Investigations/Analysis Scripts/IDCategoryMapping.txt")
	print "Importance Mappings loaded"
	
	#All Emails
	emails = loadJSONOrderedDict("/Users/James/Documents/Enron Email Corpus/EmailsJSON.json")
	print "Emails loaded"

	#Selection Criteria
	i = 0
	emailSelection = {}
	print "Checking Criteria"
	for email in emails.keys():
		i += 1
		if i%5000 == 0:
			print i

		#data = emails[email]
		data = emails.pop(email)
		
		#If email is in ANLP dataset
		if (data['Message-ID'] in importanceMappings):
			emailSelection[email] = data

	del emails
	#emails could be thrown out here

	i = 0
	print "Processing Selected Emails"
	minimum = []
	maximum = []
	for email in emailSelection.keys():
		emailID = int(email)

		i += 1
		if i%500 == 0:
			print i

		data = emailSelection[email]
		user = data['User']
		parentFolder = data['ParentFolder']
		
		#Assign Importance Rating. Don't have to check for existance as this is checked above.
		data['Importance_Rating'] = str(importanceMappings[data['Message-ID']])

		processedData = processData(data)
		preparedData = prepareDataForWrite(emailID,user,parentFolder,processedData)

		#Cutting down to only useful values
		#EmailID, Importance Statement, Number or Recipients, Email Length, Number of Tos, Number of Ccs, Number of Bccs
		preparedData = [preparedData[0]] + [preparedData[14]] + [preparedData[10]] + [preparedData[11]] + [preparedData[15]] + [preparedData[16]] + [preparedData[17]] 
		
		#Loading LIWC values for this email
		sql = loadJSONOrderedDict(__LIWCDATA__ + email).values()
		
		#Assembling write string
		data = preparedData + sql

		if (__NORMALISED__):#Ensure min & max are correct length & full of unlikely values
			while (len(minimum) < (len(data)-2)):
				minimum.append(100.0)
				maximum.append(0.0)

			j = 2 #Ignore emailID & Importance Statement
			while j<len(data):
				if float(str(data[j])) < minimum[j-2]:
					minimum[j-2] = float(str(data[j]))
				elif float(str(data[j])) > maximum[j-2]:
					maximum[j-2] = float(str(data[j]))
				j += 1
		
		output.append(data)

	if (__NORMALISED__):
		print "Normalising Data"
		#print minimum
		#print maximum
		output = normaliseResults(output, minimum, maximum)

	print "Writing to CSV"
	writeAllToCSV(output)
	print "Writing to JSON"


	# for root, dirs, files in os.walk(__DATASETLOCATION__):
	# 	if len(files) > 0: #If files actually present
	# 		for element in files:
				
	# 			emailID = int(element)
	# 			filePath = root + "/" + element

	# 			i += 1
	# 			if i%1000 == 0:
	# 				print i
				
	# 			data = parseEmail(filePath)

	# 			if (data['Message-ID'] in importanceMappings):
	# 				data['Importance_Rating'] = str(importanceMappings[data['Message-ID']])

	# 			processedData = processData(data)

	# 			if (__OUTPUT__ == "CSV") or (__OUTPUT__ == "WEKA"):
	# 				writeToCSV(emailID,filePath,processedData,minMax)
	# 			elif __OUTPUT__ == "DATABASE":
	# 				writeToDatabase(emailID,filePath,processedData,minMax)
	# 			elif __OUTPUT__ == "LIWC":
	# 				writeBodyToFile(emailID,processedData[4])