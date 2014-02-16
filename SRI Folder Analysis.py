#!/usr/bin/env python
#Run this from the top level directory (maildir)
import os #import os module as it makes it easy to taverse dir structure
import collections

#Dictionary of format Folder Name - [Frequency of folder, Number of Emails in that folder]
def getFrequencyOfFolder(folderName):
  print dictionaryOfFolders[folderName][0]
  return dictionaryOfFolders[folderName][0]

def getNumberOfEmailsInFolder(folderName):
  print dictionaryOfFolders[folderName][1]
  return dictionaryOfFolders[folderName][1]

def setFrequencyOfFolder(folderName, frequency):
  print "Setting frequency of folder: " + folderName + " to: " + frequency
  dictionaryOfFolders[folderName][0] = frequency
  return

def setNumberOfEmailsInFolder(folderName, numberOfEmails):
  print "Setting NumberOfEmailsInFolder of folder: " + folderName + " to: " + frequency
  dictionaryOfFolders[folderName][1] = numberOfEmails
  return

#Initialise folder method?

#TODO: Change data structure of dictionaryOfFolders from folderName > frequency, to Folder Name - [Frequency of folder, Number of Emails in that folder]

dictionaryOfFolders = {} #Unsorted dictionary
listOfEmployees = [] 
dictionaryOfEmailsInFolder = {}

i = 0
for root, dirs, files in os.walk("/Users/James/Documents/Enron Email Corpus/Base Enron Email Dataset"):#,topdown=False):
  if i == 1:
    listOfEmployees = dirs #Dirty way of capturing employees. 2nd Dirs is at the correct level in the file tree.

  #if i%100 == 0:
  #  print i
  i = i+1

  print root
  print files
  print len(files)

  for directory in dirs:
    if directory in dictionaryOfFolders:
      dictionaryOfFolders[directory] = dictionaryOfFolders[directory]+1
    else:
      dictionaryOfFolders[directory] = 1

for employee in listOfEmployees:
  if employee in dictionaryOfFolders:
    del dictionaryOfFolders[employee] #Could just del, but that would throw an error, will avoid.

sortedFolders = collections.OrderedDict(sorted(dictionaryOfFolders.items(), key=lambda t: t[1]))
print "Sorted User Defined Folders:"
print sortedFolders