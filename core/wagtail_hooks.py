from time import time
from wagtail import hooks
from django.templatetags.static import static
from django.utils.html import format_html


@hooks.register("insert_global_admin_js")
def inject_brand_js():
    from time import time
    from django.templatetags.static import static
    from django.utils.html import format_html
    return format_html(
        '<script>window.__DIBOS_LOGO__="{logo_header}";window.__DIBOS_LOGIN_LOGO__="{logo_login}";</script>'
        '<script src="{js}?v={v}"></script>',
        logo_header=static("core/img/logo-kerasgo.png"),
        logo_login=static("core/img/logo-kerasgo.png"),
        js=static("core/admin-brand.js"),
        v=int(time()),
    )

@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}?v={}">',
        static("core/admin-brand.css"),
        int(time())
    )