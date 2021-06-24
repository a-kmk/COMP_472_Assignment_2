import re
import string
from math import log

import classifier
from webscraper import IMDBReviewsCollector
from bs4 import BeautifulSoup
from requests import get
import pickle
from webscraper import Review
from matplotlib import pyplot as plt
from analyser import Analyser
from analyser import WordRecord


def test_season():
    wire_url = 'https://www.imdb.com/title/tt0306414/'
    response = get(wire_url, headers={'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 ('
                                                    'KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'})
    html_soup = BeautifulSoup(response.text, 'html.parser')
    # print(html_soup.prettify())
    # browse-episodes-season
    season_dropdown = html_soup.find('select', id='browse-episodes-season')
    print(season_dropdown['aria-label'][0])


def test_only_one_season():
    one_season_url = 'https://www.imdb.com/title/tt2006848/'
    response = get(one_season_url, headers={'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) '
                                                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                                                          'Chrome/91.0.4472.101 Safari/537.36'})
    html_soup = BeautifulSoup(response.text, 'html.parser')
    season_dropdown = html_soup.find_all('a', class_='ipc-button ipc-button--single-padding '
                                                     'ipc-button--center-align-content ipc-button--default-height '
                                                     'ipc-button--core-base ipc-button--theme-base '
                                                     'ipc-button--on-accent2 ipc-text-button')
    seasons = season_dropdown[1].div.string
    print(int(seasons[0]))


def test_getting_episodes():
    url = 'https://www.imdb.com/title/tt0306414/'
    site_url = 'https://www.imdb.com/'
    episode_endpoint = 'episodes?season='
    review_endpoint = 'reviews'
    season_num = 1

    response = get(url + episode_endpoint + str(season_num), headers={'user-agent': 'Mozilla/5.0 (Windows NT 6.3; '
                                                                                    'Win64; x64) AppleWebKit/537.36 ('
                                                                                    'KHTML, like Gecko) '
                                                                                    'Chrome/91.0.4472.101 '
                                                                                    'Safari/537.36'})
    html_soup = BeautifulSoup(response.text, 'html.parser')
    episodes_list = html_soup.find('div', class_='list detail eplist')

    if episodes_list is not None:
        episodes = episodes_list.findChildren('div', class_='info')
        for episode in episodes:
            title_link = episode.strong.a
            name = title_link.string
            air_time = episode.find('div', class_='airdate').string.strip()
            href = title_link['href'] + review_endpoint
            print(f'{name}\n{air_time}\n{href}')
    else:
        print('failed')


def test_getting_reviews():
    response = get('https://www.imdb.com/title/tt5924366/reviews', headers={'user-agent': 'Mozilla/5.0 (Windows NT '
                                                                                          '6.3; Win64; x64) '
                                                                                          'AppleWebKit/537.36 (KHTML, '
                                                                                          'like Gecko) '
                                                                                          'Chrome/91.0.4472.101 '
                                                                                          'Safari/537.36'})
    html_soup = BeautifulSoup(response.text, 'html.parser')
    reviews_list = html_soup.find('div', class_='lister-list')
    reviews = reviews_list.findChildren('div', class_=lambda x: x and 'lister-item mode-detail imdb-user-review' in x)
    reviews_2 = reviews_list.findChildren('div', class_='lister-item mode-detail imdb-user-review collapsable')

    print(f'review using the first selector{len(reviews)}')
    print(f'review using the second selector{len(reviews_2)}\n')

    counter = 0
    for review in reviews:
        counter += 1
        rating_element = review.find('span', class_='rating-other-user-rating')
        rating = int(rating_element.find_all('span')[0].string)
        title = review.find('a', class_='title').string.strip()
        content = review.find('div', class_='text show-more__control').get_text(separator=' ')
        print(f'title:{title}\nrating:{rating}\ncontent:{content}\n')
    print(f'\ntotal: {counter}')


