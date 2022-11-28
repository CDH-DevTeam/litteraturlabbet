from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('litteraturlabbet', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql='''
              CREATE TRIGGER text_vector_trigger
              BEFORE INSERT OR UPDATE OF text, text_vector
              ON litteraturlabbet_page
              FOR EACH ROW EXECUTE PROCEDURE
              tsvector_update_trigger(
                text_vector, 'pg_catalog.simple', text
              );

              UPDATE litteraturlabbet_page SET text_vector = NULL;
            ''',

            reverse_sql = '''
              DROP TRIGGER IF EXISTS text_vector
              ON litteraturlabbet_page;
            '''
        ),
    ]