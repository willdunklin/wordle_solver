from numpy import Infinity, log2
import json
import os
import random
from pathlib import Path

words = [word.strip() for word in list(open('words_freq.txt'))]
def score_fn(max_freq: int) -> dict:
    scores = {}
    for x in range(max_freq):
        scores[x] = x * log2(x+1)
    return scores
scores = score_fn(len(words))

def lookup_path(parent_path, word):
    return f'lookup/{parent_path}{word}.json'

def percent(x, total):
    return f'{round(100*x/total, 1)}%'

def wordle_str(guess: str, word: str): 
    wordle_string = ['g', 'g', 'g', 'g', 'g']
    word = [char for char in word]
    for i in range(len(guess)):
        if guess[i] == word[i]: # green case  (consume letter in word)
            word[i] = '*'
        elif guess[i] in word:  # yellow case (consume letter in word)
            word[word.index(guess[i])] = '*'
            wordle_string[i] = 'y'
        else:                   # gray case   (don't cosume)
            wordle_string[i] = '*'

    return wordle_string

# string of wordle response: len 5, of chars 'gy*' 
def wordle_str_hash(wordle_string) -> int:    
    word_hash = 0
    three_pows = [1, 3, 9, 27, 81]
    for x, char in zip(three_pows, wordle_string):
        if char == 'g':
            word_hash += x * 2
        elif char == 'y':
            word_hash += x
    return word_hash

def wordle_hash(guess: str, word: str) -> int:
    return wordle_str_hash(wordle_str(guess, word))

def get_input(best_word, min_score):
    game_response = input(f'{best_word}, {min_score}, (respond in the form yg*** [where *=grey, y=yellow, g=green]): ')

    if len(game_response) != 5:
        print('    ERROR: game response length not 5')
        get_input(best_word, min_score)

    if not all(letter in 'gy*' for letter in game_response):
        print('    ERROR: response must solely consist of chars \'gy*\'')
        get_input(best_word, min_score)
    
    return game_response

def eliminate_words(viable_words: list, best_word: str, min_score: float, filter_str: str, debug: str='pw'):
    global words, scores

    filter_str_hash = wordle_str_hash(filter_str)
    viable_words = [word for word in viable_words if filter_str_hash == wordle_hash(best_word, word)]

    if len(viable_words) <= 1:
        return viable_words, best_word, min_score

    for i, guess in enumerate(words):
        # if "p" debug flag is set, print [p]ercentage completion
        if i % 1000 == 999 and 'p' in debug: 
            # if "r" debug flag set, only print percent [r]arely 
            if 'r' not in debug or random.random() < (1/4):
                print(f'  {percent(i, len(words))}')

        freq_table = [0] * 3**5
        for word in viable_words:
            freq_table[wordle_hash(guess, word)] += 1

        score = sum(map(lambda x: scores[x], freq_table[:-1]))

        if score < min_score:
            min_score = score
            best_word = guess
            # if "w" in debug flag, print new best [w]ord
            if 'w' in debug:
                print(f'! {min_score}@{best_word}')

    return best_word, min_score, viable_words

def play():
    global words

    parent_path = ''
    viable_words = words
    best_word = 'tares' # '?????'
    min_score = Infinity

    for _ in range(6):
        response = get_input(best_word, min_score)
        if(Path(lookup_path(parent_path, best_word)).is_file()):
            best_word, min_score, viable_words = read_variations(parent_path, best_word)[response]
        else:
            best_word, min_score, viable_words = eliminate_words(viable_words, best_word, min_score, filter_str=response)

        parent_path += f'{best_word}/'

        if len(viable_words) == 0:
            print('Ran out of words in dictionary. Incorrect filter strings')
            break
        elif len(viable_words) == 1:
            print(f'\nFound answer: {viable_words[0]}')
            break
        else:
            print(f'Best guess: {best_word}')
            if len(viable_words) <= 10:
                print(f'    There were <10 options: {viable_words}')

def make_tree(start_viable_words, parent_path, start_word='tares', min_score=Infinity):
    viable_words = start_viable_words
    best_word = start_word

    log_path = lookup_path(parent_path, start_word)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    with open(log_path, 'w') as file:
        info_dict = {}
        for i in range(3**5):
            tmp = i
            filter_str = ''
            for _ in range(5):
                filter_str += '*yg'[tmp%3]
                tmp //= 3

            print(f'{start_word}:', filter_str, f'[{percent(i, 3**5)}]')

            word, score, v_words = eliminate_words(viable_words, best_word, min_score, filter_str, debug='pr')

            info_dict[filter_str] = [word, score if score != Infinity else 9999999, v_words]
        file.write(json.dumps(info_dict))

def read_variations(parent_path: str, name: str) -> dict:
    with open(lookup_path(parent_path, name)) as file:
        data = '\n'.join(file.readlines())
        info_dict = json.loads(data)

        return info_dict  

if __name__ == '__main__':
    # play()
    base_word = 'tares'
    parent_path = ''

    replace = False
    base_vars = read_variations(parent_path, base_word)

    parent_path += f'{base_word}/'
    for filter_str, variation in base_vars.items():
        word, score, viable_words = variation
        
        print(f'{filter_str} {word} {score} {viable_words[:10]}...{len(viable_words)}')
        skip = '' #input()
        if len(skip) > 0:
            continue

        # don't overwrite
        if(not replace and Path(lookup_path(parent_path, word)).is_file()):
            continue

        if len(viable_words) <= 1:
            input('length of viable words <= 1')
            continue
        
        make_tree(start_viable_words=viable_words, parent_path=parent_path, start_word=word, min_score=score)
    # print(read_variation('', 'tares', '*gg**'))