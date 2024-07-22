from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from playlist.models import Feedback, Playlist


class PlaylistForm(forms.ModelForm):
    url = forms.CharField(
        max_length=500,
        widget=forms.TextInput(
            {
                "class": "form-control",
                "id": "playlist-url",
                "placeholder": "Enter a youtube playlist url",
            }
        ),
    )
    from_video = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            {
                "class": "form-control",
                "id": "from-video",
                "placeholder": "From",
            }
        ),
    )
    to_video = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(
            {
                "class": "form-control",
                "id": "to-video",
                "placeholder": "To",
            }
        ),
    )

    class Meta:
        model = Playlist
        fields = ["url"]

    def clean(self):
        cleaned_data = super().clean()

        if (
            cleaned_data.get("from_video")
            and cleaned_data.get("to_video")
            and cleaned_data["from_video"] > cleaned_data["to_video"]
        ):
            raise ValidationError(
                "The 'from' value must be less than or equal to the 'to' value."
            )
        return cleaned_data

    def clean_from_video(self):
        from_video = self.cleaned_data.get("from_video")
        if from_video is not None and from_video <= 0:
            raise ValidationError("The 'from' value must be a positive number")
        return from_video

    def clean_to_video(self):
        to_video = self.cleaned_data.get("to_video")
        if to_video is not None and to_video <= 0:
            raise ValidationError("The 'to' value must be a positive number")
        return to_video


class FeedbackForm(forms.ModelForm):
    feedback = forms.CharField(widget=forms.Textarea())

    class Meta:
        model = Feedback
        fields = ["feedback"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["feedback"].widget.attrs["rows"] = 10
        self.fields["feedback"].widget.attrs["class"] = "form-control"
