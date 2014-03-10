#!/usr/bin/env python
import email
import os
import csv
import string

def parseEmail(emailPath):
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
	try:
		results = open("/Users/James/Dropbox/Final Year Project/Technical Investigations/Analysis Scripts/EnronData.csv",'w')
	except:
		print "Failed to open csv"

	writer = csv.writer(results,dialect="excel")
	headings = ["Email ID","Parent Folder","User","Date","Subject","From","To","Body","Cc","Bcc","Attachment","Path"]
	writer.writerow(headings)
	results.close()

def writeToCSV(emailId,path,emailData):
	try:
		results = open("/Users/James/Dropbox/Final Year Project/Technical Investigations/Analysis Scripts/EnronData.csv",'a')
	except:
		print "Failed to open csv"
	
	writer = csv.writer(results,dialect='excel')
	
	# Structure of emailData: [Date,Subject,From,To,Body,Cc,Bcc,Attachment,Re,Origin,Folder]

	#Generated info
	parentFolder = str(path.rpartition("/")[-1])
	user = string.split(root,"/")[7]

	#Previously gathered info
	
	email = [emailId,parentFolder,user] + emailData[0:8] + [path]
	writer.writerow(email)
	results.close

def attemptToSet(key,source):
	try:
		headerField = source[key]
		return headerField
	except KeyError:
		headerField = ""
		return headerField

def attemptToSetDouble(key1,key2,source):
	if key1 in source and key2 in source:
		print "Both keys in dictionary, enjoy sorting this mess out! Key1: " + key1 +": " + source[key1] + ", Key2 " + key2 +": " + source[key2]
	elif key1 in source:
		return source[key1]
	elif key2 in source:
		return source[key2]
	else:
		print "Neither key1 nor key2 in dictionary, eh?"
		return ""

def processData(headerList):
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

	#Multiple possibilities
	# From = attemptToSetDouble('From','X-From',headerList)
	# To = attemptToSetDouble('To','X-To',headerList)
	# Cc = attemptToSetDouble('Cc','X-cc',headerList)
	# Bcc = attemptToSetDouble('Bcc','X-bcc',headerList)

	if attemptToSet('X-FileName',headerList) != "":
		Attachment = True
	else:
		Attachment = False

	return [Date,Subject,From,To,Body,Cc,Bcc,Attachment,Re,Origin,Folder]


# collatedHeaders = []
i = 0
initialiseCSV()
for root, dirs, files in os.walk("/Users/James/Documents/Enron Email Corpus/Edited Enron Email Dataset/maildir"):
	if len(files) > 0: #If files actually present
		for element in files:
			i = i+1
			if i%1000 == 0: #No of files processed
				print i

			filePath = root + "/" + element
			data = parseEmail(filePath)
			processedData = processData(data)
			writeToCSV(i,root,processedData)
# 			headers = data[0]
# 			for header in headers:
# 				if header[0] not in collatedHeaders:
# 					collatedHeaders.append(header[0])
# print collatedHeaders