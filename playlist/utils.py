import re
import os
from datetime import datetime, timedelta
from googleapiclient.discovery import build

from playlist.config import REGEX_PATTERN, MIN_VIDEO_NUMBER, MAX_VIDEO_NUMBER


class ProcessPlaylist:
    def __init__(self, playlist_url, from_video, to_video):
        self.playlist_url = playlist_url.strip()
        self.from_video = from_video if from_video else MIN_VIDEO_NUMBER
        self.to_video = to_video if to_video else MAX_VIDEO_NUMBER

        self.url_pattern = re.compile(REGEX_PATTERN.get("PLAYLIST"))

        self.hours_pattern = re.compile(REGEX_PATTERN.get("HOUR"))
        self.minutes_pattern = re.compile(REGEX_PATTERN.get("MINUTE"))
        self.seconds_pattern = re.compile(REGEX_PATTERN.get("SECOND"))

        self.total_seconds = 0
        self.nextPageToken = None
        self.connection = build(
            "youtube", "v3", developerKey=os.environ.get("YOUTUBE_API_KEY")
        )

        self.videos_details = []
        self.all_video_count = 0
        self.video_count = 0

    def get_playlist_id(self):
        playlist_id = self.url_pattern.match(self.playlist_url)

        if playlist_id:
            self.playlist_id = playlist_id.group(2)
            return True

    def get_playlist_info(self):
        if not self.get_playlist_id():
            return {"error": "Invalid playlist URL"}

        pl_request = self.connection.playlists().list(
            part="snippet",
            id=self.playlist_id,
            maxResults=50,
        )
        pl_response = pl_request.execute()

        if len(pl_response.get("items")) == 1:
            playlist_data = pl_response.get("items")[0].get("snippet")
            playlist_title = playlist_data.get("title")
            channel_title = playlist_data.get("channelTitle")

        while True:
            vid_response = {}
            pl_request = self.connection.playlistItems().list(
                part="contentDetails",
                playlistId=self.playlist_id,
                maxResults=50,
                pageToken=self.nextPageToken,
            )
            try:
                pl_response = pl_request.execute()
            except Exception:
                return {"error": "Invalid playlist URL"}

            vid_ids = []
            for item in pl_response["items"]:
                # only get the required video details by filtering with `from` and `to` number
                self.all_video_count += 1
                if self.all_video_count >= self.from_video and self.all_video_count <= self.to_video:
                    vid_ids.append(item["contentDetails"]["videoId"])

            if vid_ids:
                vid_request = self.connection.videos().list(
                    part="contentDetails,snippet,statistics", id=",".join(vid_ids)
                )
                try:
                    vid_response = vid_request.execute()
                except Exception:
                    return {"error": "Invalid playlist URL"}
            else:
                vid_response["items"] = []
            
            for item in vid_response["items"]:
                # Get & calculate video duration
                duration_string = item["contentDetails"]["duration"]
                video_seconds = self.get_video_duration(duration_string)

                self.total_seconds += video_seconds
                self.video_count += 1

                # Append video details to list
                video_detail = {
                    "view_count": int(item.get("statistics").get("viewCount"))
                    if item.get("statistics").get("viewCount")
                    else 0,
                    "like_count": int(item.get("statistics").get("likeCount"))
                    if item.get("statistics").get("likeCount")
                    else 0,
                    "comment_count": int(item.get("statistics").get("commentCount"))
                    if item.get("statistics").get("commentCount")
                    else 0,
                    "video_seconds": int(video_seconds),
                    "raw_video_duration": self.calculate_length(int(video_seconds)),
                    "uploaded_time": datetime.strptime(
                        item["snippet"]["publishedAt"], "%Y-%m-%dT%H:%M:%SZ"
                    ),
                    "title": item["snippet"]["title"],
                    "thumbnail": self.get_thumbnail_url(item["snippet"]["thumbnails"]),
                    "url": f"https://www.youtube.com/watch?v={item['id']}",
                }

                self.videos_details.append(video_detail)
            self.nextPageToken = pl_response.get("nextPageToken")

            if not self.nextPageToken:
                break

        self.total_seconds = int(self.total_seconds)

        if not self.total_seconds:
            return {"error": "No videos found!"}

        total_duration = {
            1: self.calculate_length(self.total_seconds),
            125: self.calculate_length(int(self.total_seconds / 1.25)),
            150: self.calculate_length(int(self.total_seconds / 1.50)),
            175: self.calculate_length(int(self.total_seconds / 1.75)),
            2: self.calculate_length(int(self.total_seconds / 2)),
        }

        most_viewed = sorted(
            self.videos_details, key=lambda data: data["view_count"], reverse=True
        )
        most_liked = sorted(
            self.videos_details, key=lambda data: data["like_count"], reverse=True
        )
        latest_first = sorted(
            self.videos_details, key=lambda data: data["uploaded_time"], reverse=True
        )
        oldest_first = sorted(
            self.videos_details, key=lambda data: data["uploaded_time"]
        )
        shortest_first = sorted(
            self.videos_details, key=lambda data: data["video_seconds"]
        )
        longest_first = sorted(
            self.videos_details, key=lambda data: data["video_seconds"], reverse=True
        )

        average_views = int(
            sum(map(lambda x: x["view_count"], self.videos_details))
            / len(self.videos_details)
            if len(self.videos_details) > 0
            else 0
        )
        average_likes = int(
            sum(map(lambda x: x["like_count"], self.videos_details))
            / len(self.videos_details)
            if len(self.videos_details) > 0
            else 0
        )
        average_comments = int(
            sum(map(lambda x: x["comment_count"], self.videos_details))
            / len(self.videos_details)
            if len(self.videos_details) > 0
            else 0
        )

        return {
            "playlist_title": playlist_title,
            "channel_title": channel_title,
            "average_views": average_views,
            "average_likes": average_likes,
            "average_comments": average_comments,
            "total_duration": total_duration,
            "video_count": self.video_count,
            "average_video_length": self.calculate_length(
                int(self.total_seconds / self.video_count)
            ),
            "most_viewed": most_viewed,
            "most_liked": most_liked,
            "latest_first": latest_first,
            "oldest_first": oldest_first,
            "shortest_first": shortest_first,
            "longest_first": longest_first,
        }

    def get_video_duration(self, duration_string):
        hours = self.hours_pattern.search(duration_string)
        minutes = self.minutes_pattern.search(duration_string)
        seconds = self.seconds_pattern.search(duration_string)

        hours = int(hours.group(1)) if hours else 0
        minutes = int(minutes.group(1)) if minutes else 0
        seconds = int(seconds.group(1)) if seconds else 0

        return timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds()

    def get_thumbnail_url(self, data):
        if data.get("maxres"):
            return data["maxres"]["url"]
        if data.get("standard"):
            return data["standard"]["url"]
        if data.get("high"):
            return data["high"]["url"]
        if data.get("medium"):
            return data["medium"]["url"]
        if data.get("default"):
            return data["default"]["url"]
        return "#"

    def calculate_length(self, seconds):
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)

        if hours > 0:
            return f"{hours} Hours, {minutes} Minutes, {seconds} Seconds"
        elif minutes > 0:
            return f"{minutes} Minutes, {seconds} Seconds"
        elif seconds > 0:
            return f"{seconds} Seconds"
        else:
            return "0 Second"


def get_playlist_details(playlist_url, from_video, to_video):
    obj = ProcessPlaylist(playlist_url, from_video, to_video)
    return obj.get_playlist_info()
