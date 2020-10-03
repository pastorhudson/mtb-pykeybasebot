# from pytube import YouTube
from __future__ import unicode_literals
from youtube_dl import YoutubeDL
import json
import os

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
        info.append(msg)
        pass

    def warning(self, msg):
        # print(msg)
        pass

    def error(self, msg):
        print(msg)


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def get_youtube(url, simulate):
    ydl_opts = {"forcejson": True,
                'logger': MyLogger(),
                'progress_hooks': [my_hook],
                'simulate': simulate,
                'format': 'mp4',
                }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            dl = ydl.download([url])

        yt_info = json.loads(info[1])
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

        return payload
    except Exception as e:
        print(e)
        payload = {"msg": "That video url didn't work.\n"
                          "https://media.giphy.com/media/SFkjp1R8iRIWc/giphy.gif",
                   "file": ""
                   }
        return payload


if __name__ == "__main__":
    print(get_youtube('https://www.youtube.com/watch?v=QlTf5X0MKbg', True))
