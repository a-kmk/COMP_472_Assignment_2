from requests import get
from bs4 import BeautifulSoup
import csv


def display_url_error():
    print('You probably did not enter the correct URL of a TV show')


class IMDBReviewsCollector:
    def __init__(self, show_url):
        self.seasons = 0  # season number
        self.season_reviews_num = {}  # to keep track the review number of each season
        self.episodes = []  # to keep episodes objs {name, season, review_url, air_time(year)}
        self.reviews = []  # to keep reviews objs {title, rating, positive, content}
        self.total_words = 0 # for probability calculation
        self.negative_reviews = 0 # for probability calculation
        self.positive_reviews = 0 # for probability calculation
        self.url = show_url
        self.site_url = 'https://www.imdb.com/'
        self.episode_endpoint = 'episodes?season='
        self.review_endpoint = 'reviews'

    def get_season_num(self):
        show_page = get(self.url)
        html_soup = BeautifulSoup(show_page.text, 'html.parser')

        season_dropdown = html_soup.find('select', id='browse-episodes-season')
        # for show with many seasons we can find a dropdown selector with the number of seasons in its aria-label
        # attribute
        if season_dropdown is not None:
            self.seasons = int(season_dropdown['aria-label'][0])
        # for show with only 1 season, we can find a button which is a link, it shares class def with some other buttons
        # but it's always the second one among them
        else:
            season_button = html_soup.find_all('a', class_='ipc-button ipc-button--single-padding '
                                                           'ipc-button--center-align-content '
                                                           'ipc-button--default-height ipc-button--core-base '
                                                           'ipc-button--theme-base ipc-button--on-accent2 '
                                                           'ipc-text-button')
            if season_button is not None:
                self.seasons = season_button[1].div.string[0]
            else:
                display_url_error()

    def get_episodes(self, season_num):
        episodes_page = get(self.url + self.episode_endpoint + str(season_num))
        html_soup = BeautifulSoup(episodes_page.text, 'html.parser')
        episodes_list = html_soup.find('div', class_='list detail eplist')

        if episodes_list is not None:
            episodes = episodes_list.findChildren('div', class_='info')
            for episode in episodes:
                title_link = episode.strong.a
                name = title_link.string
                air_time = episode.find('div', class_='airdate').string.strip()
                review_url = self.site_url + title_link['href'] + self.review_endpoint
                self.episodes.append(Episode(name, season_num, review_url, air_time))
        else:
            display_url_error()

    # noinspection DuplicatedCode
    def get_reviews(self):
        if self.episodes:
            for episode in self.episodes:
                # dictionary with season as key and review num as value to check if each season has >= 50 reviews
                if (episode.season not in self.season_reviews_num):
                    self.season_reviews_num[episode.season] = 0

                reviews_page = get(episode.review_url)
                html_soup = BeautifulSoup(reviews_page.text, 'html.parser')
                reviews_list = html_soup.find('div', class_='lister-list')

                # the reviews list contains both spoiler and non-spoiler reviews
                reviews = reviews_list.findChildren('div', class_=lambda
                    x: x and 'lister-item mode-detail imdb-user-review' in x)

                for review in reviews:
                    self.season_reviews_num[episode.season] += 1
                    rating_element = review.find('span', class_='rating-other-user-rating')

                    # some episodes might have no review so we need to check for that
                    if rating_element is not None:
                        rating = int(rating_element.find_all('span')[0].string)
                        # title text contains a newline character for some reason
                        title = review.find('a', class_='title').string.strip()
                        # using get text to remove linebreak elements (br/)
                        content = review.find('div', class_='text show-more__control').get_text(separator=' ')
                        self.reviews.append(Review(title, rating, content))
        else:
            print('Need to get the episodes first')

    # adapted from https://realpython.com/python-csv/#writing-csv-files-with-csv
    # write the episode info to data.csv as per instruction
    def record_episodes(self):
        if self.episodes:
            with open('data.csv', mode='w') as file:
                fieldnames = ['Name', 'Season', 'Review Link', 'Year']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                writer.writeheader()
                for episode in self.episodes:
                    writer.writerow({'Name': episode.name, 'Season': episode.season, 'Review Link': episode.review_url,
                                     'Year': episode.air_time})
        else:
            print('Need to get the episodes first')

    # just to see if all the functions run correctly
    def gather_data(self):
        self.get_season_num()
        for i in range(self.seasons):
            self.get_episodes(i + 1)
        self.record_episodes()
        self.get_reviews()
        for review in self.reviews:
            print(str(review))

        all_over_50 = True
        for season in self.season_reviews_num:
            if self.season_reviews_num[season] < 50:
                all_over_50 = False
        print(f'Every season has over 50 episodes:{all_over_50}')


class Episode:
    def __init__(self, name, season, review_url, air_time):
        self.name = name
        self.season = season
        self.air_time = air_time.split()[-1]
        self.review_url = review_url


class Review:
    def __init__(self, title, rating, content):
        self.title = title
        self.rating = rating
        self.positive = True if rating >= 8 else False
        self.content = content

    def __str__(self):
        return f'\ntitle:{self.title}\nrating:{self.rating}\nis rating positive:{self.positive}\ncontent:{self.content}\n '
