import os
import sys
import id3reader
import cPickle
from pybing import Bing
#from pprint import pformat
from BeautifulSoup import BeautifulSoup
from mechanize_crawler import Browser
import Image
from traceback import print_exc
import subprocess
import re
from .slideshow import pan_zoom


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
        self.conf_tags = tags
        self.conf_tags_done = True
        return self.conf_tags_done

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
        bing = Bing('A98B5504E6CAEC6C4ECDED9D83AA57C947206C8F')
        tags = self.conf_tags
        search = '%s lyrics %s' % (tags['title'], tags['performer'])
        print 'Searching for lyrics. Search string: %s' % search
        lyrics_search = bing.search_web(search)
        #print 'Lyrics search result: %s' % pformat(lyrics_search)
        for result in lyrics_search.get(
                            'SearchResponse', {}).get(
                                'Web', {}).get('Results', []):
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
        bing = Bing('A98B5504E6CAEC6C4ECDED9D83AA57C947206C8F')
        tags = self.conf_tags
        search = '%s %s' % (tags['title'], tags['performer'])
        print 'Searching for images. Search string: %s' % search
        img_search = bing.search_image(search)
        #print 'Images: %s' % pformat(img_search)
        imgdir = self.imgdir
        if not os.path.exists(imgdir):
            os.makedirs(imgdir)
        for result in img_search.get(
                            'SearchResponse', {}).get(
                                'Image', {}).get('Results', []):
            browser = Browser()
            browser.set_handle_robots(None)
            registry = processed_image_urls.setdefault(imgdir, set())
            if result['MediaUrl'] not in registry:
                registry.add(result['MediaUrl'])
                count = len(registry)
                try:
                    browser.open(result['Url'])
                    img = Image.open(browser.open(result['MediaUrl']))
                    if img.size[0] >= 640 and img.size[1] >= 480:
                        print 'Found image: %s' % result['MediaUrl']
                        img.save(os.path.join(imgdir, ('image%03d.png' % count)))
                        self.conf_pics_done = True
                except:
                    print_exc()
        if count < 10:
            search = tags['performer']
            print 'Searching for images. Search string: %s' % search
            img_search = bing.search_image(search)
            for result in img_search.get(
                                'SearchResponse', {}).get(
                                    'Image', {}).get('Results', []):
                browser = Browser()
                browser.set_handle_robots(None)
                try:
                    browser.open(result['Url'])
                    img = Image.open(browser.open(result['MediaUrl']))
                    if img.size[0] >= 640 and img.size[1] >= 480:
                        print 'Found image: %s' % result['MediaUrl']
                        img.save(os.path.join(imgdir, ('image%03d.png' % count)))
                        count += 1
                        if count > 10:
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
        cmd = r'ffmpeg -i "%s" 2>&1|sed -n "s/.*Duration: \([^,]*\).*/\1/p"' % self.mp3_fname
        output = subprocess.Popen([cmd], stdout=subprocess.PIPE).communicate()[0]
        regex = r'([\d][\d]):([\d][\d]):([\d][\d]\.[\d]+)'
        match = re.match(regex, output)
        if match:
            self.mp3_seconds = (int(match.group(1)) * 60 * 60
                       + int(match.group(2)) * 60
                       + float(match.group(3)))
        else:
            raise RuntimeError('Failed to detect MP3 length')

    def generate_images(self):
        imgdir = self.imgdir
        for image_file in os.listdir(imgdir):
            image_file = os.path.join(imgdir, image_file)
            img_dir = image_file + '_frames'
            if not os.path.exists(img_dir):
                os.makedirs(img_dir)
            pan_zoom()

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
    root = len(sys.argv) > 1 and sys.argv[1] or 'data'
    crawl(root)
