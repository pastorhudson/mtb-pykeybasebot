# from pytube import YouTube
from __future__ import unicode_literals
from youtube_dl import YoutubeDL
import json
import os
from urllib.parse import urlparse


def get_domain(url):
    # print(urlparse(url).netloc)
    return urlparse(url).netloc

info = []


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
    domain = get_domain(url)
    if domain == 'youtube.com' or domain == 'youtu.be':
        info = []
        return get_youtube(url, simulate)

    else:
        info = []
        return get_other_video(url, simulate)


def get_other_video(url, simulate):
    global info
    ydl_opts = {"forcejson": True,
                'logger': MyLogger(),
                'progress_hooks': [my_hook],
                'simulate': simulate,
                'format': 'mp4',
                'no-cache-dir': True,
                }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            dl = ydl.download([url])
        yt_info = info[0]
        payload = {"title": yt_info["fulltitle"],
                   "author": yt_info["uploader"],
                   "file": f'{os.path.abspath("./")}/{yt_info["_filename"]}',
                   "duration": convert_seconds(yt_info["duration"]),
                   'url': yt_info['webpage_url']
                   }
        msg = "\n".join(["```", yt_info["fulltitle"],
                         f"Author: {yt_info['uploader']}",
                         f"Duration: {convert_seconds(yt_info['duration'])}",
                         "```",
                         yt_info['webpage_url']])
    except Exception as e:
        payload = {
            "file": None
        }
        msg = "I can't download videos from this site."
    finally:
        payload['msg'] = msg
        info = []
        return payload


def get_youtube(url, simulate):
    global info
    print(f"URL: {url}")
    ydl_opts = {"forcejson": True,
                'logger': MyLogger(),
                'progress_hooks': [my_hook],
                'simulate': simulate,
                'format': 'mp4',
                'no-cache-dir': True,
                }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            dl = ydl.download([url])

        yt_info = info[0]
        print(info)
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
                         "```",
                         yt_info['webpage_url']])
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
    # print(get_youtube('https://www.youtube.com/watch?v=WcWA1LoeWU4', True))
    # print(get_youtube('https://www.youtube.com/watch?v=u95wgmBZ99A', True))
    # print(get_youtube('https://www.youtube.com/watch?v=UZPPVfMrfug', True))
    # print(get_youtube('https://www.dailymotion.com/video/x7wl5ns', False))
    print(get_video("https://twitter.com/realDonaldTrump/status/1313267615083761665", False))
    # print(get_video("https://youtu.be/R3kkpVbOcsA", True))
    # print(get_youtube('https://www.cnn.com/2020/10/02/politics/kellyanne-conway-positive-for-covid-19/index.html', True))


