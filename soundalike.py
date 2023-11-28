from Levenshtein import distance as levenshtein_distance
import random
import os
import nltk
from nltk.corpus import cmudict

nltk.download('cmudict')
cmu_dict = cmudict.dict()

BOT_TOKEN = os.environ.get('BOT_TOKEN')

# Don't change above

def phonetic_representation(word):
    """Return the phonetic representation of a word using the CMU Pronouncing Dictionary."""
    try:
        return cmu_dict[word.lower()][0]  # Using the first pronunciation
    except KeyError:
        return word  # Word not found in the dictionary
    
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

def clean_word(word):
    return re.sub(r'[^\w\s]', '', word)

def generate_random_sentence(sentence, threshold=.75):
    words = sentence.split()
    cleaned_words = [clean_word(word) for word in words]
    alternatives = [find_other_words(word, threshold) for word in cleaned_words]
    
    # Ensure each list of alternatives includes the cleaned word
    for i, word in enumerate(cleaned_words):
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

# Bot part:
import re
import telebot
import string

bot = telebot.TeleBot(BOT_TOKEN)

# Function to remove inter-word punctuation
def remove_inter_word_punctuation(text):
    return re.sub(r'(?<=\s)[{0}]|[{0}](?=\s)'.format(re.escape(string.punctuation)), '', text)

# Function to find inter-word punctuation in a sentence
def find_inter_word_punctuation(text):
    punctuation_positions = [(i, char) for i, char in enumerate(text.split()) if char in string.punctuation]
    return punctuation_positions

# Function to reinsert punctuation into a sentence at word level
def reinsert_punctuation_at_word_level(sentence, punctuation_positions):
    words = sentence.split()
    for pos, punct in punctuation_positions:
        if pos < len(words):
            words.insert(pos, punct)
    return ' '.join(words)

# Function to match the capitalization of the original text
def match_capitalization(source, target):
    result = []
    for s_word, t_word in zip(source.split(), target.split()):
        if s_word.istitle():
            result.append(t_word.capitalize())
        else:
            result.append(t_word.lower())
    return ' '.join(result)

# Handler for any text message
@bot.message_handler(func=lambda message: True)
def generate_alternative(message):
    try:
        original_text = message.text
        punctuation_positions = find_inter_word_punctuation(original_text)
        cleaned_text = remove_inter_word_punctuation(original_text)
        generated_sentence = generate_random_sentence(cleaned_text.lower(), 0.65)
        final_response = match_capitalization(original_text, generated_sentence)
        final_response_with_punct = reinsert_punctuation_at_word_level(final_response, punctuation_positions)
        bot.send_message(message.chat.id, final_response_with_punct)
    except Exception as e:
        bot.send_message(message.chat.id, "Error: " + str(e))

# Polling the bot to keep it running
bot.polling()
