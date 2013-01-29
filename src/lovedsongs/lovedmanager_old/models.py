from django.db import models


class DownloadedResourceMixin(models.Model):
    source_url = models.CharField(max_length=255, blank=True, null=True)
    data_downloaded = models.DateTimeField(auto_now_add=True)
    local_filename = models.CharField(max_length=255)

    class Meta:
        abstract = True


class StatusMixin(models.Model):
    status = models.IntegerField(blank=True, null=True)
    error_text = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class Song(DownloadedResourceMixin):
    pass


class Image(DownloadedResourceMixin):
    song = models.ForeignKey(Song)
    inspired_by = models.CharField(max_length=255, blank=True, null=True)


class Lyrics(DownloadedResourceMixin):
    text = models.TextField()
    song = models.ForeignKey(Song)


class TextBit(DownloadedResourceMixin):
    text = models.TextField()
    song = models.ForeignKey(Song)
    inspired_by = models.CharField(max_length=255, blank=True, null=True)


class Post(StatusMixin):
    song = models.ForeignKey(Song)
    approved_lyrics = models.ForeignKey(Lyrics)
    approved_images = models.ManyToManyField(Image)
    approved_textbits = models.ManyToManyField(TextBit)
    date_approved = models.DateTimeField(auto_now_add=True)
    date_started_processing = models.DateTimeField()
    date_created_video = models.DateTimeField()
    date_posted = models.DateTimeField()
    video_local_path = models.CharField(max_length=255)
    video_url = models.CharField(max_length=255)
    blog_url = models.CharField(max_length=255)
    tweet_url = models.CharField(max_length=255)
    fb_url = models.CharField(max_length=255)


class CrawlUrl(StatusMixin):
    url = models.CharField(max_length=255)
    force_encoding = models.CharField(max_length=255, blank=True, null=True)
    date_last_crawled = models.DateTimeField(blank=True, null=True)

    def __unicode__(self):
        maxlen = 50
        return ('<URL: %s>' % (self.url[:maxlen] + (len(self.url) > maxlen and '...' or '')))

