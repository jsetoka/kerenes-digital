from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wagtail.snippets.models import register_snippet
from django.utils.text import slugify
from modelcluster.fields import ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey
from django.shortcuts import redirect



class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Base queryset : tous les articles sous cet index, récents d'abord
        qs = (BlogPage.objects.live().public()
              .descendant_of(self)
              .order_by("-date"))  # ou "-first_published_at" si tu préfères

        # Filtres GET
        tag = (request.GET.get("tag") or "").strip()
        if tag:
            qs = qs.filter(tags__name=tag)

        cat = (request.GET.get("cat") or "").strip()
        if cat:
            qs = qs.filter(categories__slug=cat)

        qs = qs.distinct()  # évite les doublons si jointures

        # À la une (non paginés) — respectent les filtres
        featured_qs = qs.filter(featured=True)[:3]
        context["featured_articles"] = featured_qs

        # Récents (paginés) — on exclut ceux déjà "à la une"
        recent_qs = qs.exclude(id__in=featured_qs.values("id"))

        page_number = request.GET.get("page", 1)
        per_page = 6

        paginator = Paginator(recent_qs, per_page)
        try:
            posts = paginator.page(page_number)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context.update({
            "posts": posts,
            "paginator": paginator,
            "page_number": posts.number,
            "active_tag": tag or None,
            "active_cat": cat or None,
        })
        return context

    
class BlogPageTag(TaggedItemBase):
    content_object = ParentalKey("blog.BlogPage", related_name="tagged_items", on_delete=models.CASCADE)

class BlogPage(Page):
    date = models.DateField("Date de publication")
    intro = RichTextField(features=["bold", "italic"])
    body = RichTextField(features=["bold", "italic", "link", "image", "embed"])
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )
    featured = models.BooleanField(
        default=False,
        verbose_name="Mettre à la une",
        help_text="Si coché, l’article peut apparaître dans le bandeau À la une."
    )
    tags = ClusterTaggableManager(through=BlogPageTag, blank=True)
    categories = ParentalManyToManyField("blog.BlogCategory", blank=True)


    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("image"),
        FieldPanel("featured"),
        FieldPanel("tags"),
        FieldPanel("categories"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        # Base: mêmes section / parent (si tu utilises un BlogIndexPage)
        try:
            index = self.get_parent()
            qs_base = BlogPage.objects.live().public().descendant_of(index)
        except Exception:
            qs_base = BlogPage.objects.live().public()

        context["recent_articles"] = (
            qs_base.exclude(id=self.id)
                   .order_by("-date", "-first_published_at")[:6]
        )
        return context
    
@register_snippet
class BlogCategory(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, help_text="Utilisé dans l’URL ou les filtres ?cat=slug")
    description = models.TextField(blank=True)

    panels = [FieldPanel("name"), FieldPanel("slug"), FieldPanel("description")]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)