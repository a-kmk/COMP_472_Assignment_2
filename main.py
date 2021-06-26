import os
import re
from matplotlib import pyplot as plt
from analyser import Analyser
from webscraper import IMDBReviewsCollector

def create_graph(title, x_name, y_name, x_values, y_values):
    plt.xkcd()
    plt.plot(x_values, y_values, color='#444444', linestyle='--')
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.title(title)

    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    # run webscraper
    # if you never ran it before, you need to run it at least once on your machine for the analyser to work,
    # because analyser work with serialized reviews data file created by the scraper
    # adjust the show_ur, to a imdb url for a show of your liking
    # adjust user-agent, pls change it to your own or grab one from the internet that is for mac/pc
    #

    # header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36'}
    # show_url = 'https://www.imdb.com/title/tt0306414/'
    # reviews_filename = 'review_objs.pickle'
    # test_review_filename = 'test_review_objs.pickle'
    # sample_scraper = IMDBReviewsCollector(show_url, reviews_filename, test_review_filename, header)

    # #get data through main page
    # sample_scraper.gather_data()

    # # need to ran if you want to get testing data from a csv file
    # # need to be ran independently from .gather_data() above
    # episode_data_path = 'testing_data.csv'
    # sample_scraper.gather_test_data_from_file(episode_data_path)

    # # run
    reviews_path = 'review_objs.pickle'
    stop_words_path = 'stopword.txt'
    txt_output_path = 'model.txt'
    removed_words_path = 'removed.txt'
    dictionary_output_path = 'vocabulary_dictionary.pickle'
    test_data_input_path = 'test_review_objs.pickle'
    # set to False if you just want to use 10% of the training set as testing set
    # set to True if you want to use the testing data from the csv
    sample_analyser = Analyser(reviews_path, stop_words_path, txt_output_path, dictionary_output_path,
                               removed_words_path, True, test_data_input_path)
    sample_analyser.compute_statistics()

    # # ----------------------------------------TASK 1.2 & 1.3------------------------------------------
    # sample_analyser.register_word_stats(sample_analyser.vocabulary)
    # sample_analyser.classify()

    # ----------------------------------------TASK 2.1------------------------------------------------
    # #[(words_remaining, accuracy)]
    # result_set = sample_analyser.gradual_word_removal_by_frequency()
    #
    # y_values = []
    # x_values = []
    # for result in result_set:
    #     x_values.append(result[0])
    #     y_values.append(result[1])
    # create_graph('Model Accuracy by Frequency Based Removal','Words Remaining', 'Accuracy', x_values, y_values)
    
    # ----------------------------------------TASK 2.2------------------------------------------------
    # smooth_result_path = 'smooth-result.txt'
    # smooth_model_path = 'smooth-model.txt'
    # if os.path.exists(smooth_result_path):
    #     os.remove(smooth_result_path)
    # if os.path.exists(smooth_model_path):
    #     os.remove(smooth_model_path)
    #
    # filter_smoothing_values = [1, 1.2, 1.4, 1.6, 1.8, 2.0]
    #
    # for smoothing_value in filter_smoothing_values:
    #     sample_analyser.classify(smooth_result_path, smoothing_value)
    #
    # sample_analyser.register_stop_word()
    # sample_analyser.register_word_stats(sample_analyser.vocabulary, smooth_model_path)
    #
    # with open(smooth_result_path, 'r') as file:
    #     outputStr = file.read()
    # substring = "The prediction correctness is "
    # matches = re.finditer(substring, outputStr)
    # matches_positions = [match.start() for match in matches]
    #
    # #this gets the y axis (accuracy)
    # y_values = []
    # x_values = []
    # for x in range(len(matches_positions)):
    #     aString = outputStr[matches_positions[x]+30] + outputStr[matches_positions[x] + 31] + outputStr[matches_positions[x] + 32] + outputStr[matches_positions[x] + 33]+ outputStr[matches_positions[x] + 34] + outputStr[matches_positions[x] + 35]
    #     aFloat = float(aString)
    #     y_values.append(aFloat)
    #     x_values.append(1+0.2*x)
    #
    # create_graph('Model accuracy by smoothing value', 'Smoothing Values', 'Accuracy', x_values, y_values)

    ## ----------------------------------------TASK 2.3------------------------------------------------
    # # make new file
    # length_result_path = "length-result.txt"
    # length_model_path = "length-model.txt"
    #
    # if os.path.exists(length_result_path):
    #     os.remove(length_result_path)
    # if os.path.exists(length_model_path):
    #     os.remove(length_model_path)
    #
    # x_values = []
    #
    # sample_analyser.register_word_stats(sample_analyser.vocabulary, length_model_path)
    # sample_analyser.classify(length_result_path)
    # x_values.append(sample_analyser.return_total_words())
    #
    # filter_lengths = [2,4,9]
    #
    # for length in filter_lengths:
    #     sample_analyser.reset_analyser()
    #     sample_analyser.compute_statistics(length)
    #     sample_analyser.register_word_stats(sample_analyser.vocabulary, length_model_path)
    #     sample_analyser.classify(length_result_path)
    #     x_values.append(sample_analyser.return_total_words())
    #
    # # finding accuracy values from the text result file
    # with open(length_result_path, 'r') as file:
    #     outputStr = file.read()
    # substring = "The prediction correctness is "
    # matches = re.finditer(substring, outputStr)
    # matches_positions = [match.start() for match in matches]
    # # print(matches_positions)
    #
    # #this gets the y axis (accuracy)
    # y_values = []
    # for x in range(len(matches_positions)):
    #     # print(matches_positions[x])
    #     aString = outputStr[matches_positions[x]+30] + outputStr[matches_positions[x] + 31] + outputStr[matches_positions[x] + 32] + outputStr[matches_positions[x] + 33]+ outputStr[matches_positions[x] + 34] + outputStr[matches_positions[x] + 35]
    #     aFloat = float(aString)
    #     y_values.append(aFloat)
    #
    # # doing it directly, when we reach the accuracy/words remaining for removal of words with length > 9
    # # because it's the last point in the dataset, the graph does a weird jump backward from the increased
    # # words remaining and an increase in accuracy, and our graph ends up with a horizontal convex shape
    # # with some Xs giving two Y values, to solve this, bubble sort x_values and y_values pairs
    #
    # # comment these out to see what I'm talking about
    # for i in range(len(x_values) - 1):
    #     for j in range(len(x_values) - i - 1):
    #         if x_values[j] > x_values[j+1]:
    #             x_values[j], x_values[j+1] = x_values[j+1], x_values[j]
    #             y_values[j], y_values[j+1] = y_values[j+1], y_values[j]
    #
    # create_graph('Model Accuracy by Length Based Removal', 'Words Remaining', 'Accuracy', x_values, y_values)
    # # # END TASK 2.3