import json
import glob
import os
from .. import models
import requests
from . import litteraturbanken
from tqdm import tqdm
from django.db.models import Count, Q

pages_text = {}

gender_map = {
    'male': 'M',
    'female': 'F',
    'not known': 'X'
}

def get_work_metadata(lbworkid):

    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
    }

    url = lambda x: f"https://litteraturbanken.se/api/get_work_info?lbworkid={(x)}"
    

    response = requests.get(url(lbworkid), headers=headers).json()

    return response['data']


def fetch_work_info(work_metadata, author):
    metadata = {}
    
    try :
        title =  work_metadata.get('title')
    except:
        title = None
    try :
        short_title =  work_metadata.get('shorttitle')
    except:
        short_title = None
    try :
        modernized_title =  work_metadata.get('titleid')
    except:
        modernized_title = None
    try :
        librisid =  work_metadata.get('librisid')
    except:
        librisid = None
    try :
        edition =  work_metadata.get('edition')
    except:
        edition = None   
    try :
        language =  work_metadata.get('language')
    except:
        language = None
    try :
        word_count =  work_metadata.get('word_count')
    except:
        word_count = None
    try :
        sort_year = work_metadata.get('sort_date').get('date')
    except:
        sort_year = None
    try :
        imprint_year =  work_metadata.get('sort_date_imprint').get('date')
    except:
        imprint_year = None

    metadata={
        'title': title,
        'short_title': short_title,
        'modernized_title': modernized_title,
        'librisid': librisid,
        'main_author': author,
        'edition': edition,
        'language': language,
        'word_count': word_count,
        'sort_year' : sort_year,
        'imprint_year' : imprint_year,

    }
    return metadata


def authors_meta(data):
    result = []
    for author in data:
        try:
            gender = gender_map[author.get('gender')]
        except:
            gender = 'X'
        try: 
            birth_year =  int(author.get('birth').get('date'))
        except:
            birth_year = None
        try:
            death_year = int(author.get('death').get('date'))
        except:
                death_year = None  

        author,_ = models.Author.objects.update_or_create(

            lbauthorid=author.get('authorid'),
            normalized_lbauthorid=author.get('authorid_norm'),
            name=author.get('full_name'),
            gender=gender,
            formatted_name=author.get('name_for_index'),
            birth_year=birth_year,
            death_year=death_year,
            )
        result.append(author)
    return result 


def load_works(root):
    work_list = []
    # page_files = glob(os.path.join(root, '*.json'))
    # for page in library:

    for library in glob.glob(os.path.join(root, '*.json')):
        with open(os.path.join(os.getcwd(), library), 'r') as file:
            work = json.load(file, strict=False)

            if work['lbworkid'] not in work_list:
                progress = tqdm(library)
                try:
                    metadata = get_work_metadata(work["lbworkid"])[0]
                    author_metadata = metadata.get('main_author')
                    authors_metadata =  metadata.get('authors')

                except:
                    author_metadata = {}
                    
                progress.set_description(work["lbworkid"])

                try:
                    gender = gender_map[author_metadata.get('gender')]
                except:
                    gender = 'X'

                try: 
                    birth_year =  int(author_metadata.get('birth').get('date'))
                except:
                    birth_year = None

                try:
                    death_year = int(author_metadata.get('death').get('date'))
                except:
                    death_year = None

                author, _   = models.Author.objects.get_or_create(
                    lbauthorid=author_metadata.get('authorid'),
                    normalized_lbauthorid=author_metadata.get('authorid_norm'),
                    name=author_metadata.get('full_name'),
                    gender=gender,
                    formatted_name=author_metadata.get('name_for_index'),
                    birth_year=birth_year,
                    death_year=death_year,
                    )
                
                authors = authors_meta(authors_metadata)
                work_metadata = metadata
                try :
                    title =  work['title']
                except:
                    title = None
                try :
                    short_title =  work['shorttitle']
                except:
                    short_title = None
                try :
                    modernized_title =  work['title_modernized']
                except:
                    modernized_title = None
                try :
                    librisid =  work['librisid']
                except:
                    librisid = None
                try :
                    edition =  work['edition']
                except:
                    edition = None   
                try :
                    language =  work['language']
                except:
                    language = None
                try :
                    word_count =  work['word_count']
                except:
                    word_count = None
                try :
                    sort_year = work['sort_date'].get('date')
                except:
                    sort_year = None
                try :
                    imprint_year =  work['sort_date_imprint'].get('date')
                except:
                    imprint_year = None
                try:
                    modernized_title = work['titleid']
                except:
                    modernized_title = None


                lbworkid=work["lbworkid"]
                if (lbworkid):
                    book,_ = models.Work.objects.update_or_create(
                                                                lbworkid=work["lbworkid"], 
                                                                defaults= {
                                                                    'title': title,
                                                                        'short_title': short_title,
                                                                        'modernized_title': modernized_title,
                                                                        'librisid': librisid,
                                                                        'main_author': author,
                                                                        'edition': edition,
                                                                        'language': language,
                                                                        'word_count': word_count,
                                                                        'sort_year' : sort_year,
                                                                        'imprint_year' : imprint_year,
                                                                        }
                                                                )
                    book.authors.set(authors)
                    book.save()
                    work_list.append(lbworkid)

            

def load_pages(root):
    # pages = open(root, encoding='latin-1')
    for library in glob.glob(os.path.join(root, '*.json')):
        with open(os.path.join(os.getcwd(), library), 'r') as file:
            work = json.load(file, strict=False)
            workid = work['lbworkid']
            pages = work['pages']
            for page in pages:
                if page['text']:
                    text = page['text']
                else:
                    text = ''
                page,_ = models.Page.objects.update_or_create(           
                                            number = page['page_n'],
                                            work = models.Work.objects.get(lbworkid=workid),
                                            defaults= {
                                                'text': text,
                                            }
                                        )
                page.save()

    

def load_cluster(root):
    library = glob.glob(root+"/*.json")
    progress = tqdm(library)
    for book in progress:
        book = open(book).readlines()
        for line in book:
            row = json.loads(line) 
            workid = row["series"]
            progress.set_description(f"{workid}, {row['cluster']}")
            cluster,_ = models.Cluster.objects.get_or_create(           
                    id = (row['cluster']),
                    size = row['size'],
                )
            cluster.save()
            

def load_segment(root):
    library = glob.glob(root+"/*.json")
    progress = tqdm(library)
    for book in progress:
        book = open(book).readlines()
        for line in book:
            row = json.loads(line) 
            workid = row["series"]
            work = models.Work.objects.get(lbworkid=workid)
            page = models.Page.objects.get(work=work, number=row['page'])
            cluster = row['cluster']
            progress.set_description(f"{workid}, {cluster}")
            segment,_ = models.Segment.objects.get_or_create(   
                                uid = row['uid'],
                                gid = row['gid'],      
                                bw = row['bw'],
                                ew = row['ew'],
                                begin = row['begin'],
                                end = row['end'],
                                cluster = models.Cluster.objects.get(id=cluster),
                                page = page,
                                text = row['text'],
                                series = models.Work.objects.get(lbworkid=workid)
                            )
            segment.save()
