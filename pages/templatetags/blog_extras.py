from django import template
from collections import Counter
from wagtail.models import Page
from blog.models import BlogCategory, BlogPage  # ajuste import si app séparée

register = template.Library()

@register.inclusion_tag("blog/_recent_posts.html", takes_context=True)
def recent_posts(context, limit=5):
    posts = (Page.objects.live().type(BlogPage)
             .specific().order_by("-first_published_at")[:limit])
    return {"posts": posts}

@register.inclusion_tag("blog/_tag_cloud.html", takes_context=True)
def tag_cloud(context, limit=30):
    # Récupère les tags utilisés et leur fréquence
    posts = Page.objects.live().type(BlogPage).specific()
    counter = Counter()
    for p in posts:
        for t in p.tags.all():
            counter[t.name] += 1
    # tri par fréquence, puis alpha
    items = sorted(counter.items(), key=lambda x: (-x[1], x[0]))[:limit]
    # normalisation pour tailles (1..4)
    if items:
        maxc = max(c for _, c in items)
    else:
        maxc = 1
    cloud = [{"name": n, "count": c, "size": 1 + round(3*(c/maxc))} for n, c in items]
    return {"cloud": cloud}

@register.inclusion_tag("blog/_categories.html", takes_context=True)
def categories_list(context, limit=None, with_count=True):
    request = context["request"]
    page = context.get("page")

    # Trouve l'URL de base de l'index (si on est sur un article, remonter au parent)
    try:
        from blog.models import BlogIndexPage  # ajuste l'import si besoin
        if isinstance(getattr(page, "specific", page), BlogIndexPage):
            base_url = page.url
        else:
            base_url = page.get_parent().url  # parent de BlogPage = BlogIndexPage
    except Exception:
        base_url = "/blog/"  # fallback

    # Compte articles par catégorie
    from collections import Counter
    from wagtail.models import Page
    from blog.models import BlogPage, BlogCategory  # ajuste si autre app
    posts = Page.objects.live().type(BlogPage).specific()
    counter = Counter()
    for p in posts:
        for c in getattr(p, "categories", []).all():
            counter[c.slug] += 1

    cats = list(BlogCategory.objects.all().order_by("name"))
    items = [{"name": c.name, "slug": c.slug, "count": counter.get(c.slug, 0)} for c in cats]
    if limit:
        items = items[:int(limit)]

    return {
        "categories": items,
        "base_url": base_url,   # <- important pour générer les liens
        "with_count": with_count,
        "request": request,
    }

@register.inclusion_tag("blog/_featured.html", takes_context=True)
def featured_posts(context, count=3, index_page=None):
    """
    Récupère 'count' articles :
    - d'abord ceux marqués featured=True sous 'index_page' (si fourni),
    - sinon complète avec les plus récents.
    Retourne 1 principal + 2 secondaires.
    """
    from wagtail.models import Page
    # Import local pour éviter les imports circulaires
    from blog.models import BlogPage

    qs = BlogPage.objects.live().public().specific().order_by("-first_published_at")
    if index_page is not None:
        qs = qs.descendant_of(index_page)

    # d'abord les “à la une”
    featured_qs = qs.filter(featured=True)[:count]
    # si pas assez, on complète avec les récents non déjà pris
    if featured_qs.count() < count:
        remaining = count - featured_qs.count()
        ids_taken = [p.id for p in featured_qs]
        extra = qs.exclude(id__in=ids_taken)[:remaining]
        posts = list(featured_qs) + list(extra)
    else:
        posts = list(featured_qs)

    primary = posts[0] if posts else None
    secondary = posts[1:count] if len(posts) > 1 else []

    return {
        "primary": primary,
        "secondary": secondary,
        "request": context["request"],
    }