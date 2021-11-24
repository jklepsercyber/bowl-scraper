import os
import platform
import random
import sys
import json
import sqlite3
import re
from collections import defaultdict

def generate_sentence(mk_chain, count, start_word="") -> str:
    """
    Import a generated Markov chain as mk_chain', and the number of words you'd like to see as count.
    """

    punc = [',','.', '?', '!', '"']
    endpunc = ['.','?','!']

    # BIGRAM APPROACH: Capitalize your sentences ;)
    # word1 = random.choice(list(mk_chain.keys()))
    # sentence = word1.capitalize()
    # capitalize_flag = False

    # N-GRAM APPROACH: Make sure gen doesn't begin with punctuation!
    seq1 = ""
    firstchoice = []
    if len(start_word)>0:
        firstchoice = [i for i in mk_chain.keys() if start_word in i]
        firstchoice = [choice for choice in firstchoice if (not any (p in choice for p in punc))]
        if len(firstchoice)==0:
            firstchoice = list(mk_chain.keys())
    else:
        firstchoice = list(mk_chain.keys())
    while True:
        seq1 = random.choice(firstchoice)
        if not any(p in seq1[0] for p in punc):
            break
    sentence = seq1
    # count = count-3 # possibly, to be congruent with count input that user submits
    
    # N-GRAM APPROACH:
    gram_length = 2 # length is currently 2 because trigrams (2 words followed by a 3rd, picked word). This can be changed to anything!
    for i in range(count):
        # Handle exceptions, but keep generating.
        if (seq1 not in mk_chain.keys()): 
            print(f"EXCEPTION: Sequence \"{seq1}\" not in mk_chain.keys(). Ending sentence and picking new n-gram...")
            print(sentence)
            if not any (p in sentence[len(sentence)-1] for p in endpunc): # Finish sentence containing invalid n-gram
                sentence += random.choice(endpunc)
            while True:
                seq1 = random.choice(list(mk_chain.keys()))
                if not any(p in seq1[0] for p in punc):
                    break
            sentence += ' ' + seq1 # Add new chain to the sentence.
            print(sentence)
        
        # Generate the next word in the sentence, based off the current n-gram.
        possible_sequences = mk_chain[seq1]
        seq2 = possible_sequences[random.randrange(len(possible_sequences))]

        # Add new word to the sentence! Will handle unnecessary space created around punctuation later.
        sentence += ' ' + seq2

        # Figure out what the next n-gram to pick from should be!
        seq_words = sentence.split(' ')
        seq1 = ' '.join(seq_words[len(seq_words)-gram_length:len(seq_words)])

    # BIGRAM APPROACH:
    # for i in range(count-1):
    #     # Generate a second word, based off your Markov chain.
    #     try:
    #         word2 = random.choice(mk_chain[word1])
    #     except:
    #         word2 = random.choice(list(mk_chain.keys())) # happens if the last token was punctuation.

    #     word1 = word2 # setting the next word to be chained off of, on the next loop iteration.
        
    #     # Capitalize your sentences! ;)
    #     if (capitalize_flag):
    #         word2 = word2.capitalize()
    #         capitalize_flag = False

    #     # punctuate your sentences correctly!
    #     if not any (p in word2 for p in punc):
    #         word2 = ' ' + word2
    #     else:
    #         if word2 != ',' and word2 != '"':
    #             capitalize_flag = True
        
    #     sentence += word2

    #Capitalize first word, now that capitalizing stuff won't mess up n-gram lookups:
    sentence = sentence[0].capitalize() + sentence[1:]
    
    # Handle unneccesary spaces between words and punctuation
    sentence = re.sub(r'\s+([?.,!\"])', r'\1', sentence)

    # If the sentence doesn't already end in punctuation, end it with some!
    if not any (p in sentence[len(sentence)-1] for p in endpunc): # where seq2 was the last word added  
        if sentence[len(sentence)-1]==',':
            sentence = sentence[:len(sentence)-1] + "...(BowlScraper trails off.)"
            return sentence
        sentence += random.choice(endpunc)

    return sentence