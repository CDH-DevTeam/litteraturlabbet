import json
import glob
from .. import models
import requests
from . import litteraturbanken
from tqdm import tqdm

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
        modernized_title =  work_metadata.get('title_modernized')
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

        author,_ = models.Author.objects.get_or_create(

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

    # library = litteraturbanken.Library.from_directory(root)
    library = glob.glob(root+"/*.json")

    works = []
    progress = tqdm(library)
    for book in progress:
        print(book)
        book = open(book).readlines()
        for line in book:
            row = json.loads(line)
            try:
                metadata = get_work_metadata(row["series"])[0]
                author_metadata = metadata.get('main_author')
                authors_metadata =  metadata.get('authors')

            except:
                author_metadata = {}
                
            progress.set_description(row["series"])

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
                title =  work_metadata.get('title')
            except:
                title = None
            try :
                short_title =  work_metadata.get('shorttitle')
            except:
                short_title = None
            try :
                modernized_title =  work_metadata.get('title_modernized')
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


            lbworkid=row["series"]
            if (lbworkid):
                work,_ = models.Work.objects.get_or_create(
                                                            lbworkid=row["series"], 
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
                work.authors.set(authors)
                work.save()
        
        # models.Work.objects.bulk_create(works, ignore_conflicts=False, update_conflicts=True, update_fields=True, unique_fields=False)

def load_pages(root):

    # library = litteraturbanken.Library.from_directory(root)
    library = glob.glob(root+"/*.json")
    progress = tqdm(library)
    for book in progress:
        book = open(book).readlines()
        progress = tqdm(book)
    
        for line in book:
            row = json.loads(line) 
            workid = row["series"]
            if workid in pages_text:
                text = pages_text[workid].get(row['page'], "")
            # if workid == pages_text['series'] and row['page'] == pages_text['number']:
            #     text = pages_text['text']
            else:
                text = ''
            progress.set_description(f"{workid}, {row['page']}")
            page,_ = models.Page.objects.get_or_create(           
                                number = row['page'],
                                work = models.Work.objects.get(lbworkid=workid),
                                defaults= {
                                    'text': text,
                                }
                            )
            page.save()

    

def load_pages_text(main_text_input):
    pages = open(main_text_input, encoding='latin-1')
    for page in pages:
        try :
            page = json.loads(page, strict=False)
            book_id = page['series']
            if book_id not in pages_text:
                pages_text[book_id] = {}
            pages_text[book_id][page['page']] = page['text']
        except:
            print(page)
    i = 5


def load_cluster(root):
    library = glob.glob(root+"/*.json")
    progress = tqdm(library)
    for book in progress:
        print(book)
        book = open(book).readlines()
        for line in book:
            row = json.loads(line) 
            workid = row["series"]
            progress.set_description(f"{workid}, {row['cluster']}")
            

def load_segment(root):
    library = glob.glob(root+"/*.json")
    progress = tqdm(library)
    for book in progress:
        print(book)
        book = open(book).readlines()
        for line in book:
            row = json.loads(line) 
            workid = row["series"]
            progress.set_description(f"{workid}, {row['cluster']}")
            segment,_ = models.Segment.objects.get_or_create(   
                                uuid = row['uuid'],
                                gid = row['gid'],      
                                bw = row['bw'],
                                ew = row['ew'],
                                begin = row['begin'],
                                end = row['end'],
                                # ????
                                cluster = models.Cluster.objects.get(lbworkid=workid),
                                # ????
                                page = models.Page.objects.get(lbworkid=workid),
                                text = row['text'],
                                series = workid
                            )
            segment.save()
