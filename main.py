from webscraper import IMDBReviewsCollector
from bs4 import BeautifulSoup
from requests import get


# the functions here are just for testing purposes, change show_url in main and run it to see reviews and episodes
# info getting gathered, shouldn't run into errors but it might run for quite a while (> 20s)
def test_season():
    wire_url = 'https://www.imdb.com/title/tt0306414/'
    response = get(wire_url)
    html_soup = BeautifulSoup(response.text, 'html.parser')
    # browse-episodes-season
    season_dropdown = html_soup.find('select', id='browse-episodes-season')
    print(season_dropdown['aria-label'][0])


def test_only_one_season():
    one_season_url = 'https://www.imdb.com/title/tt2006848/'
    response = get(one_season_url)
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

    response = get(url + episode_endpoint + str(season_num))
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
    response = get('https://www.imdb.com/title/tt5924366/reviews')
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


if __name__ == '__main__':
    show_url = 'https://www.imdb.com/title/tt0306414/'
    sample_scraper = IMDBReviewsCollector(show_url)
    sample_scraper.gather_data()
