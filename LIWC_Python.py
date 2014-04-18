#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import os.path
import re
from collections import Counter
from collections import OrderedDict
import json # as json
import csv

__LIWC__ = "/Users/James/Documents/Enron Email Corpus/LIWC/"
__INPUT__ = __LIWC__ + "Input/"
__OUTPUT__ = __LIWC__ + "Output/"

word_re = re.compile(r"[a-z]['a-z]*")

categories = ['funct', 'pronoun', 'ppron', 'i', 'we', 'you', 'shehe', 'they', 'ipron', 'article', 'verb', 'auxverb', 'past', 'present', 'future', 'adverb', 'preps', 'conj', 'negate', 'quant', 'number', 'swear', 'social', 'family', 'friend', 'humans', 'affect', 'posemo', 'negemo', 'anx', 'anger', 'sad', 'cogmech', 'insight', 'cause', 'discrep', 'tentat', 'certain', 'inhib', 'incl', 'excl', 'percept', 'see', 'hear', 'feel', 'bio', 'body', 'health', 'sexual', 'ingest', 'relativ', 'motion', 'space', 'time', 'work', 'achieve', 'leisure', 'home', 'money', 'relig', 'death', 'assent', 'nonfl', 'filler']

# print open('/usr/local/data/liwc_2007.trie').read()
_trie = json.load(open(__LIWC__ + 'LIWC_trie.txt'))

def _walk(token, i, cursor):
    if '*' in cursor:
        return True, cursor['*']
    if '$' in cursor and i == len(token):
        return True, cursor['$']
    if i < len(token):
        letter = token[i]
        if letter in cursor:
            return _walk(token, i + 1, cursor[letter])
    return False, None


def from_tokens(tokens):
    counts = dict.fromkeys(categories + ['Dic'], 0)
    for token in tokens:
        success, cats = _walk(token, 0, _trie)
        if success:
            for category in cats:
                counts[category] += 1
            counts['Dic'] += 1

    return counts

# full analysis variables below:

full_columns = ['WC', 'WPS', 'Sixltr', 'Dic', 'Numerals'] + categories + ['Period', 'Comma', 'Colon', 'SemiC', 'QMark', 'Exclam', 'Dash', 'Quote', 'Apostro', 'Parenth', 'OtherP', 'AllPct']

punctuation = [
    ('Period', '.'),
    ('Comma', ','),
    ('Colon', ':'),
    ('SemiC', ';'),
    ('QMark', '?'),
    ('Exclam', '!'),
    ('Dash', '-'), # –—
    ('Quote', '"'), # “”
    ('Apostro', "'"), # ‘’
    ('Parenth', '()[]{}'),
    ('OtherP', '#$%&*+-/<=>@\\^_`|~')
]

def from_text(text):
    text = text.lower()
    tokens = word_re.findall(text)
    # tokens = [token for token in re.split(r'\b', text) if token != '' and token != None]
    # tokens = re.split(r'\b\W+\b', text)
    # tokens = re.findall(r"(\w|')+", text)
    wc = max(len(tokens), 1)
    sentence_count = max(len(re.findall(r"[.!?]+", text)), 1)

    counts = {'WC': wc, 'WPS': wc / float(sentence_count),
        'Sixltr': len([1 for token in tokens if len(token) > 6]),
        'Numerals': len([1 for token in tokens if token.isdigit()])}

    category_counts = from_tokens(tokens)
    counts.update(category_counts)

    character_counts = Counter(text)
    for name, chars in punctuation:
        counts[name] = sum(character_counts[char] for char in chars)
    counts['Parenth'] = counts['Parenth'] / 2.0
    counts['AllPct'] = sum(counts[name] for name, _ in punctuation)

    for column in full_columns[2:]:
        counts[column] = float(counts[column]) / wc

    return counts

def print_liwc_results(filename,counts):
    line = ''
    values = ['%d' % counts['WC'], '%0.2f' % counts['WPS']] + \
        ['%0.2f' % (counts[column] * 100) for column in full_columns[2:]]    
    if (int(counts['WC']) >= 1): #If one or more words? - this may not be correct (doesn't deal with emails of 0 body length)
        for col, val in zip(full_columns, values):
            # print '%16s %s' % (col, val)
            line += `val` + ','
        if not os.path.exists(__OUTPUT__):
            os.makedirs(__OUTPUT__)
        f = open(__OUTPUT__ + filename,'w') #This should be moved to not be dependent 
        mappings = OrderedDict(zip(full_columns,values))
        json.dump(mappings,f)
        # Write headers to CSV
        # writer = csv.writer(f,dialect='excel')
        # writer.writerow(full_columns)
        # Write data to CSV
        # f.write("" + line.replace("'","")+'\n')
        f.close()
        #write to DB too

print("!")

# print "Len full_columns: " + str(len(full_columns))
# print "Len categories: " + str(len(categories))
# print categories
# print "Len categories[:-1]: " + str(len(categories[:-1]))
# print categories[:-1]
# print "Rest of full_columns: 17"
i = 0
for filename in os.listdir(__INPUT__):
    i += 1
    if i%1000 == 0: #No of files processed
        print i
    #if (not os.path.exists(__OUTPUT__+filename)): #Only update if files do not exist.
    if (filename != ".DS_Store"):
        linestring = open(__INPUT__+filename).read()
        messages = linestring.split('#SEG#')
        for message in messages:
            counts = from_text(`message`)
            print_liwc_results(filename,counts)

# filename = "1198"
# linestring = open(__INPUT__+ filename).read()
# messages = linestring.split('#SEG#')
# for message in messages:
#     i = i+1
#     if i%1000 == 0: #No of files processed
#         print i
#     counts = from_text(`message`)
#     print_liwc_results(filename,counts)

