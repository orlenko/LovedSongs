import os
import sys
import glob
import id3reader
import cPickle
from pprint import pformat
from BeautifulSoup import BeautifulSoup
from mechanize_crawler import Browser
import Image
from traceback import print_exc
import subprocess
import re
import slideshow
import logging
from bing_search_api import BingSearchAPI
import random


log = logging.getLogger(__file__)


DEFAULT_VIDEO_RESOLUTION = [640, 360]
REQUIRED_IMAGE_COUNT = 10


def get_genre(genre):
    try:
        return id3reader._genres[int(genre.strip('() '))]
    except:
        return genre


def walker(context, dirname, files):
    print 'Walking through %s: %s' % (dirname, files)
    for f in files:
        fname = os.path.join(dirname, f)
        if os.path.isfile(fname) and fname.lower().endswith('.mp3'):
            on_mp3(fname)


def smart_decode(value):
    #print 'Raw value: %r' % (value,)
    already_unicode = isinstance(value, unicode)
    #if already_unicode:
    #    print 'Already unicode'
    for encoding in ('cp1251', 'utf-16', 'win1251', 'koi8-r', 'utf-8'):
        try:
            #print 'trying to decode as %s' % encoding
            decoded = value.decode(encoding)
            #print 'ok: %r' % decoded
            return decoded
        except:
            #print 'nope'
            pass
    if already_unicode:
        #print 'Maybe I am wrong, but I will return original value'
        return value
    return 'failed to decode'


lyrics_matches = {
    # Site: (what to look for, what to skip)
    'lyricsmode.com': ({'id': 'songlyrics_h'}, 'lyricsmode.com'),
    'lyricsfreak.com': ({'id': 'content', 'class': 'lyricstxt'}, 'lyricsfreak.com'),
    'songlyrics.com': ({'id': 'songLyricsDiv'}, 'songlyrics.com'),
    'elyrics.net': ({'class': 'ly'}, 'elyrics.net'),
}


processed_image_urls = {} # dirname -> set(urls)


