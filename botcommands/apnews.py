import xml.etree.ElementTree as ET
import requests


def get_top_ap_news(rss_url="https://news.google.com/rss/search?q=when:24h+allinurl:apnews.com", num_articles=5):
    msg = ""
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
    print(get_top_ap_news(num_articles=10))