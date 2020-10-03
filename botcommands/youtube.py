from pytube import YouTube


def get_youtube(url):
    try:
        yt = YouTube(url)
        print(yt)
        payload = {"title": yt.title,
                   "author": yt.author,
                   "file": yt.streams.filter(subtype='mp4').get_highest_resolution().download(filename='yt')
                   }
        return payload
    except Exception as e:
        print(e)
        payload = {"title": "That video url didn't work.",
                   "author": "https://media.giphy.com/media/SFkjp1R8iRIWc/giphy.gif",
                   "file": ""
                   }
        return payload


if __name__ == "__main__":
    get_youtube('https://www.youtube.com/watch?v=dQw4w9WgXcQ')
