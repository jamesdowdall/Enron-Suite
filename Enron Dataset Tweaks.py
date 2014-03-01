#!/usr/bin/env python
import os 
import os.path
import shutil

pathsOfEmailsToBeMoved = []
pathsofEmailsToBeRenamed = []

i = 0
for root, dirs, files in os.walk("/Users/James/Documents/Enron Email Corpus/Edited Enron Email Dataset/maildir"):
	if i%100 == 0:
		print i
  	i = i+1

  	#currentfolder = str(root.rpartition("/")[-1]) #folder name by parsing root
  	#parentfolderpath = str(root.rpartition("/")[0]) #folder name by parsing root)
  	
  	# if ".DS_Store" in files:
  	#	os.remove(root + "/.DS_Store")
  	#	print "Deleted .DS_Store"

	if ("_sent_mail" in dirs) and ("sent" in dirs): #Covers case if both present
		if "sent_mail" not in dirs:
			os.mkdir(root+"/sent_mail")
			print "Creating dir in: " + root
		pathsofEmailsToBeRenamed.append(root+"/_sent_mail")
		pathsofEmailsToBeRenamed.append(root+"/sent")

	elif ("_sent_mail" in dirs):	#Covers case when only _sent_mail is present (as AND case will have entered if both are present)
		if "sent_mail" not in dirs:	#Addresses case when _sent_mail is not present
			os.mkdir(root+"/sent_mail")
			print "Creating dir in: " + root
		pathsOfEmailsToBeMoved.append(root+"/_sent_mail")

	elif ("sent" in dirs): 			#Covers case when only sent is present (as AND case will have entered if both are present)
		if "sent_mail" not in dirs:	#Addresses case when _sent_mail is not present
			os.mkdir(root+"/sent_mail")
			print "Creating dir in: " + root
		pathsOfEmailsToBeMoved.append(root+"/sent")


	#if ((currentfolder == "_sent_mail") or (currentfolder == "_sent_mail")):
	#	new = parentfolderpath + "/sent_mail/"
	#	if os.path.isdir(new): #If the /sent_mail folder exists, rename current files

	#	else: #If /sent_mail does not exist, create new folder and move across
	#		os.mkdir(new)
		
		#Rename files
	#	os.renames(currentfolder,new)


		
	#	if "sent_mail" in dirs: #If the sent_mail directory is also present, copy files across then remove old dir
	#		for email in files:
	#			src = old + email
	#			shutil.move(src,new)
	#			_sent_mail_renames = _sent_mail_renames + 1
	#		shutil.rmtree(old)
	#	else: #If sent_mail directory is not present, 


	#if "sent" in dirs:
	#	old = root + "/sent/"
		# new = root + "/sent_mail/"
		# if "sent_mail" in dirs: #If the sent_mail directory is also present, copy files across then remove old dir
		# 	for email in files:
		# 		src = old + email
		# 		shutil.move(src,new)
		# 		sent_renames = sent_renames + 1
		# 	shutil.rmtree(old)
		# else:
		# 	print root
		# 	os.renames(old,new)
		# 	sent_renames = sent_renames + 1

#print "Paths of Emails to be Renamed prior to renaming:"
#print pathsofEmailsToBeRenamed

print "Length of Paths of Emails to be Renamed: " + str(len(pathsofEmailsToBeRenamed))
print "Length of Paths of Emails to be Moved prior to renaming: " + str(len(pathsOfEmailsToBeMoved))

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
	#pathsofEmailsToBeRenamed.remove(folders)

#print "Paths of Emails to be Renamed post renaming:"
#print pathsofEmailsToBeRenamed

print "Length of Paths of Emails to be Moved post renaming: " + str(len(pathsOfEmailsToBeMoved))

print "Paths of Emails to be Moved:"
print pathsOfEmailsToBeMoved
