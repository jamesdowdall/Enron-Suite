#!/usr/bin/env python
import os 
import shutil

i = 0
_sent_mail_renames = 0
sent_renames = 0
for root, dirs, files in os.walk("/Users/James/Documents/Enron Email Corpus/Edited Enron Email Dataset/maildir"):
	if i%100 == 0:
		print i
  	i = i+1

  	folder = str(root.rpartition("/")[-1]) #folder name by parsing root

  	#if ".DS_Store" in files:
  	#	os.remove(root + "/.DS_Store")
  	#	print "Deleted .DS_Store"

	if "_sent_mail" in dirs:
		old = root + "/_sent_mail/"
		new = root + "/sent_mail/"
		if "sent_mail" in dirs: #If the sent_mail directory is also present, copy files across then remove old dir
			for email in files:
				src = old + email
				shutil.move(src,new)
				_sent_mail_renames = _sent_mail_renames + 1
			shutil.rmtree(old)
		else: #If sent_mail directory is not present, 
			os.renames(old,new)
			_sent_mail_renames = _sent_mail_renames + 1

	if "sent" in dirs:
		old = root + "/sent/"
		new = root + "/sent_mail/"
		if "sent_mail" in dirs: #If the sent_mail directory is also present, copy files across then remove old dir
			for email in files:
				src = old + email
				shutil.move(src,new)
				sent_renames = sent_renames + 1
			shutil.rmtree(old)
		else:
			print root
			os.renames(old,new)
			sent_renames = sent_renames + 1

print "_sent_mail renamed to sent_mail " + str(_sent_mail_renames) + " times"
print "sent renamed to sent_mail " + str(sent_renames) + " times"
