import json
import logging
import os
from pathlib import Path
from pprint import pprint
import webvtt
import yt_dlp
from yt_dlp.postprocessor.common import PostProcessor

storage = Path('./storage')
# cookies = Path('/app/botcommands/cookies.txt')
# proxy_url = os.environ.get('PROXY_URL')
info = []
payload = {}


def is_supported(url):
    extractors = yt_dlp.extractor.gen_extractors()
    for e in extractors:
        # print(e.suitable(url))
        # if e.suitable(url) and e.IE_NAME != 'generic':
        if e.suitable(url):
            return True
    return False


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
        logging.info(msg)
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        logging.error(msg)


class MyCustomPP(PostProcessor):

    def run(self, info):
        global payload
        logging.info("I'm running post processor")
        filename = info['filepath']

        logging.info(f"FILENAME: {filename}")
        # Access the upload date from the 'info' dictionary
        upload_date = info['upload_date']

        if upload_date:
            # Format the date if needed, here it is kept in YYYYMMDD format
            formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
        else:
            formatted_date = "Unknown"
        try:
            """We're going to try to get subtitles"""
            payload = {"title": info["title"],
                       # "author": yt_info["uploader"],
                       "file": filename,
                       'transcript': extract_transcript_from_vtt(info['requested_subtitles']['en']['filepath']),
                       "duration": convert_seconds(info["duration"]),
                       "upload_date": formatted_date,  # Add this line
                       'url': info['webpage_url']
                       }

        except (KeyError, TypeError):
            """We can't get subs"""
            payload = {"title": info["title"],
                       # "author": yt_info["uploader"],
                       "file": filename,
                       'transcript': None,
                       "duration": convert_seconds(info["duration"]),
                       "upload_date": formatted_date,  # Add this line
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
                msg += f"Upload Date: {formatted_date}\n"
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
            logging.info(e)

        payload['msg'] = msg
        return [], info


def my_hook(d):
    if d['status'] == 'finished':
        print('Done downloading, now converting ...')


def get_mp3(url):
    global payload
    if not is_supported(url):
        return {"msg": "That video url didn't work.\n"
                       "https://media.giphy.com/media/SFkjp1R8iRIWc/giphy.gif",
                "file": ""
                }
    payload = {}

    ydl_opts = {
        'format': 'bestaudio/best',

        'restrictfilenames': True,
        'writeautomaticsub': True,  # Download auto-generated subtitles
        'subtitleslangs': ['en'],  # Language code for the subtitles (e.g., 'en' for English)
        'outtmpl': f'{storage.absolute()}/%(title).50s.%(ext)s',
        'forcefilename': True,
        'ffmpeg_location': '/app/vendor/ffmpeg/ffmpeg',
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


async def get_mp4(url):
    """
    Enhanced video download function with better error handling and fallback options.
    """
    try:
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'merge_output_format': 'mp4',
            'outtmpl': '/app/storage/%(title)s.%(ext)s',
            'quiet': False,
            'no_warnings': True,
            # Add fallback formats
            'format_sort': ['res:1080', 'res:720', 'res:480'],
            'postprocessor_args': ['-codec:v', 'libx264', '-codec:a', 'aac'],
            'retries': 3
        }

        # First attempt with high quality
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
                return {
                    'file': f"/app/storage/{info['title']}.mp4",
                    'msg': f"Downloaded: {info['title']}"
                }
            except yt_dlp.utils.DownloadError as e:
                logging.warning(f"High quality download failed, trying fallback: {str(e)}")

                # Fallback to simpler format
                ydl_opts.update({
                    'format': 'best[ext=mp4]/best',
                    'merge_output_format': 'mp4'
                })

                with yt_dlp.YoutubeDL(ydl_opts) as ydl_fallback:
                    info = ydl_fallback.extract_info(url, download=True)
                    return {
                        'file': f"/app/storage/{info['title']}.mp4",
                        'msg': f"Downloaded: {info['title']} (fallback quality)"
                    }

    except Exception as e:
        logging.error(f"Video download failed: {str(e)}")
        return {
            'file': None,
            'msg': "Failed to download video. The format may be unsupported or the video may be restricted."
        }

# def get_mp4(url):
#     global info
#     global payload
#     info = {}
#     payload = {}
#
#     if not is_supported(url):
#         return {"msg": "That video url didn't work.\n"
#                        "https://media.giphy.com/media/SFkjp1R8iRIWc/giphy.gif",
#                 "file": ""
#                 }
#
#     ydl_opts = {
#         'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
#         'merge_output_format': 'mp4',    # Final merged file format
#         'postprocessors': [
#             {  # Use FFmpeg to merge video and audio
#                 'key': 'FFmpegMerger',
#             }
#         ],
#         'writethumbnail': True,
#         'restrictfilenames': True,
#         'writeautomaticsub': True,  # Download auto-generated subtitles
#         'subtitleslangs': ['en'],  # Language code for the subtitles (e.g., 'en' for English)
#         'outtmpl': f'{storage.absolute()}/%(title).50s.%(ext)s',
#         'windowsfilenames': True,
#
#         'ffmpeg_location': '/app/vendor/ffmpeg/ffmpeg',
#
#         'logger': MyLogger(),
#         'progress_hooks': [my_hook],
#     }
#
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         ydl.add_post_processor(MyCustomPP(), when='post_process')
#
#         yt_info = ydl.extract_info(url)
#         # pprint(yt_info)
#     return payload


def get_meta(url):
    global info
    if not is_supported(url):
        return {"msg": "That video url didn't work.\n"
                       "https://media.giphy.com/media/SFkjp1R8iRIWc/giphy.gif",
                "file": ""
                }
    ydl_opts = {
        # 'format': 'bestvideo[ext=mp4][vcodec=h264]+bestaudio[ext=m4a][acodec=aac]/best[ext=mp4]/best',
        # 'format': 'bestvideo+bestaudio/best',

        # 'proxy': proxy_url,
        # 'cookies': cookies.absolute(),
        # 'postprocessors': [
            # {'key': 'SponsorBlock'},
            # {'key': 'ModifyChapters',
            #  'remove_sponsor_segments': ['sponsor', 'intro', 'outro', 'selfpromo', 'preview', 'filler', 'interaction']},
            # {
            #     'key': 'FFmpegVideoConvertor',
            #     'preferedformat': 'mp4'  # Convert final file to mp4
            # }
        # ],
        'writeautomaticsub': True,  # Download auto-generated subtitles
        'subtitleslangs': ['en'],  # Language code for the subtitles (e.g., 'en' for English)
        'writethumbnail': True,
        'restrictfilenames': True,
        'outtmpl': f'{storage.absolute()}/%(title).50s.%(ext)s',
        'windowsfilenames': True,

        'ffmpeg_location': '/app/vendor/ffmpeg/ffmpeg',
        # 'ffmpeg_location': 'C://tools//ffmpeg-6.1-full_build//bin//ffmpeg.exe',

        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }
    ydl_opts_no_subs = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'merge_output_format': 'mp4',  # Final merged file format
        'postprocessors': [
            {  # Use FFmpeg to merge video and audio
                'key': 'FFmpegMerger',
            }
        ],
        # 'postprocessors': [
            # {'key': 'SponsorBlock'},
            # {'key': 'ModifyChapters',
            #  'remove_sponsor_segments': ['sponsor', 'intro', 'outro', 'selfpromo', 'preview', 'filler',
            #                              'interaction']},
            # {
            #     'key': 'FFmpegVideoConvertor',
            #     'preferedformat': 'mp4'  # Convert final file to mp4
            # }
        # ],
        'writeautomaticsub': True,  # Download auto-generated subtitles
        # 'subtitleslangs': ['en'],  # Language code for the subtitles (e.g., 'en' for English)
        'writethumbnail': True,
        'restrictfilenames': True,
        'outtmpl': f'{storage.absolute()}/%(title).50s.%(ext)s',
        'windowsfilenames': True,

        'ffmpeg_location': '/app/vendor/ffmpeg/ffmpeg',
        # 'ffmpeg_location': 'C://tools//ffmpeg-6.1-full_build//bin//ffmpeg.exe',

        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }


    with yt_dlp.YoutubeDL(ydl_opts_no_subs) as ydl:
        try:
            ydl.add_post_processor(MyCustomPP())
            yt_info = ydl.extract_info(url)
            upload_date = yt_info['upload_date']

            if upload_date:
                # print('HERE')
                # Format the date if needed, here it is kept in YYYYMMDD format
                formatted_date = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
            else:
                formatted_date = "Unknown"
            try:
                payload = {"title": yt_info["title"],
                           "file": None,
                           'transcript': extract_transcript_from_vtt(yt_info['requested_subtitles']['en']['filepath']),
                           "duration": convert_seconds(yt_info["duration"]),
                           "upload_date": formatted_date,
                           'url': yt_info['webpage_url']
                           }
            except Exception as e:

                payload = {"title": yt_info["title"],
                           "file": None,
                           'transcript': None,
                           "duration": convert_seconds(yt_info["duration"]),
                           "upload_date": formatted_date,
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
                    msg += f"Uploaded: {formatted_date}\n"
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
                # print(yt_info)

                logging.info(e)
                logging.info(msg)

            payload['msg'] = msg
        except Exception as e:
            print(e)
            payload = {"msg": "That video url didn't work.\n"
                              "https://media.giphy.com/media/SFkjp1R8iRIWc/giphy.gif",
                       "file": ""
                       }

        return payload


def extract_transcript_from_vtt(vtt_file):

    vtt = webvtt.read(vtt_file)
    transcript = ""

    lines = []
    for line in vtt:
        # Strip the newlines from the end of the text.
        # Split the string if it has a newline in the middle
        # Add the lines to an array
        lines.extend(line.text.strip().splitlines())

    # Remove repeated lines
    previous = None
    for line in lines:
        if line == previous:
            continue
        transcript += " " + line
        previous = line

    return transcript


if __name__ == '__main__':
    # print(get_mp4('https://twitter.com/klasfeldreports/status/1450874629338324994?s=21'))
    # print(get_meta('https://www.youtube.com/watch?v=bBDNN8SyL98'))

    # print(get_mp4('https://fb.watch/ffBAHvNt1A/'))
    # meta = get_meta('https://youtu.be/w0ZHlp6atUQ?si=qhGgjVxVrl0olCyZ')
    # pprint(meta)
    # vtt_file = meta['title'].replace(' ', '_') + ".en.vtt"
    # print(vtt_file)
    # vtt_file = 'C://Users//geekt//PycharmProjects//2021//mtb-pykeybasebot//botcommands//storage//A_long-winded_1-year_ownership_report_on_my_Hyunda.en.vtt'  # Replace with the path to your VTT file
    # transcript = extract_transcript_from_vtt(vtt_file)
    # print(transcript)
    pass
