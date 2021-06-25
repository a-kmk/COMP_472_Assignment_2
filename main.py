import os
import re
from matplotlib import pyplot as plt
from analyser import Analyser
from webscraper import IMDBReviewsCollector

if __name__ == '__main__':
    # run webscraper
    # if you never ran it before, you need to run it at least once on your machine for the analyser to work,
    # because analyser work with serialized reviews data file created by the scraper
    # adjust the show_ur, to a imdb url for a show of your liking
    # adjust user-agent, pls change it to your own or grab one from the internet that is for mac/pc

    header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36'}
    show_url = 'https://www.imdb.com/title/tt0306414/'
    reviews_filename = 'review_objs.pickle'
    sample_scraper = IMDBReviewsCollector(show_url, reviews_filename, header)
    sample_scraper.gather_data()
    # run
    reviews_path = 'review_objs.pickle'
    stop_words_path = 'stopword.txt'
    txt_output_path = 'model.txt'
    removed_words_path = 'removed.txt'
    dictionary_output_path = 'vocabulary_dictionary.pickle'
    sample_analyser = Analyser(reviews_path, stop_words_path, txt_output_path, dictionary_output_path,
                               removed_words_path)
    sample_analyser.compute_statistics()
    # ----------------------------------------TASK 2.1------------------------------------------------
    
    # sample_analyser.gradual_word_removal_by_frequency()
    
    # ----------------------------------------TASK 2.2------------------------------------------------
    smooth_result_path = 'smooth-result.txt'
    if os.path.exists(smooth_result_path):
        os.remove(smooth_result_path)

    sample_analyser.classify(smooth_result_path, 1)
    sample_analyser.classify(smooth_result_path, 1.2)
    sample_analyser.classify(smooth_result_path, 1.4)
    sample_analyser.classify(smooth_result_path, 1.6)
    sample_analyser.classify(smooth_result_path, 1.8)
    sample_analyser.classify(smooth_result_path, 2.0)

    with open(smooth_result_path, 'r') as file:
        outputStr = file.read()
    substring = "The prediction correctness is "
    matches = re.finditer(substring, outputStr)
    matches_positions = [match.start() for match in matches]
    print(matches_positions)

    #this gets the y axis (accuracy)
    yValues = []
    xValues = []
    for x in range(len(matches_positions)):
        print(matches_positions[x])
        aString = outputStr[matches_positions[x]+30] + outputStr[matches_positions[x] + 31] + outputStr[matches_positions[x] + 32] + outputStr[matches_positions[x] + 33]+ outputStr[matches_positions[x] + 34] + outputStr[matches_positions[x] + 35]
        aFloat = float(aString)
        yValues.append(aFloat)
        xValues.append(1+0.2*x)
    print(yValues)
    print(xValues)

    plt.xkcd()
    plt.plot(xValues, yValues, color='#444444', linestyle='--')
    plt.xlabel('smoothing values')
    plt.ylabel('Accuracy')
    plt.title('Model accuracy by smoothing value')

    plt.legend()
    plt.tight_layout()
    plt.show()

    # ----------------------------------------TASK 2.3------------------------------------------------
    # make new file
    # text_file = open("length-result.txt", "w")
    # text_file = open("length-model.txt", "w")
    # text_file.close()
    # sample_analyser = Analyser(reviews_path, stop_words_path, txt_output_path, dictionary_output_path)
    # sample_analyser.compute_statistics(2)
    # sample_analyser.display_statistics()
    # sample_analyser.register_word_stats_for_23(sample_analyser.vocabulary)
    # sample_analyser.classify(1, True)

    # sample_analyser = Analyser(reviews_path, stop_words_path, txt_output_path, dictionary_output_path)
    # sample_analyser.compute_statistics(4)
    # # sample_analyser.display_statistics()
    # sample_analyser.register_word_stats_for_23(sample_analyser.vocabulary)
    # sample_analyser.classify(1, True)

    # sample_analyser = Analyser(reviews_path, stop_words_path, txt_output_path, dictionary_output_path)
    # sample_analyser.compute_statistics(9)
    # sample_analyser.display_statistics()
    # sample_analyser.register_word_stats_for_23(sample_analyser.vocabulary)
    # sample_analyser.classify(1, True)
    # END TASK 2.3

    # ----------------------------------------TASK 1.2------------------------------------------------

    sample_analyser.register_stop_word()
    sample_analyser.display_statistics()
