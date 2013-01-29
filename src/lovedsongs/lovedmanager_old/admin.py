from django.contrib import admin
from lovedmanager.models import (Song, Image, Lyrics, TextBit, Post, CrawlUrl)


admin.site.register(Song)
admin.site.register(Image)
admin.site.register(Lyrics)
admin.site.register(TextBit)
admin.site.register(Post)
admin.site.register(CrawlUrl)