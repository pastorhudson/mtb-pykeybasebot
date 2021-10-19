import json
import os
from pathlib import Path
from pprint import pprint

import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor

storage = Path('./storage')
# print(storage.absolute())
info = []
payload = {}


def sizeof_fmt(num, suffix="B"):
    for unit in [" ", " Ki", " Mi", " Gi", " Ti", " Pi", " Ei", " Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


def convert_seconds(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    return "%d:%02d:%02d" % (hour, minutes, seconds)


class MyLogger:
    def debug(self, msg):
        # For compatability with youtube-dl, both debug and info are passed into debug
        # You can distinguish them by the prefix '[debug] '
        if msg.startswith('[debug] '):
            pass
        else:
            self.info(msg)

    def info(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


class MyCustomPP(PostProcessor):

    def run(self, info):
        global payload
        filename = info['_filename'].replace('.m4a', '.mp3')
        filename = info['_filename'].replace('.webm', '.mp3')

        payload = {"title": info["title"],
                   # "author": yt_info["uploader"],
                   "file": filename,
                   "duration": convert_seconds(info["duration"]),
                   'url': info['webpage_url']
                   }
        file_size = os.path.getsize(filename)

        try:
            msg = "```"
            msg += info["title"] + '\n'
            try:
                msg += f"Channel: {info['uploader']}\n"
            except KeyError:
                pass
            try:
                msg += f"Duration: {convert_seconds(info['duration'])}\n"
            except KeyError:
                pass
            try:
                msg += f"Views: {info['view_count']:,}\n"
            except KeyError:
                pass
            try:
                msg += f"Average Rating: {info['average_rating']}\n"
            except KeyError:
                pass
            try:
                msg += f"Likes: {info['like_count']:,} Dislikes: {info['dislike_count']:,}\n"
            except KeyError:
                pass
            try:
                msg += f"Size: {sizeof_fmt(file_size)}\n"
            except KeyError:
                pass
            msg += "```"

        except Exception as e:
            print(e)

        payload['msg'] = msg
        return [], info


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def get_mp3(url):
    global payload
    payload = {}

    ydl_opts = {
        'format': 'bestaudio/best',
        'restrictfilenames': True,
        'outtmpl': f'{storage.absolute()}/%(title)s.%(ext)s',
        'forcefilename': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.add_post_processor(MyCustomPP())
        info = ydl.extract_info(url)
        # print(json.dumps(ydl.sanitize_info(info)))
    return payload


def get_mp4(url):
    global info
    global payload
    ydl_opts = {
        # 'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b', #old
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'restrictfilenames': True,
        'outtmpl': f'{storage.absolute()}/%(title)s.%(ext)s',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.add_post_processor(MyCustomPP())
        yt_info = ydl.extract_info(url)
        # pprint(json.dumps(ydl.sanitize_info(yt_info)))
    return payload


def get_meta(url):
    global info

    ydl_opts = {
        # 'format': 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4] / bv*+ba/b', #old
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'simulate': True,
        'restrictfilenames': True,
        'outtmpl': f'{storage.absolute()}/%(title)s.%(ext)s',
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.add_post_processor(MyCustomPP())
            yt_info = ydl.extract_info(url)
            # pprint(yt_info)
            payload = {"title": yt_info["title"],
                       "file": None,
                       "duration": convert_seconds(yt_info["duration"]),
                       'url': yt_info['webpage_url']
                       }
            try:
                msg = "```"
                msg += yt_info["title"] + '\n'
                try:
                    msg += f"Channel: {yt_info['uploader']}\n"
                except KeyError:
                    pass
                try:
                    msg += f"Duration: {convert_seconds(yt_info['duration'])}\n"
                except KeyError:
                    pass
                try:
                    msg += f"Views: {yt_info['view_count']:,}\n"
                except KeyError:
                    pass
                try:
                    msg += f"Average Rating: {yt_info['average_rating']}\n"
                except KeyError:
                    pass
                try:
                    msg += f"Likes: {yt_info['like_count']:,} Dislikes: {yt_info['dislike_count']:,}\n"
                except KeyError:
                    pass
                msg += "```"
            except Exception as e:
                print(e)

            payload['msg'] = msg
        except Exception as e:
            payload = {"msg": "That video url didn't work.\n"
                              "https://media.giphy.com/media/SFkjp1R8iRIWc/giphy.gif",
                       "file": ""
                       }

        return payload


if __name__ == '__main__':
    print(get_mp4('https://www.reddit.com/r/ArduinoProjects/comments/qalpk6/msgeq7_and_arduino_uno_music_leds/'))
    # get_meta('https://www.cnn.com/2021/10/18/politics/covid-vaccines-colin-powell-what-matters/index.html')
    # print(get_mp4('https://www.cnn.com/2021/10/18/politics/covid-vaccines-colin-powell-what-matters/index.html'))
