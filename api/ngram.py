import api.ulti as ut
import api.analysis as ana

import random
import math as ma


class NGramLM():
    def __init__(self, input_list, n):
        self.n = n
        self.all_ngram = ut.get_upto_ngrams(input_list, n)
        self.probability = {}
        for i in range(1, n + 1):
            self.probability[i] = {}
            for word in self.all_ngram[i]:
                self.probability[i][word] = ut.calculate_prob(self.all_ngram, word)
        # setup all of the possible guess
        self.guess = {}
        for i in range(2, n + 1):
            for words in self.probability[i]:
                keyList = words[:-1]
                tup = (words[-1], self.probability[i][words])
                if keyList not in self.guess:
                    self.guess[keyList] = []
                self.guess[keyList].append(tup)

    def generate_text(self, length, prompt=[]):
        result = [word for word in prompt]
        while len(result) < length:
            score = random.random()
            # print("Result is: ", result)
            # print("Prompt is: ", prompt)
            if len(prompt) >= self.n:
                prompt = prompt[len(prompt) - self.n + 1:]
            if tuple(prompt) in self.guess:
                for word, prob in self.guess[tuple(prompt)]:
                    if score < prob:
                        # print("Guess tuple ", word)
                        prompt.append(word)
                        result.append(word)
                        break
                    else:
                        score -= prob
            else:  # len(prompt)
                if len(prompt) == 0:
                    # print("prompt len: ", len(prompt))
                    for word, prob in self.probability[1].items():
                        if score < prob:
                            # print("Prob ", word)
                            prompt.append(word[0])
                            result.append(word[0])
                            break
                        else:
                            score -= prob
                else:
                    if len(prompt) == 1:
                        prompt = []
                    else:
                        prompt = prompt[1:]
        final = ""
        for i in range(len(result)):
            if i == len(result) - 1:
                final += result[i]
            else:
                final += result[i] + " "
        return final

    def generate_song(self, artist):
        analysis = ana.artist_analysis(artist)
        lyrics = ""
        if analysis['Intro'][0] >= 0.5:
            lyrics += "[Intro]\n"
            generated = self.generate_text(analysis['Intro'][1], prompt=[])
            generated = generated.capitalize()
            lyrics += generated
            lyrics += "\n"
        if analysis['Chorus'][0] >= 1.5:
            chorus = self.generate_text(analysis['Chorus'][1], prompt=[])
            lyrics += "[Verse 1]\n"
            generated = self.generate_text(analysis['Verse'][1], prompt=[])
            generated = generated.capitalize()
            lyrics += generated
            lyrics += "\n"

            lyrics += "[Chorus]\n"
            lyrics += chorus
            lyrics += "\n"

            lyrics += "[Verse 2]\n"
            generated = self.generate_text(analysis['Verse'][1], prompt=[])
            generated = generated.capitalize()
            lyrics += generated
            lyrics += "\n"

            lyrics += "[Chorus]\n"
            lyrics += chorus
            lyrics += "\n"

            lyrics += "[Outro]\n"
            generated = self.generate_text(analysis['Verse'][1], prompt=[])
            generated = generated.capitalize()
            lyrics += generated
            lyrics += "\n"
        else:
            chorus = self.generate_text(analysis['Chorus'][1], prompt=[])
            lyrics += "[Verse 1]\n"
            generated = self.generate_text(analysis['Verse'][1], prompt=[])
            generated = generated.capitalize()
            lyrics += generated
            lyrics += "\n"

            lyrics += "[Chorus]\n"
            lyrics += chorus
            lyrics += "\n"

            lyrics += "[Verse 2]\n"
            generated = self.generate_text(analysis['Verse'][1], prompt=[])
            generated = generated.capitalize()
            lyrics += generated
            lyrics += "\n"
        return lyrics

    def score_text(self, text):
        res = 0
        if text == "":
            return 1
        # ['Hamlet','just','use','Google']
        # n = 2
        # using b = 2
        curr = [text[0]]  # [ Hamlet, just ]
        # for j in range(self.ngram - 1, 0, -1):
        i = 1
        while i <= len(text):
            curr_tuple = tuple(curr)
            if len(curr) <= self.n:
                if curr_tuple in self.probability[len(curr)]:
                    curr_prob = self.probability[len(curr)][curr_tuple]
                    # print(curr_tuple, curr_prob)
                    res += ma.log2(curr_prob)
                    if i == len(text):
                        break
                    curr.append(text[i])
                    i += 1
                else:
                    if len(curr) < 2:  # This also means that we have looked in unigram
                        return float('inf')
                    else:
                        curr = curr[1:]
            else:
                curr = curr[1:]

        res *= -1 / len(text)
        return 2 ** (res)