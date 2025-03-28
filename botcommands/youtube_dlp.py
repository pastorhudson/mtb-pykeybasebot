from pathlib import Path
from yt_dlp.postprocessor.common import PostProcessor
import os
import re
import logging
import yt_dlp

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
    Enhanced video download function with filename sanitization including space to underscore conversion.
    """

    def sanitize_filename(filename):
        """
        Sanitize filename to remove or replace problematic characters.
        Converts spaces to underscores and handles special characters.
        """
        # Replace vertical bars and other special characters with hyphen
        filename = re.sub(r'[|｜]', '-', filename)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Replace other problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '-', filename)
        # Replace multiple hyphens with single hyphen
        filename = re.sub(r'-+', '-', filename)
        # Replace multiple underscores with single underscore
        filename = re.sub(r'_+', '_', filename)
        # Remove any trailing/leading hyphens or underscores
        filename = filename.strip('-_')
        return filename

    try:
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': '/app/storage/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'postprocessor_args': [
                '-c', 'copy',  # Copy streams without re-encoding
                '-movflags', '+faststart'
            ],
            'retries': 3
        }

        # First attempt with preferred formats
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)  # First get info without downloading
                # Sanitize the filename before download
                sanitized_title = sanitize_filename(info['title'])
                ydl_opts['outtmpl'] = f'/app/storage/{sanitized_title}.%(ext)s'

                # Now download with sanitized filename
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_download:
                    info = ydl_download.extract_info(url, download=True)
                    output_file = f"/app/storage/{sanitized_title}.mp4"

                    # Verify file exists before returning
                    if os.path.exists(output_file):
                        return {
                            'file': output_file,
                            'msg': f"Downloaded: {info['title']}"  # Use original title in message
                        }
                    else:
                        raise FileNotFoundError(f"Output file not found: {output_file}")

            except (yt_dlp.utils.DownloadError, FileNotFoundError) as e:
                logging.warning(f"Preferred format download failed, trying fallback: {str(e)}")

                # Fallback to simpler format if needed
                ydl_opts.update({
                    'format': 'best',
                })

                with yt_dlp.YoutubeDL(ydl_opts) as ydl_fallback:
                    info = ydl_fallback.extract_info(url, download=True)
                    return {
                        'file': f"/app/storage/{sanitized_title}.mp4",
                        'msg': f"Downloaded: {info['title']} (fallback format)"  # Use original title in message
                    }

    except Exception as e:
        logging.error(f"Video download failed: {str(e)}")
        return {
            'file': None,
            'msg': f"Failed to download video: {str(e)}"
        }





async def get_mp4_tool(url):
    """
    Enhanced video download function with filename sanitization including space to underscore conversion.
    """

    def sanitize_filename(filename):
        """
        Sanitize filename to remove or replace problematic characters.
        Converts spaces to underscores and handles special characters.
        """
        # Replace vertical bars and other special characters with hyphen
        filename = re.sub(r'[|｜]', '-', filename)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Replace other problematic characters
        filename = re.sub(r'[<>:"/\\|?*]', '-', filename)
        # Replace multiple hyphens with single hyphen
        filename = re.sub(r'-+', '-', filename)
        # Replace multiple underscores with single underscore
        filename = re.sub(r'_+', '_', filename)
        # Remove any trailing/leading hyphens or underscores
        filename = filename.strip('-_')
        return filename

    try:
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'merge_output_format': 'mp4',
            'outtmpl': '/app/storage/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'postprocessor_args': [
                '-c', 'copy',  # Copy streams without re-encoding
                '-movflags', '+faststart'
            ],
            'retries': 3
        }

        # First attempt with preferred formats
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)  # First get info without downloading
                # Sanitize the filename before download
                sanitized_title = sanitize_filename(info['title'])
                ydl_opts['outtmpl'] = f'/app/storage/{sanitized_title}.%(ext)s'

                # Now download with sanitized filename
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_download:
                    info = ydl_download.extract_info(url, download=True)
                    output_file = f"/app/storage/{sanitized_title}.mp4"

                    # Verify file exists before returning
                    if os.path.exists(output_file):
                        logging.info(f"Successfully downloaded video to {output_file}")
                        return {
                            'msg': f"Downloaded: {info['title']}",  # Use original title in message
                            'file': output_file
                        }
                    else:
                        raise FileNotFoundError(f"Output file not found: {output_file}")

            except (yt_dlp.utils.DownloadError, FileNotFoundError) as e:
                logging.warning(f"Preferred format download failed, trying fallback: {str(e)}")

                # Fallback to simpler format if needed
                ydl_opts.update({
                    'format': 'best',
                })

                with yt_dlp.YoutubeDL(ydl_opts) as ydl_fallback:
                    info = ydl_fallback.extract_info(url, download=True)
                    output_file = f"/app/storage/{sanitize_filename(info['title'])}.mp4"

                    # Verify file exists before returning
                    if os.path.exists(output_file):
                        logging.info(f"Successfully downloaded video (fallback) to {output_file}")
                        return {
                            'msg': f"Downloaded: {info['title']} (fallback format)",
                            'file': output_file
                        }
                    else:
                        return f"⚠️ Failed to download video: File not created"

    except Exception as e:
        logging.error(f"Video download failed: {str(e)}")
        return f"⚠️ Failed to download video: {str(e)}"

def get_meta(url, storage_path=storage):
    """
    Retrieve metadata and transcript from a YouTube video.

    Args:
        url (str): YouTube video URL
        storage_path (Path): Path to store temporary subtitle files

    Returns:
        dict: Dictionary containing video metadata and transcript
    """
    ydl_opts = {
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        'writethumbnail': False,  # We don't need thumbnails
        'restrictfilenames': True,
        'outtmpl': f'{storage_path.absolute()}/%(title).50s.%(ext)s',
        'windowsfilenames': True,
        'skip_download': True,  # Skip video download but allow subtitle download
        'writesubtitles': True,  # Write the subtitles file
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract video information
            yt_info = ydl.extract_info(url, download=False)

            # Format upload date
            upload_date = yt_info.get('upload_date')
            formatted_date = (f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
                              if upload_date else "Unknown")

            # Try to get transcript if available
            transcript = None
            try:
                # Download info first to get potential subtitle info
                info = ydl.extract_info(url, download=False)
                if info.get('subtitles') or info.get('automatic_captions'):
                    # Now download with subtitles
                    info = ydl.extract_info(url, download=True)
                    # Find the subtitle file
                    subtitle_files = [f for f in Path(storage_path).glob("*.vtt")]
                    if subtitle_files:
                        transcript = extract_transcript_from_vtt(subtitle_files[0])
                        # Clean up subtitle file after reading
                        subtitle_files[0].unlink()
            except Exception as e:
                logging.error(f"Failed to extract transcript: {e}")

            # Prepare metadata message
            metadata_msg = [
                "```",
                yt_info["title"],
                f"Channel: {yt_info.get('uploader', 'Unknown')}",
                f"Uploaded: {formatted_date}",
                f"Duration: {convert_seconds(yt_info.get('duration', 0))}",
                f"Views: {yt_info.get('view_count', 0):,}",
            ]

            # Add optional metadata if available
            if 'average_rating' in yt_info:
                metadata_msg.append(f"Average Rating: {yt_info['average_rating']}")
            if 'like_count' in yt_info:
                metadata_msg.append(f"Likes: {yt_info['like_count']:,}")

            metadata_msg.append("```")

            return {
                "title": yt_info["title"],
                "transcript": transcript,
                "duration": convert_seconds(yt_info.get('duration', 0)),
                "upload_date": formatted_date,
                "url": yt_info['webpage_url'],
                "msg": "\n".join(metadata_msg)
            }

        except Exception as e:
            logging.error(f"Failed to extract video information: {e}")
            return {
                "msg": "Failed to retrieve video metadata.",
                "transcript": None
            }


def convert_seconds(seconds):
    """Convert seconds to HH:MM:SS format"""
    if not seconds:
        return "00:00"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{minutes:02d}:{seconds:02d}"


def extract_transcript_from_vtt(vtt_path):
    """Extract text content from VTT file"""
    try:
        with open(vtt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Basic VTT parsing - you might want to enhance this
            lines = [line.strip() for line in content.split('\n')
                     if line.strip() and not line.strip().isdigit()
                     and not '-->' in line
                     and not line.strip() == 'WEBVTT']
            return ' '.join(lines)
    except Exception as e:
        logging.error(f"Failed to parse VTT file: {e}")
        return None

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
    print(get_meta('https://www.youtube.com/watch?v=gqupdjbzs0M'))
    pass
