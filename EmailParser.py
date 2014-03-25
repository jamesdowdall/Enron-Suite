#!/usr/bin/env python
import email
import os
import os.path
import csv
import string
import sqlite3

__DATASETLOCATION__ = "/Users/James/Documents/Enron Email Corpus/Edited Enron Email Dataset/maildir/"
__RESULTLOCATION__ = "/Users/James/Dropbox/Final Year Project/Technical Investigations/Analysis Scripts/"
__CSVLOCATION__ = __RESULTLOCATION__ + "EnronData.csv"
__BODYLOCATION__ = __RESULTLOCATION__ + "EnronBodies.txt"
__DATABASELOCATION__ = "/Users/James/Documents/Enron Email Corpus/Enron.db"

__CSVHEADERS__ = ["Email_ID","Parent_Folder","User","Date","Subject","Email_From","Email_To","Body","Cc","Bcc","Number_of_Recipients","Length_of_Email_Body","Message_ID"]#,"FilePath"]
__OUTPUT__ = ""


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
	writer.writerow(__CSVHEADERS__)
	results.close()

def initialiseDatabase():
	#delete if database already exists
	if os.path.exists(__DATABASELOCATION__):
		os.remove(__DATABASELOCATION__)

	database = sqlite3.connect(__DATABASELOCATION__)
	db = database.cursor()
	db.execute("CREATE TABLE enron (Email_ID,Parent_Folder,User,Date,Subject,Email_From,Email_To,Body,Cc,Bcc,Number_of_Recipients,Length_of_Email_Body,Message_ID)")
	database.commit()
	database.close()

def determineNumberOfRecipients(recipients):
	# INPUT: list containing to, cc and bcc fields as the 3 elements
	# OUTPUT: number of unique recipients
	parsedRecipients = []
	for field in recipients:
		split = string.split(field,',')
		for potentialRecipient in split:
			if (potentialRecipient not in parsedRecipients) and (potentialRecipient != ""):
				parsedRecipients.append(potentialRecipient)
	return len(parsedRecipients)

def prepareDataForWrite(emailId,path,emailData):
	# Structure of emailData: [Date,Subject,From,To,Body,Cc,Bcc,Re,Origin,Folder,MessageID]

	#Generated info
	stub = string.split(path,"/")
	user = stub[7]
	parentFolder = stub[8]

	recipients = [emailData[3]] + emailData[5:6]
	numberOfRecipients = determineNumberOfRecipients(recipients)
	lengthOfEmail = len(emailData[4])	
	return [emailId] + [parentFolder] + [user] + emailData[0:7] + [numberOfRecipients] + [lengthOfEmail] + [emailData[10]]


def writeToCSV(emailId,path,emailData):
	# INPUT: Unique ID of Email, Location of email, List containing the header values.
	# OUTPUT: Writes details to file.
	try:
		results = open(__CSVLOCATION__,'a')
	except IOError:
		print "Failed to open csv in: " + __CSVLOCATION__
	
	writer = csv.writer(results,dialect='excel')

	#Cutting down overflow of Body length
	if len(emailData[4]) > 32767:
		emailData[4] = emailData[4][0:32600]

	preparedData = prepareDataForWrite(emailID,path,emailData)
	try: 
		writer.writerow(preparedData)
	except:
		print "Could not write email: " + str(emailId)
	results.close

def writeBodyToFile(headers):
	# INPUT: Headers list [Date,Subject,From,To,Body,Cc,Bcc,Attachment,Re,Origin,Folder]
	# OUTPUT: Writes just the body field to the CSV, separated by #SEG#
	try:
		bodies = open(__BODYLOCATION__,'a')
	except IOError:
		print "Failed to open: " + __BODYLOCATION__
	body = headers[4]
	bodies.write(body + '#SEG#')
	bodies.close

def writeToDatabase(emailId,path,emailData):
	# INPUT: Unique ID of Email, Location of email, List containing the header values.
	# OUTPUT: Writes details to database.
	database = sqlite3.connect(__DATABASELOCATION__)
	db = database.cursor()

	preparedData = prepareDataForWrite(emailId,path,emailData)
	values = tuple(preparedData)
	db.execute("insert into enron values (?,?,?,?,?,?,?,?,?,?,?,?,?)",values)
	database.commit()
	database.close()

def attemptToSet(key,source):
	# INPUT: key: header key. source: Dictionary of header
	# OUTPUT: value of that key if exists. "" if doesn't
	try:
		headerField = unicode(source[key],'utf-8','replace')
		return headerField
	except KeyError:
		headerField = unicode("",'utf-8','replace')
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

	return [Date,Subject,From,To,Body,Cc,Bcc,Re,Origin,Folder,MessageID]


if __name__ == "__main__":

	if __OUTPUT__ == "CSV":
		initialiseCSV()
	else:
		initialiseDatabase()

	for root, dirs, files in os.walk(__DATASETLOCATION__):
		if len(files) > 0: #If files actually present
			for element in files:
				
				emailID = int(element)
				filePath = root + "/" + element

				if emailID%1000 == 0: #No of files processed
					print emailID

				
				data = parseEmail(filePath)
				processedData = processData(data)

				if __OUTPUT__ == "CSV":
					writeToCSV(emailID,filePath,processedData)
				else:
					writeToDatabase(emailID,filePath,processedData)
				
				#writeBodyToFile(processedData)