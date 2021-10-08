# from pytube import YouTube
from __future__ import unicode_literals

from pprint import pprint

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
                'restrictfilenames': True,
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
                # 'format': 'bestaudio',
                'restrictfilenames': True,
                'extractaudio': True,
                'audioformat': 'mp3',
                'audioquality': 0,
                'writethumbnail': True,
                'outtmpl': f'{storage.absolute()}/%(title)s.%(ext)s',
                           'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                }
    domain = get_domain(url)
    if domain == 'youtube.com' or domain == 'youtu.be' or domain == 'www.youtube.com':
        info = []
        payload = get_youtube(url, simulate, ydl_opts)
        pre, ext = os.path.splitext(payload['file'])
        payload['file'] = pre + '.mp3'
        return payload

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
        print(payload)
        info = []
        return payload


def sizeof_fmt(num, suffix="B"):
    for unit in [" ", " Ki", " Mi", " Gi", " Ti", " Pi", " Ei", " Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def get_youtube(url, simulate, ydl_opts):
    global info
    print(f"URL: {url}")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            dl = ydl.download([url])

        yt_info = info[0]

        payload = {"title": yt_info["fulltitle"],
                   "author": yt_info["uploader"],
                   "file": f'{yt_info["_filename"]}',
                   "duration": convert_seconds(yt_info["duration"]),
                   "views": yt_info['view_count'],
                   'url': yt_info['webpage_url']
                   }
        if not simulate:
            file_size = os.path.getsize(yt_info["_filename"])
            msg = "\n".join(["```", yt_info["fulltitle"],
                             f"Channel: {yt_info['uploader']}",
                             f"Duration: {convert_seconds(yt_info['duration'])}",
                             f"Views: {yt_info['view_count']:,}",
                             f"Average Rating: {yt_info['average_rating']}",
                             f"Likes: {yt_info['like_count']:,} Dislikes: {yt_info['dislike_count']:,}",
                             f"Age Limit: {yt_info['age_limit']} ",
                             f"Size: {sizeof_fmt(file_size)}",
                             "```",
                             # yt_info['webpage_url']
                             ])
        else:
            msg = "\n".join(["```", yt_info["fulltitle"],
                             f"Channel: {yt_info['uploader']}",
                             f"Duration: {convert_seconds(yt_info['duration'])}",
                             f"Views: {yt_info['view_count']:,}",
                             f"Average Rating: {yt_info['average_rating']}",
                             f"Likes: {yt_info['like_count']:,} Dislikes: {yt_info['dislike_count']:,}",
                             f"Age Limit: {yt_info['age_limit']} ",
                             "```",
                             ])
        payload['msg'] = msg
        info = []
        pprint(payload)
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
    pprint(get_video('https://youtu.be/DgeovMetvZQ', simulate=True))
    pass

    # print(storage.absolute())
