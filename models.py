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


    name = models.CharField(blank=True, null=True, max_length=128, verbose_name=_("litteraturlabbet.author.name"))
    formatted_name = models.CharField(blank=True, null=True, max_length=128, verbose_name=_("litteraturlabbet.author.formatted_name"))
    surname = models.CharField(blank=True, null=True, max_length=128, verbose_name=_("litteraturlabbet.author.surname"))

    birth_year = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=_("litteraturlabbet.author.birth_year"))
    death_year = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=_("litteraturlabbet.author.death_year"))


class Work(abstract.AbstractBaseModel):

    
    title = models.CharField( blank=True, null=True, max_length=1024, default="", verbose_name=_("litteraturlabbet.work.title"))
    short_title = models.CharField(max_length=256, blank=True, null=True, verbose_name=_("litteraturlabbet.work.short_title"))
    modernized_title = models.CharField(max_length=1024, blank=True, null=True, verbose_name=_("littearturlabbet.work.modernized_title"))

    lbworkid = models.CharField(unique=True, max_length=128, verbose_name=_("litteraturlabbet.work.lbworkid"))
    librisid = models.CharField(max_length=128, blank=True, null=True, verbose_name=_("litteraturlabbet.work.librisid")) 

    main_author   = models.ForeignKey(Author, blank=True, null=True, verbose_name=_("litteraturlabbet.work.author"), on_delete=models.CASCADE)
    authors  = models.ManyToManyField(Author, related_name='works', verbose_name=_("litteraturlabbet.work.authors"))

    edition  = models.CharField(max_length=128, blank=True, null=True, verbose_name=_("litteraturlabbet.work.edition"))

    language = models.CharField(max_length=128, blank=True, null=True, verbose_name=_("litteraturlabbet.work.language"))

    imprint_year = models.PositiveSmallIntegerField(default=None, blank=True, null=True, verbose_name=_("litteraturlabbet.work.imprint_year"))
    sort_year    = models.PositiveSmallIntegerField(default=None, blank=True, null=True, verbose_name=_("litteraturlabbet.work.sort_year"))
    
    word_count = models.PositiveIntegerField(verbose_name=_("litteraturlabbet.work.word_count"), blank=True, null=True, )

    @property
    def page_count(self):
        return self.pages.count()


class Page(abstract.AbstractDocumentModel):

    work = models.ForeignKey(Work, verbose_name=_("litteraturlabbet.work.work"), on_delete=models.CASCADE, related_name='pages')
    number = models.PositiveIntegerField(verbose_name=_("litteraturlabbet.cluster.size"))

    class Meta:
        ordering = ['-number']
        constraints = [
            models.UniqueConstraint(fields=['work', 'number'], name='unique page-work identifier')
        ]

class Cluster(abstract.AbstractBaseModel):

    id = models.PositiveBigIntegerField(unique=True, primary_key=True)
    size = models.PositiveIntegerField(verbose_name=_("litteraturlabbet.cluster.size"))

class Segment(abstract.AbstractBaseModel):
    
    uid = models.CharField(max_length=256, default="")
    gid = models.CharField(max_length=256, default="")

    bw = models.PositiveIntegerField(verbose_name=_("litteraturlabbet.segment.bw"))
    ew = models.PositiveIntegerField(verbose_name=_("litteraturlabbet.segment.ew"))
    begin = models.PositiveIntegerField(verbose_name=_("litteraturlabbet.segment.begin"))
    end = models.PositiveIntegerField(verbose_name=_("litteraturlabbet.segment.end"))

    cluster = models.ForeignKey(Cluster, verbose_name=_("litteraturlabbet.segment.cluster"), on_delete=models.CASCADE, related_name='segments')
    page = models.ForeignKey(Page, verbose_name=_("litteraturlabbet.segment.page"), on_delete=models.CASCADE)
    text = models.TextField(default="", verbose_name=_("litteraturlabbet.segment.text"))

    series =models.CharField(max_length=64, verbose_name=_("litteraturlabbet.segment.series"))


