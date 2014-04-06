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

	emailInfo['Date'] = unicode(date)

	#Stripping FWD & RE
	emailInfo['Subject'] = regex.sub('',str(emailInfo['Subject'])).strip()

	emailInfo['Body'] = unicode(fileObject.get_payload())

	stub = string.split(emailPath,"/")
	user = stub[7]
	parentFolder = stub[8]
	emailInfo['User'] = unicode(user)
	emailInfo['ParentFolder'] = unicode(parentFolder)
	message.close()
	return emailInfo

def writeResultsJSON(results,filepath):
	try:
		f = open(__OUTPUT__,'w')
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
				#print dateutil.parser.parse(str(emails[emailID]['Date']))
				#print type(dateutil.parser.parse(str(emails[emailID]['Date'])))

print "Sorting emails"
sortedEmails = collections.OrderedDict(sorted(emails.items(), key=lambda t: dateutil.parser.parse(str(t[1]['Date']))))

print "Deleting emails"
del emails

# j = 0
# while j<len(sortedEmails):
#  	j += 1
#  	if j%100 == 0:
#  		print j
# 	a = sortedEmails.popitem(last = False)
#  	print a[1]['Date']

	#date = sortedEmails[element]['Date']
	#date = unicode(str(date))
	#sortedEmails[element]['Date'] = date

print "Writing " + str(len(sortedEmails)) + " results"
writeResultsJSON(sortedEmails,__OUTPUT__)

print "Completed writing full emails"

j = 0
example = collections.OrderedDict()
while j<1000:
 	j += 1
 	if j%100 == 0:
 		print j
	a = sortedEmails.popitem(last = False)
	example[a[0]] = a[1]
 	
print "Writing example results"
writeResultsJSON(example,__EXAMPLES__)

print "Fin."