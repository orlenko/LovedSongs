# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Song'
        db.create_table('lovedmanager_song', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('data_downloaded', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('local_filename', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('lovedmanager', ['Song'])

        # Adding model 'Image'
        db.create_table('lovedmanager_image', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('data_downloaded', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('local_filename', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lovedmanager.Song'])),
            ('inspired_by', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('lovedmanager', ['Image'])

        # Adding model 'Lyrics'
        db.create_table('lovedmanager_lyrics', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('data_downloaded', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('local_filename', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lovedmanager.Song'])),
        ))
        db.send_create_signal('lovedmanager', ['Lyrics'])

        # Adding model 'TextBit'
        db.create_table('lovedmanager_textbit', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('source_url', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('data_downloaded', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('local_filename', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lovedmanager.Song'])),
            ('inspired_by', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('lovedmanager', ['TextBit'])

        # Adding model 'Post'
        db.create_table('lovedmanager_post', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('error_text', self.gf('django.db.models.fields.TextField')()),
            ('song', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lovedmanager.Song'])),
            ('approved_lyrics', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['lovedmanager.Lyrics'])),
            ('date_approved', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_started_processing', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_created_video', self.gf('django.db.models.fields.DateTimeField')()),
            ('date_posted', self.gf('django.db.models.fields.DateTimeField')()),
            ('video_local_path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('video_url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('blog_url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('tweet_url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('fb_url', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('lovedmanager', ['Post'])

        # Adding M2M table for field approved_images on 'Post'
        db.create_table('lovedmanager_post_approved_images', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('post', models.ForeignKey(orm['lovedmanager.post'], null=False)),
            ('image', models.ForeignKey(orm['lovedmanager.image'], null=False))
        ))
        db.create_unique('lovedmanager_post_approved_images', ['post_id', 'image_id'])

        # Adding M2M table for field approved_textbits on 'Post'
        db.create_table('lovedmanager_post_approved_textbits', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('post', models.ForeignKey(orm['lovedmanager.post'], null=False)),
            ('textbit', models.ForeignKey(orm['lovedmanager.textbit'], null=False))
        ))
        db.create_unique('lovedmanager_post_approved_textbits', ['post_id', 'textbit_id'])

        # Adding model 'CrawlUrl'
        db.create_table('lovedmanager_crawlurl', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('error_text', self.gf('django.db.models.fields.TextField')()),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date_last_crawled', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal('lovedmanager', ['CrawlUrl'])


    def backwards(self, orm):
        
        # Deleting model 'Song'
        db.delete_table('lovedmanager_song')

        # Deleting model 'Image'
        db.delete_table('lovedmanager_image')

        # Deleting model 'Lyrics'
        db.delete_table('lovedmanager_lyrics')

        # Deleting model 'TextBit'
        db.delete_table('lovedmanager_textbit')

        # Deleting model 'Post'
        db.delete_table('lovedmanager_post')

        # Removing M2M table for field approved_images on 'Post'
        db.delete_table('lovedmanager_post_approved_images')

        # Removing M2M table for field approved_textbits on 'Post'
        db.delete_table('lovedmanager_post_approved_textbits')

        # Deleting model 'CrawlUrl'
        db.delete_table('lovedmanager_crawlurl')


    models = {
        'lovedmanager.crawlurl': {
            'Meta': {'object_name': 'CrawlUrl'},
            'date_last_crawled': ('django.db.models.fields.DateTimeField', [], {}),
            'error_text': ('django.db.models.fields.TextField', [], {}),
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
