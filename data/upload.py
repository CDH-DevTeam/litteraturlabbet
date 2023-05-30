import json
import glob
from .. import models
import requests
from . import litteraturbanken
from tqdm import tqdm

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
                metadata = {}
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

            work,_ = models.Work.objects.get_or_create(
                lbworkid=row["series"],
                defaults={
                    'title': work_metadata.get('title'),
                    'short_title': work_metadata.get('shorttitle'),
                    'modernized_title': work_metadata.get('title_modernized'),
                    'librisid': work_metadata.get('librisid'),
                    'main_author': author,
                    'edition': work_metadata.get('edition'),
                    'language': work_metadata.get('language'),
                    'word_count': work_metadata.get('word_count')
                }
            )
            work.authors.set(authors)
            work.save()
            # works.append(work)
        
        # models.Work.objects.bulk_create(works, ignore_conflicts=False, update_conflicts=True, update_fields=True, unique_fields=False)

def load_pages(root):

    library = litteraturbanken.Library.from_directory(root)

    progress = tqdm(library)
    for book in progress:
        
        work = models.Work.objects.get(lbworkid=book.id)

        pages = []

        for page in book.pages:
            page_number = page.id.split('_')[1].replace('.html','')
            progress.set_description(f"{book.id}, {page_number}")
            pages.append(models.Page(
                work=work, 
                number=int(page_number),
                text=page.as_text()
            ))

        models.Page.objects.bulk_create(pages)

    
