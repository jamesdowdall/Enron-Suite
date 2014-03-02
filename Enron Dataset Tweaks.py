#!/usr/bin/env python
import os 
import os.path
import shutil

pathsOfEmailsToBeMoved = []
pathsofEmailsToBeRenamed = []

i = 0
for root, dirs, files in os.walk("/Users/James/Documents/Enron Email Corpus/Edited Enron Email Dataset/maildir"):
	i = i+1
	if i%100 == 0:
		print i

	#Deal with sent_items case

	if ("_sent_mail" in dirs) and ("sent" in dirs): #Covers case if both present
		if "sent_mail" not in dirs:
			os.mkdir(root+"/sent_mail")
		pathsofEmailsToBeRenamed.append(root+"/_sent_mail")
		pathsofEmailsToBeRenamed.append(root+"/sent")

	elif ("_sent_mail" in dirs):	#Covers case when only _sent_mail is present (as AND case will have entered if both are present)
		if "sent_mail" not in dirs:	#Addresses case when _sent_mail is not present
			os.mkdir(root+"/sent_mail")
		pathsOfEmailsToBeMoved.append(root+"/_sent_mail")

	elif ("sent" in dirs): 			#Covers case when only sent is present (as AND case will have entered if both are present)
		if "sent_mail" not in dirs:	#Addresses case when _sent_mail is not present
			os.mkdir(root+"/sent_mail")
		pathsOfEmailsToBeMoved.append(root+"/sent")


print "Length of Paths of Emails to be Renamed: " + str(len(pathsofEmailsToBeRenamed))
print "Length of Paths of Emails to be Moved prior to renaming: " + str(len(pathsOfEmailsToBeMoved))

#Rename files in cases where there are several folders, add paths to list of files to be moved
for folders in pathsofEmailsToBeRenamed:
	files = os.listdir(folders)
	folderName = str(folders.rpartition("/")[-1]) #folder name by parsing root
	for email in files:
		if (folderName == "_sent_mail"):
			oldName = folders + "/" + email
			newName = folders + "/A" + email
			os.rename(oldName,newName)
		
		elif (folderName == "sent"):
			oldName = folders + "/" + email
			newName = folders + "/B" + email
			os.rename(oldName,newName)
		
		else:
			print "folderName not recognised: " + folderName

	pathsOfEmailsToBeMoved.append(folders)

print "Length of Paths of Emails to be Moved post renaming: " + str(len(pathsOfEmailsToBeMoved))

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