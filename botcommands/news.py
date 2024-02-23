import xml.etree.ElementTree as ET
import requests


def get_top_hacker_news(rss_url="https://news.ycombinator.com/rss", num_articles=5):
    msg = ""
    # RSS feed URL
    rss_url = 'https://news.ycombinator.com/rss'
    try:
        response = requests.get(rss_url)
        root = ET.fromstring(response.content)

        for num, item in enumerate(root.findall('.//item')[:num_articles]):
            title = item.find('title').text
            link = item.find('link').text
            msg += f"{num + 1}. {title}\n{link}\n\n"

    except Exception as e:
        print(f"An error occurred: {e}")

    return msg


if __name__ == '__main__':
    # Get and print the top 5 articles
    print(get_top_hacker_news(num_articles=10))
