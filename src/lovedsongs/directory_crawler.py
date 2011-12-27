import os
import sys
import codecs
from ConfigParser import ConfigParser
import id3reader
import cPickle
from pybing import Bing



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


class VideoEntry:
    def __init__(self, mp3_fname):
        self.mp3_fname = mp3_fname
        self.init_config()

    def process(self):
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
            cPickle.dump(f)

    def get_tags(self):
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
        if self.conf_tags_done:
            return
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

    def get_text(self):
        bing = Bing('A98B5504E6CAEC6C4ECDED9D83AA57C947206C8F')
        bing.


    def get_pics(self):
        pass



def on_mp3(fname):
    entry = VideoEntry(fname)
    entry.process()


def crawl(dirname):
    os.path.walk(dirname, walker, None)


if __name__ == '__main__':
    crawl('data')
