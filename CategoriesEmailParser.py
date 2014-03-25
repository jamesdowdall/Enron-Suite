#!/usr/bin/env python
import email
import os
import csv
import string
import EmailParser

__CATEGORIESLOCATION__ = "/Users/James/Documents/Enron Email Corpus/enron_with_categories"

def parseCats(location):
	try:
		cats = open(location)
	except:
		print "Failed to open: " + location
		print "Please make sure that only files with categories are present in enron_with_categories"

	categories = []
	for line in cats:
		categoryRecord = line.split(',')
		categoryId = categoryRecord[0]+'.'+categoryRecord[1]
		frequency = categoryRecord[2].strip('\n')
		categories.append([categoryId,frequency])
	
	cats.close()
	return categories

def writeToCSV(emailId,path,emailData,categories,importance):
	try:
		results = open("/Users/James/Dropbox/Final Year Project/Technical Investigations/Analysis Scripts/Categories.csv",'a')
	except IOError:
		print "Failed to open csv"
	
	writer = csv.writer(results,dialect='excel')
	
	# Structure of emailData: [Date,Subject,From,To,Body,Cc,Bcc,Attachment,Re,Origin,Folder]
	if len(emailData[4])> 32767:
		emailData[4] = emailData[4][0:32600]
		#print 'Too Great in Length: ' + str(emailId)

	#Previously gathered info
	
	email = [emailId] + emailData[0:7] + [importance] + categories
	writer.writerow(email)
	results.close

def initialiseCSV():
	try:
		results = open("/Users/James/Dropbox/Final Year Project/Technical Investigations/Analysis Scripts/Categories.csv",'w')
	except IOError:
		print "Failed to open csv"

	writer = csv.writer(results,dialect="excel")
	headings = ["Email ID","Date","Subject","From","To","Body","Cc","Bcc","Category Importance Rating","Category"]
	writer.writerow(headings)
	results.close()

def calculateSubjectiveImportance(categories):
	importanceRating = float(0)
	numberOfRatings = float(0)
	for element in categories:
		frequency = float(element[1])
		importanceRating += getImportanceRating(element[0])*frequency
		numberOfRatings += float(frequency)
	return importanceRating/numberOfRatings

def getImportanceRating(categoryID):
	
	subjectiveImportanceRatings = {
	#Strong Positive Correlation - 1
	'1.5' : 1, '1.6' : 1, '2.6' : 1, '2.8' : 1, '3.1' : 1, '3.2' : 1, '3.5' : 1, '3.6' : 1, '3.10' : 1,

	#Positive Correlation - 0.75
	'1.1' : 0.75, '1.4' : 0.75, '2.3' : 0.75, '2.4' : 0.75, '2.5' : 0.75, '3.4' : 0.75, '3.7' : 0.75, '3.8' : 0.75, '3.9' : 0.75, '3.11' : 0.75, '3.12' : 0.75, '3.13' : 0.75, 

	#Neutral - 0.5
	'1.2' : 0.5, '1.3' : 0.5, '2.1' : 0.5, '2.2' : 0.5, '2.9' : 0.5, '2.13' : 0.5, '3.3' : 0.5,  

	#Negative Correlation - 0.25
	'2.7' : 0.25, '2.10' : 0.25, '2.11' : 0.25, '2.12' : 0.25, 

	#Strong Negative Correlation - 0
	'1.7' : 0, '1.8' : 0
	}
	if (int(categoryID[0]) == 4):
		return 0.5
	else:
		return float(subjectiveImportanceRatings[categoryID])


if __name__ == "__main__":
	i = 0
	initialiseCSV()
	for root, dirs, files in os.walk(__DIRLOCATION__):
		if len(files) > 0:
			filenames = os.listdir(root)
			
			#Remove .cats files from listdir
			for names in filenames:
				if (names.split('.')[-1] == 'cats'):
					filenames.remove(names)
			
			for names in filenames:
				i = i+1
				if i%300 == 0: #No of files processed
					print i

				filePath = root + "/" + names
				catsFile = filePath.split('.')[0] + '.cats'
				
				categoryInfo = parseCats(catsFile)
				importanceRating = calculateSubjectiveImportance(categoryInfo)

				data = EmailParser.parseEmail(filePath)
				processedData = EmailParser.processData(data)

				#writeToCSV(i,filePath,processedData,categoryInfo,importanceRating)

				