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

__LIWC__ = "/Users/James/Documents/Enron Email Corpus/LIWC/"
__BODYOUTPUT__ = __LIWC__ + "Input/"
__LIWCDATA__ = __LIWC__ + "Output/"

__OUTPUT__ = "LIWC"


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
	elif float(emailData[11]) <= 0.75:
		importanceStatement = "Non Important"
	elif float(emailData[11]) > 0.75:
		importanceStatement = "Important"
	else:
		importanceStatement = "Neutrally Important"

	#emailData[0:7] = [Date,Subject,From,To,Body,Cc,Bcc]
	#emailData[10:12] = [MessageID,ImportanceRating]
	return [emailId] + [parentFolder] + [user] + emailData[0:7] + [numberOfRecipients] + [lengthOfEmail] + emailData[10:12] + [importanceStatement] + [numberOfTos] + [numberOfCcs] + [numberOfBccs] + [emailData[12]]

d

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

def writeBodyToFile(emailID,body):
	# INPUT: Headers list [Date,Subject,From,To,Body,Cc,Bcc,Attachment,Re,Origin,Folder]
	# OUTPUT: Writes just the body field to the CSV, separated by #SEG#
	try:
		output = open(__BODYOUTPUT__ + str(emailID),'w')
	except IOError:
		print "Failed to open: " + __BODYOUTPUT__ + str(emailID)
	output.write(body)
	output.close

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
	Thread = attemptToSet('Thread',headerList)
	if(Thread is not None):
		Thread = "In Thread"
	else:
		Thread = "Not In Thread"

	return [Date,Subject,From,To,Body,Cc,Bcc,Re,Origin,Folder,MessageID,ImportanceRating,Thread]


for root, dirs, files in os.walk(__DATASETLOCATION__):
	if len(files) > 0: #If files actually present
		for element in files:
			
			emailID = int(element)
			filePath = root + "/" + element

			i += 1
			if i%1000 == 0:
				print i
			
			data = parseEmail(filePath)

			processedData = processData(data)

			if __OUTPUT__ == "LIWC":
				writeBodyToFile(emailID,processedData[4])