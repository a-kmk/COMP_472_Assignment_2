import string
from bs4 import BeautifulSoup
from requests import get
from analyser import WordRecord
from webscraper import Review
import pickle


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

    sample_dict = {word1.word: word1, word3.word: word3, word2.word: word2}

    print('\nbefore:\n')
    for word_record in sample_dict.values():
        print(word_record)

    sorted_dict = dict(sorted(sample_dict.items(), key=lambda word_record: word_record[1].tot_freq))

    print('\nafter:\n')
    for word_record in sorted_dict.values():
        print(word_record)