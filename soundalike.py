from Levenshtein import distance as levenshtein_distance
import random
import pandas as pd
import os
import nltk
from nltk.corpus import cmudict

BOT_TOKEN = os.environ.get('BOT_TOKEN')
nltk.download('cmudict')
cmu_dict = cmudict.dict()

def phonetic_representation(word):
    """Return the phonetic representation of a word using the CMU Pronouncing Dictionary."""
    try:
        return cmu_dict[word.lower()][0]  # Using the first pronunciation
    except KeyError:
        return None  # Word not found in the dictionary
    
def phonetic_similarity(phonetics1, phonetics2):
    """Calculate a similarity measure between two phonetic representations considering the sequence order."""
    lev_distance = levenshtein_distance(phonetics1, phonetics2)
    max_length = max(len(phonetics1), len(phonetics2))
    return 1 - (lev_distance / max_length) if max_length != 0 else 0

def find_other_words(original_word, threshold = .75, max_matches = 5):
    matches = []
    phonetics = phonetic_representation(original_word)

    for word, pron in cmu_dict.items():
        similarity = phonetic_similarity(phonetics, pron[0])
        if similarity >= threshold and word not in matches and len(matches) < max_matches and word != original_word:
            matches.append(word)
    return matches

def generate_random_sentence(sentence, threshold=.75):
    alternatives = [find_other_words(word, threshold) for word in sentence.split()]
    
    # Ensure each list of alternatives includes the original word
    for i, word in enumerate(sentence.split()):
        if word not in alternatives[i]:
            alternatives[i].append(word)

    # Generate all possible combinations
    def generate_combinations(prefix, i):
        if i == len(alternatives):
            yield ' '.join(prefix)
            return
        for word in alternatives[i]:
            yield from generate_combinations(prefix + [word], i + 1)

    # Create a list of all combinations and choose one randomly
    all_combinations = list(generate_combinations([], 0))
    return random.choice(all_combinations)

import telebot

# Initialize the bot with your token
bot = telebot.TeleBot(BOT_TOKEN)

# Handler for any text message
@bot.message_handler(func=lambda message: True)
def generate_alternative(message):
    try:
        response = generate_random_sentence(message.text.lower(), 0.65)
        bot.reply_to(message, response)
    except Exception as e:
        bot.reply_to(message, "Error: " + str(e))

# Polling the bot to keep it running
bot.polling()
