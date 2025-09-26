from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel
from wagtail.search import index
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
class BlogIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
   
        # Base queryset (tous les articles publiés, triés par date desc)
        articles_qs = BlogPage.objects.live().descendant_of(self).order_by("-date")

        # À la une (non paginés)
        context["featured_articles"] = articles_qs.filter(featured=True)[:3]

        # Récents (paginés)
        recent_qs = articles_qs.exclude(featured=True)

        page_number = request.GET.get("page", 1)
        per_page = 6  # nombre d’articles par page (ajuste selon ton besoin)

        paginator = Paginator(recent_qs, per_page)
        try:
            recent_page = paginator.page(page_number)
        except PageNotAnInteger:
            recent_page = paginator.page(1)
        except EmptyPage:
            recent_page = paginator.page(paginator.num_pages)

        context["recent_articles_page"] = recent_page          # objet de page
        context["paginator"] = paginator                       # optionnel
        context["page_number"] = int(recent_page.number)       # pratique en template

        return context

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
    featured = models.BooleanField(default=False, verbose_name="À la une")

    content_panels = Page.content_panels + [
        FieldPanel("date"),
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("image"),
        FieldPanel("featured"),
    ]
