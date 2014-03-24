#!/usr/bin/env python
import os #import os module as it makes it easy to traverse dir structure
import collections

dictionaryOfFolders = {} #Unsorted dictionary
listOfEmployees = [] 
dictionaryOfEmailsInFolder = {}
numberOfEmailsAdded = 0

#Dictionary of format Folder Name - [Frequency of folder, Number of Emails in that folder]
def getFrequencyOfFolder(folderName):
  return dictionaryOfFolders[folderName][0]

def getNumberOfEmailsInFolder(folderName):
  return dictionaryOfFolders[folderName][1]

def setFrequencyOfFolder(folderName, frequency):
  dictionaryOfFolders[folderName][0] = frequency
  return

def setNumberOfEmailsInFolder(folderName, numberOfEmails):
  dictionaryOfFolders[folderName][1] = numberOfEmails
  return

i = 0
for root, dirs, files in os.walk("/Users/James/Documents/Enron Email Corpus/Edited Enron Email Dataset/maildir"):#,topdown=False):
  if i == 0:
    listOfEmployees = dirs #Dirty way of capturing employees. 

  if i%100 == 0:
    print i
  i = i+1

  if len(files) > 0:
    folder = str(root.rpartition("/")[-1]) #folder name by parsing root
    
    if folder in dictionaryOfFolders:
      setFrequencyOfFolder(folder,getFrequencyOfFolder(folder)+1)
      setNumberOfEmailsInFolder(folder,getNumberOfEmailsInFolder(folder)+len(files))
      numberOfEmailsAdded = numberOfEmailsAdded+len(files)
    else:
      dictionaryOfFolders[folder] = [1,len(files)]
      numberOfEmailsAdded = numberOfEmailsAdded+len(files)
  
for employee in listOfEmployees:
  if employee in dictionaryOfFolders:
    del dictionaryOfFolders[employee] #Could just del, but that would throw an error, will avoid.

print "Number of Emails Added:"
print numberOfEmailsAdded

sortedFolders = collections.OrderedDict(sorted(dictionaryOfFolders.items(), key=lambda t: t[1]))
print "Sorted User Defined Folders:"
print sortedFolders

results = open('SRI Analysis Results.txt', 'w+')
titles = "Folder\t Frequency of Occurence\t Emails in folder\n"
results.write(titles)
for element in sortedFolders:
  value = sortedFolders.popitem(False)
  folder = str(value[0])
  frequency = str(value[1][0])
  emails = str(value[1][1])
  formattedResults = folder + "\t" + frequency + "\t" + emails + "\n"
  results.write (formattedResults)
results.close()
