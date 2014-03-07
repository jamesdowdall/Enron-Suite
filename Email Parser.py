#!/usr/bin/env python
import email
import os

def parseEmail(emailPath):
	try:
		message = open(emailPath)
	except:
		print "Failed to open: " + emailPath
	fileObject = email.message_from_file(message)
	headers = fileObject.items()
	body = fileObject.get_payload()
	message.close()	

	struct = [headers,body]
	return struct

# contents = parseEmail("/Users/James/Documents/Enron Email Corpus/Edited Enron Email Dataset/maildir/allen-p/all_documents/1.")
# print contents[0]
# print contents[1]

collatedHeaders = []
i = 0
for root, dirs, files in os.walk("/Users/James/Documents/Enron Email Corpus/Edited Enron Email Dataset/maildir"):

	if len(files) > 0:
		for element in files:
			i = i+1
			if i%1000 == 0:
				print i
			filePath = root + "/" + element
			data = parseEmail(filePath)
			headers = data[0]
			for header in headers:
				if header[0] not in collatedHeaders:
					collatedHeaders.append(header[0])
print collatedHeaders