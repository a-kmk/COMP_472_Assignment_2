import os
import pickle
import string
import math


# order of execution
# load_reviews->load_stop_words->parse_reviews-> compute_reviews_statistics -> compute_words_frequency ->
# compute_words_frequency -> compute_reviews_probabilities
class Analyser:
    def __init__(self, review_objs_path, stop_words_path, txt_output_path, dictionary_output_path, removed_words_path, external_testing = False, external_testing_data_path = ''):
        self.reviews_path = review_objs_path
        self.stop_path = stop_words_path
        self.text_path = txt_output_path
        self.dict_path = dictionary_output_path
        self.remove_path = removed_words_path
        self.external_test = external_testing
        self.external_testing_data_path = external_testing_data_path
        # stored review objs from webscraping
        self.reviews = []
        self.testreviews = []
        # for preventing testreviews from getting replaced between each compute_statistics
        self.reset = False
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
        if not self.external_test:
            with open(self.reviews_path, 'rb') as file:
                self.reviews = pickle.load(file)

                # splits 10% into test array, keeps 90% in review array
                length = len(self.reviews)
                testnum = length * 10 / 100
                splitat = length - math.floor(testnum)
                for x in range(splitat, length):
                    self.testreviews.append(self.reviews[x])

                tempArray = []
                for x in range(splitat):
                    tempArray.append(self.reviews[x])
                self.reviews = tempArray
        else:
            with open(self.reviews_path, 'rb') as file:
                self.reviews = pickle.load(file)
            with open(self.external_testing_data_path, 'rb') as file:
                self.testreviews = pickle.load(file)

    # read the stop words and store them into a dictionary with the word as the id for quick lookup
    def load_stop_words(self):
        with open(self.stop_path, 'r') as reader:
            for line in reader:
                self.stop_words[line[:-1]] = 0

    # going through the reviews and record each word's occurrence in positive and negative reviews
    def parse_reviews(self, length_filter = 0, filter_out_above = False):

        for review in self.reviews:
            # remove all punctuations from the review body

            content_no_punc = review.content.translate(str.maketrans('', '', string.punctuation)).lower()
            title_no_punc = review.content.translate(str.maketrans('', '', string.punctuation)).lower()

            words = content_no_punc.split() + title_no_punc.split()

            for word in words:
                if word in self.stop_words:
                    self.stop_words[word] += 1

                elif len(word) > length_filter and not filter_out_above:
                    if word in self.vocabulary:
                        self.vocabulary[word].add_freq(review.positive)
                        self.vocabulary[word].tot_freq += 1
                    # create an entry for the word in the dictionary
                    else:
                        self.vocabulary[word] = WordRecord(word, review.positive)
                        self.vocabulary[word].tot_freq += 1

                elif len(word) < length_filter and filter_out_above:
                    if word in self.vocabulary:
                        self.vocabulary[word].add_freq(review.positive)
                        self.vocabulary[word].tot_freq += 1
                    # create an entry for the word in the dictionary
                    else:
                        self.vocabulary[word] = WordRecord(word, review.positive)
                        self.vocabulary[word].tot_freq += 1

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

    # a consequence of doing it this way is that we'll need to re-parse the reviews between every task
    # if filter = 2 -> use parse_reviews_remove2
    # if filter = 4 -> use parse_reviews_remove2
    # if filter = 9 -> use parse_reviews_remove2
    # else use parse_reviews (default)
    # *filter takes a number or if no number given its default
    def compute_statistics(self, length_filter=0):
        self.load_reviews()
        self.load_stop_words()
        if length_filter == 2:
            self.parse_reviews(2, False)
        elif length_filter == 4:
            self.parse_reviews(4, False)
        elif length_filter == 9:
            self.parse_reviews(9, True)
        else:
            self.parse_reviews()
        self.compute_reviews_frequency()
        self.compute_words_frequency()
        self.compute_words_probability()
        self.compute_prior_probability()

    # filter used to print to txt files
    def classify(self, output_path='result.txt', smoothing=1.0):
        review_counter = 0
        right_review_counter = 0
        wrong_review_counter = 0

        text_file = open(output_path, "a", encoding='utf8')
        for review in self.testreviews:
            # remove all punctuations from the review body
            content_no_punc = review.content.translate(str.maketrans('', '', string.punctuation)).lower()
            title_no_punc = review.content.translate(str.maketrans('', '', string.punctuation)).lower()
            words = content_no_punc.split() + title_no_punc.split()

            # calculate probability of positive and negative review
            positive_prob = math.log10(self.prior_prob_pos)
            negative_prob = math.log10(self.prior_prob_neg)
            for word in words:
                if word in self.vocabulary:
                    positive_prob += math.log10((self.vocabulary[word].pos_freq + smoothing) / (
                                self.positive_words + smoothing * self.positive_words))
                    negative_prob += math.log10((self.vocabulary[word].neg_prob + smoothing) / (
                                self.negative_words + smoothing * self.negative_words))
                else:
                    positive_prob += math.log10(smoothing / (self.positive_words + smoothing * self.positive_words))
                    negative_prob += math.log10(smoothing / (self.negative_words + smoothing * self.negative_words))

            if positive_prob >= negative_prob:
                prediction = "positive"
            else:
                prediction = "negative"

            if review.positive:
                actual = "positive"
            else:
                actual = "negative"

            if actual == prediction:
                guess = "right"
                right_review_counter += 1
            else:
                guess = "wrong"
                wrong_review_counter += 1

            text_file.write("No." + str(review_counter) + " " + review.title + ": \n")
            text_file.write(str(positive_prob) + " ," + str(
                negative_prob) + ", " + prediction + ",  " + actual + ", " + guess + "\n")
            review_counter += 1

        text_file.write(f'-------------------------------------------------------\nThe smoothing value is {smoothing}')
        text_file.write("The prediction correctness is " + str(right_review_counter / review_counter))
        text_file.write("\n")
        text_file.write("\n")
        text_file.close()

    # for debugging only
    def display_statistics(self):
        print(f'\nPrior probabilities:\nPositive: {self.prior_prob_pos}\nNegative: {self.prior_prob_neg}')
        print(f'\nTotal reviews:\nPositive: {self.positive_reviews}\nNegative:{self.negative_reviews}')
        print(f'\nTotal positive words: {self.positive_words}\nTotal negative words: {self.negative_words}')
        print(f'\nWord specific statistics: \n')

    def register_stop_word(self):
        total_removed_words = 0
        with open(self.remove_path, 'w', encoding='utf-8') as f:
            for word, frequency in self.stop_words.items():
                total_removed_words += frequency
                f.writelines(f'word:{word} frequency:{frequency}\n')
            f.writelines(f'\nTotal words:{total_removed_words}\n')

    def register_word_stats(self, vocab, output_path='model.txt'):
        with open(output_path, 'a', encoding='utf-8') as f:
            f.writelines('\n')
            i = 0
            for word_record in vocab.values():
                i += 1
                f.writelines(f'No. {i} {word_record.word}\n')
                f.writelines(
                    f'Freq in pos: {word_record.pos_freq}, prob in pos: {word_record.pos_prob}, freq in neg: {word_record.neg_freq}, prob in neg: {word_record.neg_prob}\n')

    # for 2.1
    def classify_gradual_removal(self, smoothing, vocabulary, percentage, quantity, pos_words, neg_words):
        counter = 0
        right_counter = 0
        wrong_counter = 0

        file1 = open("frequency-result.txt", "a", encoding='utf8')

        testing_subject = 'percentage based removal' if percentage else 'frequency based removal'
        file1.write(
            f'\n\n------------------Testing for {testing_subject} at {quantity}, total words count: {pos_words + neg_words}\n-----------------------\n\n')

        for review in self.testreviews:
            # remove all punctuations from the review body
            content_no_punc = review.content.translate(str.maketrans('', '', string.punctuation)).lower()
            title_no_punc = review.content.translate(str.maketrans('', '', string.punctuation)).lower()
            words = content_no_punc.split() + title_no_punc.split()

            # calculate probability of positive and negative review
            positive_prob = math.log10(self.prior_prob_pos)
            negative_prob = math.log10(self.prior_prob_neg)
            for word in words:
                if word in vocabulary:
                    positive_prob += math.log10((vocabulary[word].pos_freq + smoothing) / (
                            pos_words + len(self.vocabulary)))
                    negative_prob += math.log10((vocabulary[word].neg_prob + smoothing) / (
                            neg_words + len(self.vocabulary)))
                else:
                    positive_prob += math.log10(smoothing / (pos_words + len(self.vocabulary)))
                    negative_prob += math.log10(smoothing / (neg_words + len(self.vocabulary)))

            if positive_prob >= negative_prob:
                prediction = "positive"
            else:
                prediction = "negative"

            if review.positive:
                actual = "positive"
            else:
                actual = "negative"

            if actual == prediction:
                guess = "right"
                right_counter += 1
            else:
                guess = "wrong"
                wrong_counter += 1

            file1.write("No." + str(counter + 1) + " " + review.title + ": ")
            file1.write(str(positive_prob) + " ," + str(
                negative_prob) + ", " + prediction + ",  " + actual + ", " + guess + "\n")
            counter += 1
        accuracy = right_counter / counter
        file1.write(f'The prediction correctness is {accuracy}')
        file1.close()
        return accuracy

    # for 2.1 returns a new dictionary after removing the words with less than specified number of frequency
    def word_removal_by_count(self, vocabulary, removal_upper_bound):
        filtered_dict = {}
        total_pos = 0
        total_neg = 0

        for word, word_record in vocabulary.items():
            if word_record.tot_freq > removal_upper_bound:
                filtered_dict[word] = word_record
                total_pos += word_record.pos_freq
                total_neg += word_record.neg_freq

        # these resets the pos_freq and neg_freq of each word record everytime, so need to rewrite them every time
        for word_record in filtered_dict.values():
            word_record.set_prob(True, word_record.pos_freq / total_pos)
            word_record.set_prob(False, word_record.neg_freq / total_neg)

        return filtered_dict, total_pos, total_neg

    # for 2.1 returns a new dictionary after removing the specified top percentage entries
    def word_removal_by_percent(self, vocabulary, removal_percentage_from_top):
        total_entries = len(vocabulary)
        entries_to_keep = total_entries * ((100 - removal_percentage_from_top) / 100)
        entries_to_keep = int(entries_to_keep)

        sorted_dict = dict(sorted(vocabulary.items(), key=lambda word_entry: word_entry[1].tot_freq))

        filtered_dict = {}

        total_pos = 0
        total_neg = 0
        i = 1
        for word, word_record in sorted_dict.items():
            filtered_dict[word] = word_record
            total_pos += word_record.pos_freq
            total_neg += word_record.neg_freq
            i += 1
            if i >= entries_to_keep:
                break

        for word_record in filtered_dict.values():
            word_record.set_prob(True, word_record.pos_freq / total_pos)
            word_record.set_prob(False, word_record.neg_freq / total_neg)

        return filtered_dict, total_pos, total_neg

    # for 2.1, executes the tasks in 2.1 and save results and model
    def gradual_word_removal_by_frequency(self):
        # testing for frequency, 1, 10, 20, compounded, e.g. vocabulary after a stage of removal is passed to the next
        counts = [1, 10, 20]
        count_vocabularies = [self.vocabulary]

        # these actually store the number of positive and negative words for a given vocabulary
        count_positive_probs = [self.positive_words]
        count_negative_probs = [self.negative_words]

        index = 0
        for count in counts:
            filtered_dict, pos_words, neg_words = self.word_removal_by_count(count_vocabularies[index], count)
            count_vocabularies.append(filtered_dict)
            count_positive_probs.append(pos_words)
            count_negative_probs.append(neg_words)
            index += 1

        # testing percentage, 5, 10, 20
        percentages = [5, 10, 20]
        perct_vocabularies = [count_vocabularies[len(count_vocabularies) - 1]]
        perct_positive_probs = [count_positive_probs[len(count_positive_probs) - 1]]
        perct_negative_probs = [count_negative_probs[len(count_negative_probs) - 1]]

        index = 0
        for percentage in percentages:
            filtered_dict, pos_words, neg_words = self.word_removal_by_percent(perct_vocabularies[index], percentage)
            perct_vocabularies.append(filtered_dict)
            perct_positive_probs.append(pos_words)
            perct_negative_probs.append(neg_words)
            index += 1
        
        freq_model_output = 'frequency-model.txt'
        if os.path.exists(freq_model_output):
            os.remove(freq_model_output)

        self.register_word_stats(perct_vocabularies[-1], freq_model_output)
        
        freq_result_output = 'frequency-result.txt'
        if os.path.exists(freq_result_output):
            os.remove(freq_result_output)

        # [(word_remaining, accuracy), ...]
        result_set = []

        # this is to account for the first indexes in count and percentages because the vocabularies start off at 0
        counts.insert(0, 0)
        percentages.insert(0, 100)
        for i in range(len(count_vocabularies)):
            accuracy = self.classify_gradual_removal(1, count_vocabularies[i], False, counts[i],
                                                     count_positive_probs[i],
                                                     count_negative_probs[i])
            word_remaining = count_positive_probs[i] + count_negative_probs[i]
            result_set.append((word_remaining, accuracy))

        for i in range(len(perct_vocabularies)):
            accuracy = self.classify_gradual_removal(1, perct_vocabularies[i], True, percentages[i],
                                                     perct_positive_probs[i],
                                                     perct_negative_probs[i])
            word_remaining = perct_positive_probs[i] + perct_negative_probs[i]
            result_set.append((word_remaining, accuracy))

        return result_set

    def return_total_words(self):
        return self.positive_words + self.negative_words

    def reset_analyser(self):
        self.reviews = []
        self.testreviews = []
        self.reset = False
        self.vocabulary = {}
        self.stop_words = {}

        self.positive_words = 0
        self.negative_words = 0

        self.total_reviews = 0
        self.negative_reviews = 0
        self.positive_reviews = 0

        self.prior_prob_pos = 0.0
        self.prior_prob_neg = 0.0


class WordRecord:
    def __init__(self, word, positive):
        self.word = word
        self.pos_freq = 1 if positive else 0
        self.neg_freq = 0 if positive else 1
        self.pos_prob = 0.0
        self.neg_prob = 0.0
        self.tot_freq = 0

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
