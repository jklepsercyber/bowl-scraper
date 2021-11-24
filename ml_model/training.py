import os
import platform
import random
import sys
import json
import sqlite3
import re
from collections import defaultdict

def sentence_dump():
    """
    Dump all message data from bowl-data.db, and clean it into a list of sentences that can be fed into the Markov chain.
    """
    #retrieve SQL database
    bowldb = sqlite3.connect('./saved-data/bowl-data.db')
    try:
        cursor = bowldb.cursor()
        print("Connected to db!")
    except:
        return("Unable to connect to db.")
    cursor.execute('SELECT * FROM main')
    table = cursor.fetchall()

    sentences = []
    #store Discord message data locally before cleaning
    for line in table:
        #print(line[0]) #prints username who sent following message
        sentences.append(line[1])

    i = 0
    while i < len(sentences):
        sentence = sentences[i]
        if "https" in sentence: # handle URLs
            sentences.pop(i)
            i=i-1 # make sure we don't miss any sentences
            continue
        # Regex magic coming right up!
        sentence = re.sub(r'<.*>', '', sentence)
        sentence = re.sub(r'[:]', ' ', sentence) # replace colons that follow a character with spaces
        sentence = re.sub(r'[;]', ' ,', sentence) # generalize semicolons as commas
        sentence = re.sub(r'[^a-zA-Z0-9_\?\.\!\s\',%\+\-&\$/]', '', sentence)
        sentence = re.sub(r'[\.]{3,}', ' ', sentence) # typically comes from discord splitting messages
        sentence = re.sub(r'[\-]{2,}', '', sentence) # handle sentence cutoff dashes
        # Time to deal with newline characters
        sentence = re.sub(r'([?.,!\"\'\s]{1,})+\n{1,}', r'\1' + ' ', sentence) # If punctuation before newline chars
        sentence = re.sub(r'\n{1,}', '. ', sentence) 
        sentence.lstrip() # remove leading whitespace
        
        # Last chance to pop any empty sentences and prevent extraneous additions after regex magic...
        if len(sentence)==0 or not any(char.isalpha() or char.isdigit() for char in sentence[0:3]):
            print(f"Popping \"{sentence}\" ---- Invalid Sentence Found!")
            sentences.pop(i)
            i=i-1 # make sure we don't miss sanitizing any sentences
            continue
        # Let's help further refine the Markov chain by clearly defining end of sentences.
        if not any (p in sentence for p in [".","!","?"]) or not any (p in sentence[len(sentence)-1] for p in [".","!","?"]): 
            sentence = sentence+"."

        sentences[i] = sentence # add sentence to list!
        i=i+1

    return sentences

def markov_chain(text_data):
    """
    Create a Markov Chain state dictionary from a list of words.
    """
    words = []
    # Tokenize sentences into words!
    for sentence in text_data:
        # We need punctuation to be recognized as individual tokens to end sentences better.
        sentence = re.sub(r',', ' ,', sentence) 
        sentence = re.sub(r'[\?]', ' ?', sentence) 
        sentence = re.sub(r'[\.]', ' .', sentence) 
        sentence = re.sub(r'[\!]', ' !', sentence) 
        sentence = re.sub(r'[\"]', ' \" ', sentence) 
        words = words+sentence.split(' ')
    words = list(filter(None, words)) # remove empty words from list 

    markov_dict = defaultdict(list)
    # BIGRAM APPROACH
    # for current_word, next_word in zip(words[0:-1], words[1:]):
    #     # only append to Markov chain does not contain, or is not a sentence ending character
    #     # commas and quotations not included in that for sentence continuity's sake
    #     if not any (p in current_word for p in [".","!","?"]):
    #         markov_dict[current_word].append(next_word) 

    # N-GRAM APPROACH
    gram_length = 2 # length is 2 because trigrams (2 words followed by a 3rd, picked word). This can be changed to anything!
    i = 0
    while i < len(words)-gram_length:
        # Handle adjacent punctuation
        while not words[i][0].isalnum() and words[i]==words[i+1]: # FIX THIS TO BE COMPATIBLE WITH ANY N-GRAM
            print(f"Adjacent punctuation found in {words[i:i+gram_length]}: popping one {words[i+1]}") 
            words.pop(i+1)

        while not (words[i+(gram_length-1)][0].isalnum() or words[i+gram_length][0].isalnum()):
            print(f"Punctuation found in last 2 indices of n-gram at \"\"{words[i:i+gram_length]} : {words[i+gram_length]} \"\" ... Popping one {words[i+gram_length]}")
            words.pop(i+gram_length) 
            print(f"{words[i:i+gram_length]} : {words[i+gram_length]}")   

        seq = ' '.join(words[i:i+gram_length])
        if seq not in markov_dict.keys():
            markov_dict[seq] = [] # Establish entry in markov_dict for this trigram

        markov_dict[seq].append(words[i+gram_length])
        i=i+1
        
    # transform back to normal dictionary  
    markov_dict = dict(markov_dict)
   
    # write to JSON file for better access
    with open('./markov_dict.json', 'w') as file:
        json.dump(markov_dict, file, indent=4, sort_keys=True)
        print("\nWrote markov file!")
    return markov_dict