#!/usr/bin/env python
import email
import os
import json
import collections
import string
import dateutil.parser
import datetime
import re

__DATASET__ = "/Users/James/Documents/Enron Email Corpus/Edited Enron Email Dataset/maildir/"
__OUTPUT__ = "/Users/James/Documents/Enron Email Corpus/EmailsJSON.json"
__EXAMPLES__ = "/Users/James/Documents/Enron Email Corpus/ExampleEmailsJSON.json"
__THREADS__ = "/Users/James/Documents/Enron Email Corpus/Threads.json"
regex = re.compile('([\[\(] *)?(RE?S?|FYI|RIF|I|FS|VB|RV|ENC|ODP|PD|YNT|ILT|SV|VS|VL|AW|WG|FWD?) *([-:;)\]][ :;\])-]*|$)|\]+ *$', re.IGNORECASE)

def parseEmail(emailPath):
	# INPUT: File location
	# OUTPUT: Dictionary of Email Headers -> Values. Body has been added to this.
	try:
		message = open(emailPath)
	except:
		print "Failed to open: " + emailPath
	fileObject = email.message_from_file(message)
	parsed = fileObject.items()
	keys = []
	values = []
	for pairs in parsed:
		keys.append(pairs[0])
		values.append(unicode(str.decode(pairs[1],'cp1252')))
	headers = zip(keys,values)
	emailInfo = dict(headers)
	
	#fill leading 0 for strptime purposes.
	if (len(emailInfo['Date']) == 36):
		emailInfo['Date'] = emailInfo['Date'][:5]+'0'+emailInfo['Date'][5:]	

	#Adding parsed date in datetime format
	date = dateutil.parser.parse(str(emailInfo['Date']))
	
	#If time is timezone aware
	if (date.tzinfo is not None):
		#Applying timezone correction
		date = date + date.utcoffset()
		#Setting Naive
		date = date.replace(tzinfo=None)

	#This
	emailInfo['Date'] = unicode(date)
	#emailInfo['Date'] = date

	#Stripping FWD & RE
	emailInfo['Subject'] = regex.sub('',str(emailInfo['Subject'])).strip()

	emailInfo['Body'] = unicode(fileObject.get_payload())

	emailInfo['Thread'] = None

	stub = string.split(emailPath,"/")
	user = stub[7]
	parentFolder = stub[8]
	emailInfo['User'] = unicode(user)
	emailInfo['ParentFolder'] = unicode(parentFolder)
	message.close()
	return emailInfo

def determineThreads(dictionaryOfEmails):
	#Unsure if this produces the list in the order I want (oldest to newest, like the ordered list.)
	#List of EmailIDs
	keys = dictionaryOfEmails.keys()
	#print keys

	#Dictionary of Thread Titles: number of occurrences
	threads = {}
	i = 0
	#For every email

	while i<len(keys):
		#EmailID
		currentEmail = keys[i] 
		
		#Current emails subject
		subject = dictionaryOfEmails[currentEmail]['Subject']

		#If subject is empty
		if (subject == ""):
			i += 1
			if i%1000 == 0:
				print i
			continue


		#If that subject already in threads
		elif subject in threads:
			#Set thread to subject
			dictionaryOfEmails[currentEmail]['Thread'] = subject
			#Increment number of occurrences
			threads[subject] += 1
		
		else:
			#Date of currentEmail 
			date = dateutil.parser.parse(str(dictionaryOfEmails[currentEmail]['Date']))

			#DateLimit
			days = datetime.timedelta(days = 1)
			dateLimit = date + days
			
			#Start at the element after i
			j = i + 1
			if j > len(keys):
				break
			
			#While the dates of the next values are under 1 day (bounding search space)
			while (dateutil.parser.parse(str(dictionaryOfEmails[keys[j]]['Date'])) < dateLimit):
				#If subjects match
				if dictionaryOfEmails[keys[j]]['Subject'] == subject:
					#Add subject to threads and initialise to 1
					threads[subject] = 1
					dictionaryOfEmails[currentEmail]['Thread'] = subject
					break
				else:	
					j += 1
					if j > len(keys):
						break
		
		i += 1
		if i%1000 == 0:
			print i
	return [dictionaryOfEmails,threads]


def writeResultsJSON(results,filepath):
	try:
		f = open(filepath,'w')
	except IOError:
		print "Failed to open"
	json.dump(results,f)
	f.close()

emails = collections.OrderedDict()
i = 0

for root, dirs, files in os.walk(__DATASET__):
	if len(files) > 0: #If files actually present
		for element in files:
			if (element != '.DS_Store'):
				i += 1
				if i%1000 == 0:
					print i

				emailID = int(element)
				filePath = root + "/" + element		
				data = parseEmail(filePath)
				emails[emailID] = data

print "Sorting emails"
sortedEmails = collections.OrderedDict(sorted(emails.items(), key=lambda t: dateutil.parser.parse(str(t[1]['Date']))))

print "Deleting emails"
del emails

print "Determining threads"
results = determineThreads(sortedEmails)

print "Completed determining " + str(len(results[1])) + " threads"

print "Deleting sorted Emails"
a = str(len(sortedEmails))
del sortedEmails

threadedEmails = results[0]
threads = results[1]

print "Writing " + a + " results"
writeResultsJSON(threadedEmails,__OUTPUT__)

print "Completed writing full emails"

print "Writing Threads"
#threads = sorted(threads, key=lambda t:t[1])
writeResultsJSON(threads,__THREADS__)

print "Completed writing threads"

j = 0
example = collections.OrderedDict()
while j<1000:
	j += 1
 	if j%100 == 0:
 		print j
	b = threadedEmails.popitem(last = False)
	example[b[0]] = b[1]


print "Writing example results"
writeResultsJSON(example,__EXAMPLES__)

print "Fin."