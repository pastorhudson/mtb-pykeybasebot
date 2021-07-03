# from pytube import YouTube
from __future__ import unicode_literals
from youtube_dl import YoutubeDL
import json
import os
from urllib.parse import urlparse
from pathlib import Path


def get_domain(url):
    # print(urlparse(url).netloc)
    return urlparse(url).netloc

info = []
storage = Path('./storage')
print(storage.absolute())


def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


class MyLogger(object):

    def info(self, msg):
        # print(f"Info: {msg}")
        pass

    def debug(self, msg):
        try:
            jmsg= json.loads(msg)
            info.append(jmsg)
        except Exception as e:
            # print(e)
            pass

    def warning(self, msg):
        # print(msg)
        pass

    def error(self, msg):
        print(msg)
        raise Exception


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def get_video(url, simulate):
    ydl_opts = {"forcejson": True,
                'logger': MyLogger(),
                'progress_hooks': [my_hook],
                'simulate': simulate,
                'format': 'mp4',
                'no-cache-dir': True,
                'outtmpl': f'{storage.absolute()}/%(title)s.%(ext)s'
                }
    domain = get_domain(url)

    if domain == 'youtube.com' or domain == 'youtu.be' or domain == 'www.youtube.com':
        info = []
        return get_youtube(url, simulate, ydl_opts)

    else:
        info = []
        return get_other_video(url, simulate, ydl_opts)


def get_mp3(url, simulate):
    ydl_opts = {"forcejson": True,
                'logger': MyLogger(),
                'progress_hooks': [my_hook],
                'simulate': simulate,
                'no-cache-dir': True,
                'format': 'bestaudio/best',
                'outtmpl': f'{storage.absolute()}/%(title)s.mp3',
                           'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                }
    domain = get_domain(url)
    if domain == 'youtube.com' or domain == 'youtu.be':
        info = []
        return get_youtube(url, simulate, ydl_opts)

    else:
        info = []
        return get_other_video(url, simulate, ydl_opts)


def get_other_video(url, simulate, ydl_opts):
    global info

    try:
        with YoutubeDL(ydl_opts) as ydl:
            dl = ydl.download([url])
        yt_info = info[0]
        # print(yt_info)
        payload = {"title": yt_info["fulltitle"],
                   "author": yt_info["uploader"],
                   "file": yt_info["_filename"],
                   "duration": convert_seconds(yt_info["duration"]),
                   'url': yt_info['webpage_url']
                   }
        msg = "\n".join(["```", yt_info["fulltitle"],
                         f"Author: {yt_info['uploader']}",
                         f"Duration: {convert_seconds(yt_info['duration'])}",
                         "```",
                         # yt_info['webpage_url']
                         ])
    except Exception as e:
        payload = {
            "file": None
        }
        msg = "I can't download videos from this site."
        info = []
    finally:
        payload['msg'] = msg
        info = []
        return payload


def get_youtube(url, simulate, ydl_opts):
    global info
    print(f"URL: {url}")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            dl = ydl.download([url])

        yt_info = info[0]
        # print(info)
        # for i in yt_info:
        #     print(yt_info[i])

        payload = {"title": yt_info["fulltitle"],
                   "author": yt_info["uploader"],
                   "file": f'{os.path.abspath("./")}/{yt_info["_filename"]}',
                   "duration": convert_seconds(yt_info["duration"]),
                   "views": yt_info['view_count'],
                   'url': yt_info['webpage_url']
                   }
        msg = "\n".join(["```", yt_info["fulltitle"],
                         f"Channel: {yt_info['uploader']}",
                         f"Duration: {convert_seconds(yt_info['duration'])}",
                         f"Views: {yt_info['view_count']}",
                         f"Average Rating: {yt_info['average_rating']}",
                         f"Likes: {yt_info['like_count']} Dislikes: {yt_info['dislike_count']}"
                         f"Age Limit: {yt_info['age_limit']}"
                         f"Quality: {yt_info['quality']}"
                         "```",
                         # yt_info['webpage_url']
                         ])
        # print(msg)
        payload['msg'] = msg
        info = []

        return payload
    except Exception as e:
        print(type(e))
        print(e)
        payload = {"msg": "That video url didn't work.\n"
                          "https://media.giphy.com/media/SFkjp1R8iRIWc/giphy.gif",
                   "file": ""
                   }
        info = []

        return payload


if __name__ == "__main__":
    print(get_video("https://www.youtube.com/watch?v=4mJayYlfcWo", simulate=True))
    pass

    # print(storage.absolute())
