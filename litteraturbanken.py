import os
from glob import glob
from bs4 import BeautifulSoup
from typing import *
import numpy as np
from multiprocessing import Pool
# from tqdm import tqdm

class Page:

    def __init__(self, path) -> None:
        self.id = os.path.basename(path)
        self.path = path

    def as_text(self):
        with open(self.path, 'r') as f:
            soup = BeautifulSoup(f, 'html.parser')
            text = soup.get_text()

        return text


class Book:

    def __init__(self, id, root) -> None:
        self.id = id
        self.root = root
        self.directory = os.path.join(root, id)

        # Initialize the book
        self.pages = Book.get_pages(self.id, self.root)

    @staticmethod
    def get_pages(id, root):
        # Pages are zero-indexed
        
        page_files = glob(os.path.join(root, id, '*.html'))
        
        # Sort by name, granted that they are 
        # named identically except for the page identifier
        page_files = sorted(page_files)

        return [Page(file) for file in page_files]

    def as_text(self):
    
        book = ""

        for page in self.pages:
            book += (page.as_text() + "\n")

        return book

    def save(self, destination):

        text = self.as_text()

        with open(destination, "w+") as f:
            f.write(text)

class Library:

    def __init__(self, root, books = []) -> None:
        self.root = root
        self.books = books
        self._book_dict = {book.id: book for book in self.books}

    @classmethod
    def from_books(cls, books: List[Book]):
        
        return cls(None, books)

    @classmethod
    def from_directory(cls, root: str):
        
        ids = os.listdir(root)
        books = []
        
        args = [(id, root) for id in ids]
        with Pool() as p:
            books = p.starmap(Book, args)
        
        return cls(root, books)

    @staticmethod
    def save_book(book: Book, destination):
        book.save(os.path.join(destination, book.id)+".txt")

    def save(self, destination):

        if not os.path.exists(destination):
            os.mkdir(destination)

        with Pool() as p:
            args = [(book, destination) for book in self.books]
            p.starmap(Library.save_book, args)

    def sample(self, n_samples=10):

        return list(np.random.choice(self.books, n_samples, replace=False))

    def __getitem__(self, key):
        return self._book_dict[key]

    def __len__(self):
        return len(self.books)

    def __iter__(self):
        for book in self.books:
            yield book