def test_serialization_test():
    review_1 = Review('don', 8, 'big dan is the biggest don\ndaannng')
    review_2 = Review('donny', 4, 'big dan is the smallest don\ndaannng2')
    reviews = [review_1, review_2]
    # pickled_reviews = []
    # hmm, we can either write a bunch of pickled objs into a file or write a pickled array of objs into a file
    # let's try both

    # to array, unnecessary
    # for review in reviews:
    #     pickled_reviews.append(pickle.dumps(review))

    with open('review_objs.pickle', 'wb') as file:
        pickle.dump(len(reviews), file)
        for review in reviews:
            pickle.dump(review, file)

    with open('review_obj_2.pickle', 'wb') as file:
        pickle.dump(reviews, file)

    with open('review_objs.pickle', 'rb') as file:
        print('for storing individually:\n')
        for _ in range(pickle.load(file)):
            print(pickle.load(file))

    with open('review_obj_2.pickle', 'rb') as file:
        print('for storing as array:\n')
        read_reviews = pickle.load(file)
        for review in read_reviews:
            print(review)


def test_load_reviews():
    reviews_path = 'review_objs.pickle'
    with open(reviews_path, 'rb') as file:
        reviews = pickle.load(file)
    for review in reviews:
        print(str(review))


def test_translate():
    ex = 'Today, is a very, very, good day. It\'s looking great!'
    ex_stripped = ex.translate(str.maketrans('', '', string.punctuation))
    print(f'before: {ex}\nafter: {ex_stripped}')

def test_sorting():
    word1 = WordRecord('wow', True)
    word1.tot_freq = 10
    word2 = WordRecord('wow2', True)
    word2.tot_freq = 20
    word3 = WordRecord('wow3', False)
    word3.tot_freq = 30

    sample_dict = {word1.word:word1, word3.word: word3, word2.word: word2}

    print('\nbefore:\n')
    for word_record in sample_dict.values():
        print(word_record)
    
    sorted_dict = dict(sorted(sample_dict.items(), key=lambda word_record: word_record[1].tot_freq))

    print('\nafter:\n')
    for word_record in sorted_dict.values():
        print(word_record)


if __name__ == '__main__':
    # run webscraper
    # if you never ran it before, you need to run it at least once on your machine for the analyser to work,
    # because analyser work with serialized reviews data file created by the scraper
    # adjust the show_ur, to a imdb url for a show of your liking
    # adjust user-agent, pls change it to your own or grab one from the internet that is for mac/pc

    # header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36'}
    # show_url = 'https://www.imdb.com/title/tt0944947/'
    # reviews_filename = 'review_objs.pickle'
    # sample_scraper = IMDBReviewsCollector(show_url, reviews_filename, header)
    # sample_scraper.gather_data()
    # run
    # reviews_path = 'review_objs.pickle'
    # stop_words_path = 'stopword.txt'
    # txt_output_path = 'model.txt'
    # removed_words_path = 'removed.txt'
    # dictionary_output_path = 'vocabulary_dictionary.pickle'
    sample_analyser = Analyser(reviews_path, stop_words_path, txt_output_path, dictionary_output_path)
    sample_analyser.compute_statistics(0)
    # sample_analyser.display_statistics()
    sample_analyser.classify(1, False)

    # START TASK 2.3
    # make new file
    text_file = open("length-result.txt", "w")
    text_file = open("length-model.txt", "w")
    text_file.close()
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

    #sample_analyser.vocabulary

    # sample_analyser.classify(1.6)
    #sample_analyser.classify(1.6)
    sample_analyser.classify(1)

    sample_analyser.classify(1.2)
    sample_analyser.classify(1.4)
    sample_analyser.classify(1.6)
    sample_analyser.classify(1.8)
    sample_analyser.classify(2.0)



    # sample_analyser.display_statistics()
    # sample_analyser.register_word_statistics()
    # sample_analyser.register_stop_word()
    # sample_analyser.classify(0.5)

    with open('result.txt', 'r') as file:
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
#    sample_analyser.infrequentWordFiltering()
#    sample_analyser.vocabulary
#
    # sample_analyser.display_statistics()
#     sample_analyser.register_word_statistics()
#     sample_analyser.register_stop_word()