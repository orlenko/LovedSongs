import os
import sys
import codecs
from ConfigParser import ConfigParser
import id3reader
import cPickle
from pybing import Bing
from pprint import pformat
from BeautifulSoup import BeautifulSoup
import urllib
from mechanize_crawler import Browser


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
    print 'Raw value: %r' % (value,)
    already_unicode = isinstance(value, unicode)
    if already_unicode:
        print 'Already unicode'
    for encoding in ('cp1251', 'utf-16', 'win1251', 'koi8-r', 'utf-8'):
        try:
            print 'trying to decode as %s' % encoding
            decoded = value.decode(encoding)
            print 'ok: %r' % decoded
            return decoded
        except:
            print 'nope'
            pass
    if already_unicode:
        print 'Maybe I am wrong, but I will return original value'
        return value
    return 'failed to decode'


lyrics_matches = {
    # Site: (what to look for, what to skip)
    'lyricsmode.com': ({'id': 'songlyrics_h'},
                       'lyricsmode.com'),
    'lyricsfreak.com': ({'id': 'content', 'class': 'lyricstxt'},
                        'lyricsfreak.com'),
}


class VideoEntry:
    def __init__(self, mp3_fname):
        self.mp3_fname = mp3_fname
        self.init_config()

    def process(self):
        print 'Processing %s' % self.mp3_fname
        self.get_tags()
        self.get_text()
        self.get_pics()
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
            return
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
            print '...%s' % part
            if hasattr(part, 'contents'):
                for sub_part in self.extract_text_parts(part.contents, exclude):
                    yield sub_part
            else:
                if not exclude or not (exclude in part):
                    yield part.strip(' \n\r')

    def get_text(self):
        if self.conf_lyrics_done:
            print 'Lyrics are already done'
            return
        bing = Bing('A98B5504E6CAEC6C4ECDED9D83AA57C947206C8F')
        tags = self.conf_tags
        lyrics_search = bing.search_web('"%s" lyrics %s %s'
                                        % (tags['title'],
                                           tags['album'],
                                           tags['performer']))
        #print 'Lyrics search result: %s' % pformat(lyrics_search)
        for result in lyrics_search.get(
                            'SearchResponse', {}).get(
                                'Web', {}).get(
                                    'Results', []):
            url = result['Url']

            for match, (good_attr, bad_part) in lyrics_matches.items():
                if match in url:
                    # Good! We have a known site with lyrics - let's extract them.

                    browser = Browser()
                    browser.set_handle_robots(None)
                    browser.open(url)
                    text = browser.response().read()
                    soup = BeautifulSoup(text)
                    lyrics_el = soup.find(attrs=good_attr)
                    if not lyrics_el:
                        print 'Not found lyrics in %s' % text
                        continue
                    print 'full text: %s' % text
                    print 'Found something like this: %s' % lyrics_el
                    parts = list(self.extract_text_parts(lyrics_el.contents, bad_part))
                    lyrics = '\n'.join(parts)
                    print 'Found lyrics: \n%s' % lyrics
                    self.conf_lyrics = lyrics
                    self.conf_lyrics_done = True
                    return

    def get_pics(self):
        if self.conf_pics_done:
            print 'Pics are already done'
            return
        bing = Bing('A98B5504E6CAEC6C4ECDED9D83AA57C947206C8F')
        tags = self.conf_tags
        img_search = bing.search_image('"%s" %s %s'
                                        % (tags['title'],
                                           tags['album'],
                                           tags['performer']))
        #print 'Images: %s' % pformat(img_search)



def on_mp3(fname):
    entry = VideoEntry(fname)
    entry.process()


def crawl(dirname):
    os.path.walk(dirname, walker, None)


if __name__ == '__main__':
    root = len(sys.argv) > 1 and sys.argv[1] or 'data'
    crawl(root)
