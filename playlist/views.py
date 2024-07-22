from django.shortcuts import render, redirect
from django.contrib import messages

from playlist.forms import FeedbackForm, PlaylistForm
from playlist.models import Playlist
from playlist.utils import get_playlist_details


def sitemap_xml(request):
    return render(request, "playlist/sitemap.xml", content_type="application/xml")


def robots_txt(request):
    return render(request, "playlist/robots.txt", content_type="text/plain")


def ads_txt(request):
    return render(request, "playlist/ads.txt", content_type="text/plain")


def privacy_policy(request):
    return render(request, "playlist/privacy_policy.html")


def terms_and_conditions(request):
    return render(request, "playlist/terms_and_conditions.html")


def about_us(request):
    return render(request, "playlist/about_us.html")


def home(request):
    if request.method == "POST":
        form = PlaylistForm(request.POST)

        if form.is_valid():
            url = form.cleaned_data["url"]
            from_video = form.cleaned_data["from_video"]
            to_video = form.cleaned_data["to_video"]

            playlist_data = get_playlist_details(url, from_video, to_video)
            if playlist_data.get("error"):
                form.fields["url"].widget.attrs["class"] = "form-control is-invalid"
                name = "Invalid playlist"
                channel_name = "Invalid channel"
            else:
                form.fields["url"].widget.attrs["class"] = "form-control is-valid"
                form.fields["from_video"].widget.attrs[
                    "class"
                ] = "form-control is-valid"
                form.fields["to_video"].widget.attrs["class"] = "form-control is-valid"
                name = playlist_data.get("playlist_title")
                channel_name = playlist_data.get("channel_title")

            # Find the IP address of request
            try:
                ip_address = request.META.get("REMOTE_ADDR")
                x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
                if x_forwarded_for:
                    ip_address = x_forwarded_for.split(",")[0]
            except Exception as exe:
                ip_address = request.META.get("REMOTE_ADDR")

            metadata = {
                key: value
                for key, value in request.META.items()
                if type(value) in (str, int, bool, tuple, list)
            }

            # Update data in database
            playlist = Playlist.objects.create(
                url=url,
                name=name,
                ip_address=ip_address,
                metadata=metadata,
                from_video=from_video,
                to_video=to_video,
                channel_name=channel_name,
            )
            playlist.save()

            if not playlist_data.get("error"):
                messages.success(
                    request,
                    "Playlist data fetched successfully!",
                )
            else:
                messages.error(
                    request,
                    playlist_data.get("error"),
                )

            context = playlist_data | {"form": form}
            return render(request, "playlist/home.html", context=context)

        else:
            for field, error_list in form.errors.items():
                for error in error_list:
                    if field == "url":
                        form.fields["url"].widget.attrs[
                            "class"
                        ] = "form-control is-invalid"
                    elif field == "from_video":
                        form.fields["from_video"].widget.attrs[
                            "class"
                        ] = "form-control is-invalid"
                    elif field == "to_video":
                        form.fields["to_video"].widget.attrs[
                            "class"
                        ] = "form-control is-invalid"
                    if field == "__all__":
                        form.fields["from_video"].widget.attrs[
                            "class"
                        ] = "form-control is-invalid"
                        form.fields["to_video"].widget.attrs[
                            "class"
                        ] = "form-control is-invalid"
            return render(
                request, "playlist/home.html", context={"form": form, "error": True}
            )

    elif request.method == "GET":
        form = PlaylistForm()
        return render(request, "playlist/home.html", {"form": form})


def feedback(request):
    if request.method == "GET":
        form = FeedbackForm()
        return render(request, "playlist/feedback.html", {"form": form})
    elif request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Thanks for your feedback!",
            )
        return redirect("home")
