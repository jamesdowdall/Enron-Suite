#!/usr/bin/env python

import email

def parseEmail(emailPath):
	headers = []
	body = ""
	try:
		message = open(emailPath)
		fileObject = email.message_from_file(message)
		headers = fileObject.items()
		body = fileObject.get_payload()
		message.close()
	except:
		print "Unexpected error, cannot read: " + emailPath
	struct = [headers,body]
	return struct

contents = parseEmail("/Users/James/Documents/Enron Email Corpus/Edited Enron Email Dataset/maildir/allen-p/all_documents/1.")
print contents[0]
print contents[1]