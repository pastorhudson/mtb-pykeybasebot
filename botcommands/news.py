import xml.etree.ElementTree as ET
import requests


def get_top_hacker_news(rss_url="https://news.ycombinator.com/rss", num_articles=5):
    # RSS feed URL
    rss_url = 'https://news.ycombinator.com/rss'
    try:
        response = requests.get(rss_url)
        root = ET.fromstring(response.content)

        for item in root.findall('.//item')[:num_articles]:
            title = item.find('title').text
            link = item.find('link').text
            print(f"Title: {title}\nURL: {link}\n")

    except Exception as e:
        print(f"An error occurred: {e}")




if __name__ == '__main__':
    # Get and print the top 5 articles
    get_top_hacker_news(rss_url)
