from .. import models
import requests
from . import litteraturbanken
from tqdm import tqdm


def get_work_metadata(lbworkid):

    headers = {
        "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36'
    }

    url = lambda x: f"https://litteraturbanken.se/api/get_work_info?lbworkid={(x)}"
    

    response = requests.get(url(lbworkid), headers=headers).json()

    return response['data']


def load_works(root):

    library = litteraturbanken.Library.from_directory(root)

    gender_map = {
        'male': 'M',
        'female': 'F',
        'not known': 'X'
    }

    works = []
    progress = tqdm(library)
    for book in progress:
        
        try:
            metadata = get_work_metadata(book.id)[0]
            author_metadata = metadata.get('main_author')

        except:
            metadata = {}
            author_metadata = {}
        
        progress.set_description(book.id)

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

        author, _   = models.Author.objects.update_or_create(
            lbauthorid=author_metadata.get('authorid'),
            normalized_lbauthorid=author_metadata.get('authorid_norm'),
            name=author_metadata.get('full_name'),
            gender=gender,
            formatted_name=author_metadata.get('name_for_index'),
            birth_year=birth_year,
            death_year=death_year,
        )
        
        work_metadata = metadata


        work = models.Work(
            title=work_metadata.get('title'),
            short_title=work_metadata.get('shorttitle'),
            modernized_title=work_metadata.get('title_modernized'),
            lbworkid=book.id,
            librisid=work_metadata.get('librisid'),
            author=author,
            edition=work_metadata.get('edition'),
            language=work_metadata.get('language'),
            word_count=work_metadata.get('word_count'),

        )

        works.append(work)
    
    models.Work.objects.bulk_create(works)

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

    
