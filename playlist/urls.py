from django.contrib import admin
from django.urls import path, include

from playlist.views import (
    home,
    robots_txt,
    sitemap_xml,
    privacy_policy,
    terms_and_conditions,
    about_us,
    ads_txt,
)

urlpatterns = [
    path("", home, name="home"),
    # path("feedback/", feedback, name="feedback"),
    path("sitemap.xml", sitemap_xml, name="sitemap_xml"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("ads.txt", ads_txt, name="ads_txt"),
    path("privacy-policy", privacy_policy, name="privacy_policy"),
    path("terms-and-conditions", terms_and_conditions, name="terms_and_conditions"),
    path("about-us", about_us, name="about_us"),
]
