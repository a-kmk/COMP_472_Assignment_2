import pickle
import string
import math
from decimal import *


# order of execution
# load_reviews->load_stop_words->parse_reviews-> compute_reviews_statistics -> compute_words_frequency ->
# compute_words_frequency -> compute_reviews_probabilities
class Analyser:
    def __init__(self, review_objs_path, stop_words_path, txt_output_path, dictionary_output_path):
        self.reviews_path = review_objs_path
        self.stop_path = stop_words_path
        self.text_paht = txt_output_path
        self.dict_path = dictionary_output_path
        # stored review objs from webscraping
        self.reviews = []
        self.testreviews = []
        # dictionary with word as key and a word record objs as value, which store frequency and probability for a
        # given word in the reviews with fast lookup
        self.vocabulary = {}
        # dictionary with word we have to ignore as key, and their frequency in the reviews as value
        self.stop_words = {}

        # for probability calculation
        self.positive_words = 0
        self.negative_words = 0

        self.total_reviews = 0
        self.negative_reviews = 0
        self.positive_reviews = 0

        self.prior_prob_pos = 0.0
        self.prior_prob_neg = 0.0

    # load the reviews array we got from the webscraper
    def load_reviews(self):
        with open(self.reviews_path, 'rb') as file:
            self.reviews = pickle.load(file)

            #splits 10% into test array, keeps 90% in review array
            length = len(self.reviews)
            testnum = length * 10 / 100
            splitat = length-math.floor(testnum)
            for x in range(splitat,length):
                self.testreviews.append(self.reviews[x])

            tempArray=[]
            for x in range(splitat):
                tempArray.append(self.reviews[x])
            print(len(self.testreviews))
            self.reviews = tempArray;

    # read the stop words and store them into a dictionary with the word as the id for quick lookup
    def load_stop_words(self):
        with open(self.stop_path, 'r') as reader:
            for line in reader:
                self.stop_words[line[:-1]] = 0

    # going through the reviews and record each word's occurrence in positive and negative reviews
    def parse_reviews(self):

        for review in self.reviews:
            # remove all punctuations from the review body

            content_no_punc = review.content.translate(str.maketrans('', '', string.punctuation)).lower()
            title_no_punc = review.content.translate(str.maketrans('', '', string.punctuation)).lower()

            words = content_no_punc.split() + title_no_punc.split()

            for word in words:
                if word in self.stop_words:
                    self.stop_words[word] += 1
                else:
                    if word in self.vocabulary:
                        self.vocabulary[word].add_freq(review.positive)
                    # create an entry for the word in the dictionary
                    else:
                        self.vocabulary[word] = WordRecord(word, review.positive)

    def compute_reviews_frequency(self):
        self.total_reviews = len(self.reviews)
        for review in self.reviews:
            if review.positive:
                self.positive_reviews += 1
            else:
                self.negative_reviews += 1

    def compute_words_frequency(self):
        for word_record in self.vocabulary.values():
            # print(str(word_record))
            self.positive_words += word_record.pos_freq
            self.negative_words += word_record.neg_freq

    def compute_words_probability(self):
        for word_record in self.vocabulary.values():
            word_record.set_prob(True, word_record.pos_freq / self.positive_words)
            word_record.set_prob(False, word_record.neg_freq / self.negative_words)

    def compute_prior_probability(self):
        self.prior_prob_pos = self.positive_reviews / self.total_reviews
        self.prior_prob_neg = self.negative_reviews / self.total_reviews

    def compute_statistics(self):
        self.load_reviews()
        self.load_stop_words()
        self.parse_reviews()
        self.compute_reviews_frequency()
        self.compute_words_frequency()
        self.compute_words_probability()
        self.compute_prior_probability()

    def classify(self, smoothing):
        #todo: check for valid smoothing range
        counter = 1;
        for review in self.testreviews:
            # remove all punctuations from the review body
            content_no_punc = review.content.translate(str.maketrans('', '', string.punctuation)).lower()
            title_no_punc = review.content.translate(str.maketrans('', '', string.punctuation)).lower()

            words = content_no_punc.split() + title_no_punc.split()




            #calculate probability of positive and negative review
            positive_prob = math.log10(self.prior_prob_pos + smoothing)
            negative_prob = math.log10(self.prior_prob_neg + smoothing)
            for word in words:
                if word in self.vocabulary:
                    positive_prob += math.log10(self.vocabulary[word].pos_prob + smoothing)
                    negative_prob += math.log10(self.vocabulary[word].neg_prob + smoothing)
                    if(positive_prob >= negative_prob) :
                        prediction = "positive"
                    else :
                        prediction = "negative"

            if (review.positive) :
                actual = "positive"
            else :
                 actual = "negative"

            if (actual == prediction) :
                guess = "right"
            else :
                guess = "wrong"
            print("No." + str(counter) + " " +  review.title + ": ")
            print(str(positive_prob) + " ," + str(negative_prob) + ", " + prediction + ",  " + actual + ", " + guess +"\n")
            counter+=1
            #calculate probability of negative revie
    def display_statistics(self):
        print(f'\nPrior probabilities:\nPositive: {self.prior_prob_pos}\nNegative: {self.prior_prob_neg}')
        print(f'\nTotal reviews:\nPositive: {self.positive_reviews}\nNegative:{self.negative_reviews}')
        print(f'\nTotal positive words: {self.positive_words}\nTotal negative words: {self.negative_words}')
        print(f'\nWord specific statistics: \n')
        for word_record in self.vocabulary.values():
            print(str(word_record))

class WordRecord:
    def __init__(self, word, positive):
        self.word = word
        self.pos_freq = 1 if positive else 0
        self.neg_freq = 0 if positive else 1
        self.pos_prob = 0.0
        self.neg_prob = 0.0

    def add_freq(self, positive):
        if positive:
            self.pos_freq += 1
        else:
            self.neg_freq += 1

    def set_prob(self, positive, prob):
        if positive:
            self.pos_prob = prob
        else:
            self.neg_prob = prob

    def __str__(self):
        return f'\nword: {self.word}\npositive frequency: {self.pos_freq}\nnegative frequency: {self.neg_freq}\npositive probability: {self.pos_prob}\nnegative probability: {self.neg_prob} '

