import os
import sys
import json
sys.path.append('./')
# import nltk
# nltk.download('punkt') if NLTK throws an error, add this back in for one run.

#GitHub module imports
from ml_model.training import *
from ml_model.markov_gen import *

def main():
    # print("Markov Generation Test:")
    # print(" ")
    # print("--------------------------")
    # print("Now Generating Sentences...:")
    # print(" ")
    # sentence_data = sentence_dump()
    # print(" ")
    # print("--------------------------")
    # print("Now Generating Markov Chain...:")
    # print(" ")
    # new_chain = markov_chain(sentence_data)
    # print("--------------------------")
    # print("Word List:")
    # print(" ")
    # for word in new_chain:
    #     print(f"{word} : {new_chain[word]}")
    # print(" ")
    # print("--------------------------")
    # print(" ")
    with open ('./markov_dict.json', 'r') as file:
       new_chain = json.load(file)
    print(generate_sentence(new_chain, 50, ""))
    print("--------------------------")
    print(generate_sentence(new_chain, 125, "of Reddit"))
    print("--------------------------")
    print(generate_sentence(new_chain, 100, "Reddit"))
    print("--------------------------")
    print(generate_sentence(new_chain, 120, "Ceaseless"))
    print("--------------------------")
    print(generate_sentence(new_chain, 140, "Bed of"))
    print("--------------------------")
    print(generate_sentence(new_chain, 100, ""))
    print(" ")

main()