class VideoEntry:
    def __init__(self, mp3_fname):
        self.mp3_fname = mp3_fname
        self.init_config()

    def process(self):
        print 'Processing %s' % self.mp3_fname
        if (self.get_tags()
                and self.get_text()
                and self.get_pics()
                and self.make_video()):
            self.save()

    @property
    def config_fname(self):
        return self.mp3_fname + '.config'

    def init_config(self):
        config_file = self.config_fname
        if os.path.exists(config_file):
            with open(config_file, 'r') as c:
                self.config = cPickle.load(c)
        else:
            self.config = {}

    def __getattr__(self, name):
        if name.startswith('conf_'):
            return self.config.get(name[len('conf_'):], None)
        else:
            return self.__dict__[name]

    def __setattr__(self, name, value):
        if name.startswith('conf_'):
            self.config[name[len('conf_'):]] = value
        else:
            self.__dict__[name] = value

    def save(self):
        with open(self.config_fname, 'w') as f:
            cPickle.dump(self.config, f)

    def get_tags(self):
        if self.conf_tags_done:
            print 'Tags are already done'
            return self.conf_tags_done
        default_tags = {
            'album': '',
            'performer': '',
            'title': '',
            'genre': '',
            'year': '',
            'track': '',
            'comment': ''
        }
        tags = self.conf_tags or default_tags
        tags = self.tags_from_mp3(tags)
        tags = self.tags_from_dir(tags)
        tags = self.convert_tags(tags)
        self.conf_tags = tags
        self.conf_tags_done = True
        return self.conf_tags_done

    def convert_tags(self, tags):
        ru_marker = u'\xc1\xf3\xeb\xee\xed\xe5\xeb\xfe\xe1\xe8\xf2\xe8'
        for k, v in tags.items():
            for mark in ru_marker:
                if mark in v:
                    try:
                        tags[k] = v.encode('windows-1252').decode('windows-1251')
                        log.debug('Converted %r -> %s' % (v, tags[k]))
                        break
                    except:
                        pass
        return tags

    def get_utf_tag(self, reader, tag):
        retval = reader.getValue(tag) or ''
        return smart_decode(retval)

    def tags_from_mp3(self, tags):
        reader = id3reader.Reader(self.mp3_fname)
        for tag in tags:
            if not tags[tag]:
                value = self.get_utf_tag(reader, tag)
                if value:
                    tags[tag] = value
                    if tag == 'genre':
                        tags[tag] = get_genre(value)
        return tags

    def tags_from_dir(self, tags):
        if not tags['album']:
            tags['album'] = smart_decode(os.path.basename(os.path.dirname(self.mp3_fname)))
        if not tags['performer']:
            tags['performer'] = smart_decode(os.path.basename(os.path.dirname(os.path.dirname(self.mp3_fname))))
        return tags

    def extract_text_parts(self, collection, exclude):
        for part in collection:
            #print '...%s' % part
            if hasattr(part, 'contents'):
                for sub_part in self.extract_text_parts(part.contents, exclude):
                    yield sub_part
            else:
                if not exclude or not (exclude in part):
                    yield part.strip(' \n\r').encode('utf8')

    def get_text(self):
        if self.conf_lyrics_done:
            print 'Lyrics are already done'
            return self.conf_lyrics_done
        bing = BingSearchAPI()
        tags = self.conf_tags
        search = '%s lyrics %s' % (tags['title'], tags['performer'])
        print 'Searching for lyrics. Search string: %s' % search
        lyrics_search = bing.search('web', search.encode('utf-8'), {'$format': 'json'})
        #print 'Lyrics search result: %s' % pformat(lyrics_search)
        for result in lyrics_search.get('d', {}).get('results', [{}])[0].get('Web', []):
            url = result['Url']
            print 'lyrics in %s?' % url
            for match, (good_attr, bad_part) in lyrics_matches.items():
                if match in url:
                    # Good! We have a known site with lyrics - let's extract them.
                    print 'yes, lyrics are probably here'
                    browser = Browser()
                    browser.set_handle_robots(None)
                    browser.open(url)
                    text = browser.response().read()
                    soup = BeautifulSoup(text, convertEntities=BeautifulSoup.HTML_ENTITIES)
                    lyrics_el = soup.find(attrs=good_attr)
                    if not lyrics_el:
                        #print 'Not found lyrics in %s' % text
                        continue
                    #print 'full text: %s' % text
                    #print 'Found something like this: %s' % lyrics_el
                    parts = list(self.extract_text_parts(lyrics_el.contents, bad_part))
                    lyrics = '\n'.join(parts)
                    #print 'Found lyrics: \n%s' % lyrics
                    print 'Found lyrics: %s...' % lyrics[:150]
                    self.conf_lyrics = lyrics
                    self.conf_lyrics_done = True
                    return self.conf_lyrics_done
            print 'Unsupported lyrics source: %s' % url
        if not self.conf_lyrics_done:
            print 'ERROR: lyrics not found! %s' % self.conf_tags['title']
        return self.conf_lyrics_done

    @property
    def imgdir(self):
        return os.path.join(os.path.dirname(self.mp3_fname),
                            'images')

    def get_pics(self):
        if self.conf_pics_done:
            print 'Pics are already done'
            return self.conf_pics_done
        imgdir = self.imgdir
        if len(glob.glob1(imgdir, "*.png")) > REQUIRED_IMAGE_COUNT:
            self.conf_pics_done = True
            return self.conf_pics_done
        bing = BingSearchAPI()
        tags = self.conf_tags
        search = '%s %s' % (tags['title'], tags['performer'])
        print 'Searching for images. Search string: %s' % search
        img_search = bing.search('image', search.encode('utf-8'), {'$format': 'json'})
        print 'Images: %s' % pformat(img_search)
        registry = processed_image_urls.setdefault(imgdir, set())
        if not os.path.exists(imgdir):
            os.makedirs(imgdir)
        for result in img_search.get('d', {}).get('results', [{}])[0].get('Image', []):
            if result['MediaUrl'] not in registry:
                browser = Browser()
                browser.set_handle_robots(None)
                registry.add(result['MediaUrl'])
                log.debug('%s images in %s' % (len(glob.glob1(imgdir, "*.png")), imgdir))
                try:
                    #log.debug('Opening %s' % result['SourceUrl'])
                    browser.open(result['SourceUrl'])
                    #log.debug('Opening %s' % result['MediaUrl'])
                    img = Image.open(browser.open(result['MediaUrl']))
                    if img.size[0] >= DEFAULT_VIDEO_RESOLUTION and img.size[1] >= DEFAULT_VIDEO_RESOLUTION[1]:
                        print 'Found image: %s' % result['MediaUrl']
                        img.save(os.path.join(imgdir, ('image%03d.png'
                            % (len(glob.glob1(imgdir, "*.png"))) + 1)))
                        self.conf_pics_done = True
                        if len(glob.glob1(imgdir, "*.png")) > REQUIRED_IMAGE_COUNT:
                            self.conf_pics_done = True
                            break
                except:
                    print_exc()
        if len(glob.glob1(imgdir, "*.png")) < REQUIRED_IMAGE_COUNT:
            search = tags['performer']
            print 'Searching for images. Search string: %s' % search
            img_search = bing.search('image', search.encode('utf-8'), {'$format': 'json'})
            for result in img_search.get('d', {}).get('results', [{}])[0].get('Image', []):
                if result['MediaUrl'] not in registry:
                    browser = Browser()
                    browser.set_handle_robots(None)
                    registry.add(result['MediaUrl'])
                    log.debug('%s images in %s' % (len(glob.glob1(imgdir, "*.png")), imgdir))
                    try:
                        #log.debug('Opening %s' % result['SourceUrl'])
                        browser.open(result['SourceUrl'])
                        #log.debug('Opening %s' % result['MediaUrl'])
                        img = Image.open(browser.open(result['MediaUrl']))
                        if img.size[0] >= DEFAULT_VIDEO_RESOLUTION[0] and img.size[1] >= DEFAULT_VIDEO_RESOLUTION[1]:
                            print 'Found image: %s' % result['MediaUrl']
                            img.save(os.path.join(imgdir, ('image%03d.png'
                                % (len(glob.glob1(imgdir, "*.png"))) + 1)))
                            if len(glob.glob1(imgdir, "*.png")) > REQUIRED_IMAGE_COUNT:
                                self.conf_pics_done = True
                                break
                    except:
                        print_exc()
        return self.conf_pics_done

    def make_video(self):
        if self.conf_video_done:
            return self.conf_video_done
        assert self.conf_pics_done
        assert self.conf_lyrics_done
        self.detect_duration()
        self.generate_images()
        self.generate_video_fragments()
        self.combine_video_fragments()
        self.conf_video_done = True
        return self.conf_video_done

    def detect_duration(self):
        ffmpeg = subprocess.Popen(['avconv', '-i', self.mp3_fname],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)
        print ffmpeg.communicate()
