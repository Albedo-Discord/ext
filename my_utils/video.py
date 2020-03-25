import youtube_dl as ytdl
import discord
from my_utils.default import format_seconds
import re

YTDL_OPTS = {
    "default_search": "ytsearch",
    "format": "bestaudio/best",
    "quiet": True,
    "extract_flat": "in_playlist"
}


class Video:
    """Class containing information about a particular video."""

    def __init__(self, url_or_search, requested_by):
        """Plays audio from (or searches for) a URL."""
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
            video = self._get_info(url_or_search)
            video_format = video["formats"][0]
            self.stream_url = video_format["url"]
            self.video_url = video["webpage_url"]
            self.title = video["title"]
            self.clean_title = video["clean_title"]
            self.uploader = video["uploader"] if "uploader" in video else ""
            self.thumbnail = video[
                "thumbnail"] if "thumbnail" in video else None
            self.duration = video["duration"]
            self.requested_by = requested_by
# [6:09] - Eminem - Rap God (Explicit ft.) [Official Video] {gay} Lyric ft. juice worsadl
    def _get_info(self, video_url):
        with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
            info = ydl.extract_info(video_url, download=False)
            video = None
            if "_type" in info and info["_type"] == "playlist":
                return self._get_info(
                    info["entries"][0]["url"])  # get info for first video
            else:
                video = info
            escaper = re.compile(r'((\[|\(|\||\{)(.*?)(\}|\||\)|\])|lyrics?|video|ft\. .*)', re.IGNORECASE)               #? One of ma first re expressions! Matches the words which are contained in [], (), ||, {}
            video["clean_title"]  = escaper.sub(r'\0', video["title"])
            return video

    def get_embed(self):
        """Makes an embed out of this Video's information."""
        embed = discord.Embed(
            title=f"[{format_seconds(self.duration, 1)}] - {self.title}", description=self.uploader, url=self.video_url)
        embed.set_footer(
            text=f"Requested by {self.requested_by.name}",
            icon_url=self.requested_by.avatar_url)
        if self.thumbnail:
            embed.set_thumbnail(url=self.thumbnail)
        return embed
