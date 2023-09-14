# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
import uuid
from django.db import models
import diana.abstract.models as abstract
import diana.abstract.mixins as mixins
from django.utils.translation import gettext_lazy as _

class Author(abstract.AbstractBaseModel, mixins.GenderedMixin):

    lbauthorid = models.CharField(blank=True, null=True, max_length=128)
    normalized_lbauthorid = models.CharField(blank=True, null=True, max_length=128)


    name = models.CharField(blank=True, null=True, max_length=128, verbose_name=_("name"))
    formatted_name = models.CharField(blank=True, null=True, max_length=128, verbose_name=_("formatted name"))
    surname = models.CharField(blank=True, null=True, max_length=128, verbose_name=_("surname"))

    birth_year = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=_("year of birth"))
    death_year = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=_("year of death"))

    def __str__(self) -> str:
        
        return self.name if self.name else "Unknown"

class Work(abstract.AbstractBaseModel):

    
    title = models.CharField( blank=True, null=True, max_length=1024, default="", verbose_name=_("title"))
    short_title = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("short title"))
    modernized_title = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("modernized title"))

    # lbworkid = models.CharField(unique=True, max_length=128, verbose_name=_("llbworkid"))
    lbworkid = models.CharField(max_length=128, verbose_name=_("llbworkid"))

    librisid = models.CharField(max_length=128, blank=True, null=True, verbose_name=_("librisid")) 

    main_author   = models.ForeignKey(Author, blank=True, null=True, verbose_name=_("author"), on_delete=models.CASCADE)
    authors  = models.ManyToManyField(Author, related_name='works', verbose_name=_("authors"))

    edition  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_("edition"))

    language = models.CharField(max_length=128, blank=True, null=True, verbose_name=_("language"))

    imprint_year = models.PositiveSmallIntegerField(default=None, blank=True, null=True, verbose_name=_("imprint year"))
    sort_year    = models.PositiveSmallIntegerField(default=None, blank=True, null=True, verbose_name=_("sort year"))
    
    word_count = models.PositiveIntegerField(verbose_name=_("word count"), blank=True, null=True, )

    @property
    def page_count(self):
        return self.pages.count()

    def __str__(self) -> str:
        return f"{self.title}"


class Page(abstract.AbstractDocumentModel):

    work = models.ForeignKey(Work, verbose_name=_("work"), on_delete=models.CASCADE, related_name='pages')
    number = models.PositiveIntegerField(verbose_name=_("page number"))

    class Meta:
        ordering = ['-number']
        constraints = [
            models.UniqueConstraint(fields=['work', 'number'], name='unique page-work identifier')
        ]

    def __str__(self) -> str:
        return f"{self.work.title}, page {self.number}"

class Cluster(abstract.AbstractBaseModel):

    id = models.PositiveBigIntegerField(unique=True, primary_key=True)
    size = models.PositiveIntegerField(verbose_name=_("cluster size"))

    def __str__(self) -> str:
        return f"{self.id}"

# class Segment(abstract.AbstractBaseModel):
    
#     uid = models.CharField(max_length=256, default="")
#     gid = models.CharField(max_length=256, default="")

#     bw = models.PositiveIntegerField(verbose_name=_("bw"))
#     ew = models.PositiveIntegerField(verbose_name=_("ew"))
#     begin = models.PositiveIntegerField(verbose_name=_("begin"))
#     end = models.PositiveIntegerField(verbose_name=_("end"))

#     cluster = models.ForeignKey(Cluster, verbose_name=_("cluster"), on_delete=models.CASCADE, related_name='segments')
#     page = models.ForeignKey(Page, verbose_name=_("page"), on_delete=models.CASCADE, related_name='segments')
#     text = models.TextField(default="", verbose_name=_("excerpt"))

#     series = models.ForeignKey(Work, on_delete=models.CASCADE, verbose_name=_("work id"))

#     def __str__(self) -> str:
#         return f"{self.page.work.title}, {self.bw}-{self.ew}"