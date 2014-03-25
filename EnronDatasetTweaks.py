#!/usr/bin/env python
import os 
import os.path
import shutil

__DATASETLOCATION__ = "/Users/James/Documents/Enron Email Corpus/Edited Enron Email Dataset/maildir/"

i = 0
for root, dirs, files in os.walk(__DATASETLOCATION__):

	if len(files) > 0:
		for email in files:
			i += 1
			if i%1000 == 0:
				print i

			oldName = root + "/" + email
			newName = root + "/" + str(i)
			os.rename(oldName,newName)

print "All files renamed"

pathsOfEmailsToBeMoved = []

i = 0
for root, dirs, files in os.walk(__DATASETLOCATION__):
	i += 1
	if i%100 == 0:
		print i

	foldersAdded = 0	

	if ("sent_items" in dirs): 
		pathsOfEmailsToBeMoved.append(root+"/sent_items")
		foldersAdded = foldersAdded + 1

	if ("_sent_mail" in dirs):
		pathsOfEmailsToBeMoved.append(root+"/_sent_mail")
		foldersAdded = foldersAdded + 1

	if ("sent" in dirs):
		pathsOfEmailsToBeMoved.append(root+"/sent")
		foldersAdded = foldersAdded + 1

	if "sent_mail" not in dirs and foldersAdded > 0:
		os.mkdir(root+"/sent_mail")

print "Length of Paths of Emails to be Moved: " + str(len(pathsOfEmailsToBeMoved))

i = 0
for folders in pathsOfEmailsToBeMoved:
	i = i+1
	if i%10 == 0:
		print i
	root = str(folders.rpartition("/")[0])
	newName = root + "/sent_mail"
	files = os.listdir(folders)
	for email in files:
		source = folders + "/" + email
		destination = newName + "/"+ email
		shutil.move(source,destination)

print "Files Moved."