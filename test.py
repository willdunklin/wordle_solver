from numpy import Infinity, log2
import json
from pathlib import Path

words = [word.strip() for word in list(open('words_freq.txt'))]
def score_fn(max_freq: int) -> dict:
    scores = {}
    for x in range(max_freq):
        scores[x] = x * log2(x+1)
    return scores
scores = score_fn(len(words))


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

def eliminate_words(viable_words: list, best_word: str, min_score: float, filter_str: str):
    global words, scores

    filter_str_hash = wordle_str_hash(filter_str)
    viable_words = [word for word in viable_words if filter_str_hash == wordle_hash(best_word, word)]

    if len(viable_words) <= 1:
        return viable_words, best_word, min_score

    for i, guess in enumerate(words):
        if i % 1000 == 999: 
            print(f'  {round(100*i/len(words), 1)}%')

        freq_table = [0] * 3**5
        for word in viable_words:
            freq_table[wordle_hash(guess, word)] += 1

        score = sum(map(lambda x: scores[x], freq_table[:-1]))

        if score < min_score:
            min_score = score
            best_word = guess
            print(f'! {min_score}@{best_word}')

    return viable_words, best_word, min_score

def play():
    global words

    parent_path = ''
    viable_words = words
    best_word = 'tares' # '?????'
    min_score = Infinity

    for _ in range(6):
        response = get_input(best_word, min_score)
        if(Path(f'lookup/{parent_path}{best_word}.json').is_file()):
            best_word, min_score, viable_words = read_variation(parent_path, best_word, response)
        else:
            viable_words, best_word, min_score = eliminate_words(viable_words, best_word, min_score, filter_str=response)

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

def make_tree(start_viable_words, parent_path, start_word='tares'):
    viable_words = start_viable_words
    best_word = start_word
    min_score = Infinity

    with open(f'lookup/{parent_path}{start_word}.json', 'w') as file:
        info_dict = {}
        for i in range(3**5):
            filter_str = ''
            for _ in range(5):
                filter_str += '*yg'[i%3]
                i //= 3

            # print(f'testing string {filter_str}')
            v, b, m = eliminate_words(viable_words, best_word, min_score, filter_str)
            # print(b, m, v)
            info_dict[filter_str] = [b, m if m != Infinity else 9999999, v]
        file.write(json.dumps(info_dict))

def read_variation(parent_path: str, name: str, filter_str: str):
    with open(f'lookup/{parent_path}{name}.json') as file:
        data = '\n'.join(file.readlines())
        info_dict = json.loads(data)

        return info_dict[filter_str]    

if __name__ == '__main__':
    play()
    # make_tree(words, parent_path='')
    # print(read_variation('', 'tares', '*gg**'))