#        sed = subprocess.Popen(['sed', '-n', '"s/.*Duration: \([^,]*\).*/\1/p"'],
#                               stdin=ffmpeg.stderr,
#                               stdout=subprocess.PIPE,
#                               stderr=subprocess.PIPE)
#        output = sed.communicate()[0]
#        print 'Output: %s' % output
#        regex = r'([\d][\d]):([\d][\d]):([\d][\d]\.[\d]+)'
#        match = re.match(regex, output)
#        if match:
#            self.mp3_seconds = (int(match.group(1)) * 60 * 60
#                       + int(match.group(2)) * 60
#                       + float(match.group(3)))
#        else:
#            raise RuntimeError('Failed to detect MP3 length')

    def generate_images(self):
        imgdir = self.imgdir
        for image_file in os.listdir(imgdir):
            image_file = os.path.join(imgdir, image_file)
            img_dir = image_file + '_frames'
            if not os.path.exists(img_dir):
                os.makedirs(img_dir)
            slideshow.pan_zoom(Image(image_file),
                               DEFAULT_VIDEO_RESOLUTION,
                               img_dir,
                               random.choice(((1,1), (1,-1), (-1,1), (-1,-1))),
                               ramdom.choice((True, False)))

    def generate_video_fragments(self):
        pass

    def combine_video_fragments(self):
        pass


def on_mp3(fname):
    try:
        entry = VideoEntry(fname)
        entry.process()
    except:
        print_exc()


def crawl(dirname):
    os.path.walk(dirname, walker, None)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    root = len(sys.argv) > 1 and sys.argv[1] or 'data'
    crawl(root)
