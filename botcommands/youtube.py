from pytube import YouTube


def get_youtube(url):
    print(url)
    yt = YouTube(url)
    print(yt.author)
    print(yt.title)
    payload = {"title": yt.title,
               "author": yt.author,
               "stream": yt.streams.filter(subtype='mp4').get_highest_resolution().download(filename='test.mp4')
               }
    print(payload)

    # print(yt.streams.filter(subtype='mp4').get_highest_resolution().url)


if __name__ == "__main__":
    get_youtube('https://www.youtube.com/watch?v=SkgTxQm9DWM')
