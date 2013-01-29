# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Changing field 'CrawlUrl.date_last_crawled'
        db.alter_column('lovedmanager_crawlurl', 'date_last_crawled', self.gf('django.db.models.fields.DateTimeField')(null=True))


    def backwards(self, orm):
        
        # Changing field 'CrawlUrl.date_last_crawled'
        db.alter_column('lovedmanager_crawlurl', 'date_last_crawled', self.gf('django.db.models.fields.DateTimeField')(default=datetime.date(2011, 12, 4)))


    models = {
        'lovedmanager.crawlurl': {
            'Meta': {'object_name': 'CrawlUrl'},
            'date_last_crawled': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'error_text': ('django.db.models.fields.TextField', [], {}),
            'force_encoding': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'lovedmanager.image': {
            'Meta': {'object_name': 'Image'},
            'data_downloaded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inspired_by': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'local_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lovedmanager.Song']"}),
            'source_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'lovedmanager.lyrics': {
            'Meta': {'object_name': 'Lyrics'},
            'data_downloaded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lovedmanager.Song']"}),
            'source_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        'lovedmanager.post': {
            'Meta': {'object_name': 'Post'},
            'approved_images': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['lovedmanager.Image']", 'symmetrical': 'False'}),
            'approved_lyrics': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lovedmanager.Lyrics']"}),
            'approved_textbits': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['lovedmanager.TextBit']", 'symmetrical': 'False'}),
            'blog_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'date_approved': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_created_video': ('django.db.models.fields.DateTimeField', [], {}),
            'date_posted': ('django.db.models.fields.DateTimeField', [], {}),
            'date_started_processing': ('django.db.models.fields.DateTimeField', [], {}),
            'error_text': ('django.db.models.fields.TextField', [], {}),
            'fb_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lovedmanager.Song']"}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'tweet_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'video_local_path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'video_url': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'lovedmanager.song': {
            'Meta': {'object_name': 'Song'},
            'data_downloaded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'local_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'source_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'lovedmanager.textbit': {
            'Meta': {'object_name': 'TextBit'},
            'data_downloaded': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inspired_by': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'local_filename': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'song': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['lovedmanager.Song']"}),
            'source_url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['lovedmanager']
