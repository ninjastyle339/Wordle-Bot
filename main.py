from pynput.keyboard import Key, Controller
import time

with open("wordle-answers-list.txt") as f:
    WORD_LIST = [w.strip().lower() for w in f]

def filter_words(words, guess, result):
    #words is the list of words left (initially full)
    #guess is the previous guess we made
    #user reports back by typing a 5 letter combination of gyr
    #example: ggyyr ->first two letters are green followed by two
    #yellow letters and then gray letter at the end
    #based on this we can filter out our word list
    filtered_words = []
    
    count1 = {}
    exact_count = {}
    for i, letter in enumerate(guess):
        if result[i] == 'g' or result[i] == 'y':
            if letter not in count1:
                count1[letter] = 0
            count1[letter] += 1
    for i, letter in enumerate(guess):
        if result[i] == 'r' and letter in count1:
            exact_count[letter] = count1[letter]
    for word in words:
        valid = True
        count2 = {}
        for i, letter in enumerate(word):
            if letter not in count2:
                count2[letter] = 0
            count2[letter] += 1
        #edge case of getting yellow yellow or yellow<->green
        for letter in count1:
            if letter not in count2:
                valid = False
                break
            if letter in exact_count:
                if count2[letter] != exact_count[letter]:
                    valid = False
                    break
            else:
                if count1[letter] > count2[letter]:
                    valid = False
                    break
        
        if not valid:
            continue
        for i, letter in enumerate(word):                    
            if result[i] == 'g':
                if letter != guess[i]:
                    valid = False
                    break
            if result[i] == 'y':
                if letter == guess[i]:
                    valid = False
                    break
                if guess[i] not in word:
                    valid = False
                    break
                
                
            if result[i] == 'r':
                #bit more tricky cause gray letters could also be green/yellow
                guessed_letter = guess[i]
                letter_valid = False
                for j in range(5):
                    if guess[j] == guessed_letter and result[j] != 'r':
                        letter_valid = True
                if letter_valid:
                    if letter == guessed_letter:
                        valid = False
                        break
                else:
                    if guessed_letter in word:
                        valid = False
                        break
        if valid:
            filtered_words.append(word)
    return filtered_words

#this algorithm is interesting
#we essentially simulate how good a guess is
#lower score -> better guess
def get_pattern(guess, answer):
    #we need the pattern of every word to split into buckets
    pattern = ""
    for i, letter in enumerate(guess):
        if guess[i] == answer[i]:
            pattern += 'g'
        elif guess[i] in answer:
            pattern += 'y'
        else:
            pattern += 'r'
    return pattern
def score_guess(guess, words):
    pattern_buckets = {}
    #if word is the answer
    for answer in words:
        pattern = get_pattern(guess, answer)
        if pattern not in pattern_buckets:
            pattern_buckets[pattern] = 0
        pattern_buckets[pattern] += 1
    total = len(words)
    score = 0
    for pattern in pattern_buckets:
        score += (pattern_buckets[pattern] * pattern_buckets[pattern]) / total
    return score
def best_guess(words):
    if len(words) == 0:
        print("Length of words is 0. You've filtered all words\n")
        return ""
    ans = 999999
    best_guess = words[0]
    for word in words:
        score = score_guess(word, words)
        if score < ans:
            ans = score
            best_guess = word
    return best_guess
def type_word(keyboard, word):
    time.sleep(0.5)
    keyboard.type(word)
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)
def get_result():
    while True:
        user_input = input("Enter the result\n: ")
        user_input = user_input.lower().strip()
        
        if len(user_input) != 5:
            print("Enter a valid result\n")
            continue
        valid = True
        for letter in user_input:
            if letter != 'g' and letter != 'y' and letter != 'r':
                print("Enter a valid result \n")
                valid = False
                break
        if valid:
            break
    return user_input
def main():
    keyboard = Controller()
    words = []
    for word in WORD_LIST:
        words.append(word)

    openers = ["crane"]
    delay = 2
    time.sleep(delay) #give time to readjust window
    for attempt in range(6):
        if attempt < len(openers) and len(words) > 10:
            guess = openers[attempt]
        else:
            guess = best_guess(words)
        
        #type_word(keyboard, guess)
        print("Enter the word: " + guess + '\n')
        result = get_result()
        if result == "ggggg":
            print("nice\n")
            return
        words = filter_words(words, guess, result)
    print("Couldn't solve it :( \n")
main()

    

        
    
