# Wordle-Bot

An intelligent Wordle solver that uses a **bucket algorithm** approach to pick the mathematically best guess every turn.

---

## How It Works

Wordle gives you feedback after every guess:
- 🟩 **Green (g)** — right letter, right position
- 🟨 **Yellow (y)** — right letter, wrong position
- ⬛ **Gray (r)** — letter not in the word

A naive solver ignores this feedback and just tries random words. This bot uses every piece of feedback to eliminate as many candidates as possible, then picks the guess that will eliminate the most words on the *next* turn too.

The flow every round looks like this:

```
Start with 2315 possible words
        ↓
Guess "crane" (pre-chosen opener)
        ↓
You enter the colors (e.g. "rrrry")
        ↓
Filter: throw out every word that contradicts the feedback
        ↓
Maybe 80 words left
        ↓
Score every remaining word with the bucket algorithm
Pick the one that splits the remaining words most evenly
        ↓
Guess it, enter colors, filter again
        ↓
Repeat until solved (usually 3-4 guesses)
```

---

## The Bucket Algorithm (Core Idea)

For every word we're *considering* guessing, we ask:

> **"If I guess this word and it's wrong, how many words will I have left on average?"**

We want that number as low as possible.

### Step 1 — Simulate patterns with get_pattern

`get_pattern(guess, answer)` simulates what Wordle would show you if `answer` were the real answer:

```
get_pattern("crane", "crimp")

c → matches position 0 of crimp (c) → 'g'
r → matches position 1 of crimp (r) → 'g'
a → 'a' not in "crimp" at all      → 'r'
n → 'n' not in "crimp" at all      → 'r'
e → 'e' not in "crimp" at all      → 'r'

result: "ggrrr"
```
It's asking if I guess crane but crimp is the real answer, what pattern would wordle give back
This lets us simulate outcomes without actually playing the guess.

### Step 2 — Group words into buckets

Say 6 words remain: `crimp, crown, craft, brave, bland, blond, crane`

We're thinking of guessing `"crane"`. For each of those 6 words, we simulate what pattern we'd get back:

```
if answer = crimp  →  "ggrrr"
if answer = crown  →  "ggrrr"
if answer = craft  →  "gyrrr"
if answer = brave  →  "ryrrr"
if answer = bland  →  "rrrrr"
if answer = blond  →  "rrrrr"
```

Grouped into buckets by pattern:

```
"ggrrr"  →  [crimp, crown]    2 words
"gyrrr"  →  [craft]           1 word
"ryrrr"  →  [brave]           1 word
"rrrrr"  →  [bland, blond]    2 words
```

Each bucket is one possible thing Wordle could say back. The smaller the buckets, the fewer words remain, the closer you are to the answer.

### Step 3 — Score the guess

A perfect guess puts every word in its own bucket of size 1 — no matter what Wordle says, you'd know the answer instantly.
A terrible guess puts everything in one giant bucket — Wordle's response told you nothing.

The score formula penalises large buckets heavily by squaring the count:

```
score = sum of (count² / total) for each bucket. We don't have to divide by total as it wouldn't change the outcome but I just do it so it can act like an average. 
```

Using our example (total = 6):

```
"ggrrr" → (2 × 2) / 6 = 0.67
"gyrrr" → (1 × 1) / 6 = 0.17
"ryrrr" → (1 × 1) / 6 = 0.17
"rrrrr" → (2 × 2) / 6 = 0.67

total score = 1.67   ← lower is better
```

A bad guess that barely splits anything:

```
"rrrrr" → (5 × 5) / 6 = 4.17
"grrrrr" → (1 × 1) / 6 = 0.17

total score = 4.34   ← much worse
```

Squaring means a bucket of 5 is penalised 25x more than a bucket of 1, not just 5x. This forces the algorithm to really care about breaking up big groups.

`best_guess` runs this scoring on every remaining word and returns the one with the lowest score.

---

## Filtering Words — filter_words

After each guess, `filter_words` removes every word from the candidate list that contradicts what Wordle told us.

### Green
Letter must be in this exact position. Throw out any word that doesn't have it there.

### Yellow
Letter exists in the word but NOT in this position. Throw out words that:
- don't contain the letter at all, OR
- have the letter in this same spot

### Gray
Letter doesn't belong here. Two cases depending on whether the same letter also appeared green or yellow elsewhere:

- **If it appeared green/yellow elsewhere** — we know the letter exists, just not in this position. Only eliminate words that have it in this same spot.
- **If it never appeared green/yellow** — the letter truly doesn't exist anywhere. Eliminate any word containing it at all.

### Duplicate Letter Edge Case

Wordle can mark the same letter multiple times. For example guessing `"beget"` might give you one yellow `e` and one green `e`, meaning the answer has at least 2 e's.

The bot handles this with two counters:

- `count1` — counts how many times a letter appeared green or yellow (minimum known frequency)
- `exact_count` — if that same letter also went gray somewhere, the count is now exact (not just a minimum)

This prevents the bot from accepting words with too few of a confirmed letter, and from rejecting words with more copies of a letter than we've seen so far.

---

## Setup

**1. Get the word list**

Download the official Wordle answer list and save it as `wordle-answers-list.txt` in the same folder as the script. You can get it by running this once:

```python
import urllib.request
url = "https://gist.githubusercontent.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b/raw/wordle-answers-alphabetical.txt"
urllib.request.urlretrieve(url, "wordle-answers-list.txt")
```
or just go to that url link and save it in the same folder as the python script
**3. Run the solver**
```bash
python wordle_solver.py
```

The bot will print the word to type. After typing it in Wordle, enter the color result back into the terminal using `g` (green), `y` (yellow), `r` (gray).

Example:
```
Enter the word: crane
Enter the result
: rrrry
Enter the word: sleet
Enter the result
: rrggg
Enter the word: tweet
nice
```

---

## Project Structure

```
wordle_solver.py        main script
wordle-answers-list.txt word list (you provide this)
README.md               this file
```

---

## Credits

The information-theoretic approach to Wordle solving was popularised by **3Blue1Brown (Grant Sanderson)** in his February 2022 video *"Solving Wordle using information theory"*. The bucket scoring used here is a simplified approximation of his full Shannon entropy approach, trading a small amount of optimality for simplicity and readability.

The mathematically optimal opener according to 3Blue1Brown's corrected analysis is `"salet"`, though `"crane"` performs nearly as well and is used here as the default.
