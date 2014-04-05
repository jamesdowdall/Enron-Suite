#!/usr/bin/env python
import email
import os
import json
import collections
import string

__DATASET__ = "/Users/James/Documents/Enron Email Corpus/Edited Enron Email Dataset/maildir/"
__OUTPUT__ = "/Users/James/Documents/Enron Email Corpus/EmailsJSON.json"

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

writeResultsJSON(emails,__OUTPUT__)
print "Fin."
return