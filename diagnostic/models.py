from django.db import models
from django.shortcuts import render, redirect

from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from modelcluster.fields import ParentalKey

from .forms import ExpressDiagnosticForm, DiagnosticCompletForm, RdvRequestForm
from .scoring import calcul_score_express, niveau_et_gain


# -------------------------
# DB MODELS (CRM / relance)
# -------------------------

class DiagnosticSubmission(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # Lead
    nom = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=40, blank=True)
    entreprise = models.CharField(max_length=160, blank=True)
    prefere_whatsapp = models.BooleanField(default=False)

    # Réponses Express (5)
    q1_secteur = models.CharField(max_length=50, blank=True)
    q2_taille = models.CharField(max_length=50, blank=True)
    q3_fonction = models.CharField(max_length=50, blank=True)
    q4_urgence = models.CharField(max_length=50, blank=True)
    q5_donnees = models.CharField(max_length=50, blank=True)

    # Réponses Complet (7)
    c1_risque_erreur = models.CharField(max_length=50, blank=True)
    c2_pertes = models.CharField(max_length=50, blank=True)
    c3_stockage_data = models.CharField(max_length=50, blank=True)
    c4_usage_ia = models.CharField(max_length=50, blank=True)
    c5_objectif = models.CharField(max_length=50, blank=True)
    c6_frequence_reporting = models.CharField(max_length=50, blank=True)
    c7_priorite_process = models.CharField(max_length=50, blank=True)
    complet_done = models.BooleanField(default=False)

    # Scoring
    score = models.IntegerField(default=0)
    # critique/intermediaire/avance (ou rouge/orange/vert)
    niveau = models.CharField(max_length=30, blank=True)
    estimation_gain = models.CharField(max_length=60, blank=True)

    # Tracking
    utm_source = models.CharField(max_length=80, blank=True)
    utm_campaign = models.CharField(max_length=80, blank=True)

    def __str__(self):
        ident = self.email or self.telephone or self.nom or "Lead"
        return f"{ident} ({self.created_at:%Y-%m-%d})"


class RdvRequest(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    submission = models.ForeignKey(
        "diagnostic.DiagnosticSubmission",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rdvs",
    )

    nom = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=40)

    creneau = models.CharField(max_length=80)
    canal = models.CharField(
        max_length=30,
        choices=[("appel", "Appel"), ("whatsapp",
                                      "WhatsApp"), ("visio", "Visio")],
        default="appel",
    )
    besoin = models.TextField(blank=True)

    def __str__(self):
        return f"RDV {self.creneau} - {self.telephone}"


# -------------------------
# WAGTAIL PAGES (Tunnel IA)
# -------------------------

# PAGE A — Landing
class DiagnosticIAIndexPage(Page):
    template = "diagnostic/diagnostic_ia_index_page.html"

    intro = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    subpage_types = [
        "diagnostic.DiagnosticExpressPage",
        "diagnostic.CaptureLeadPage",
        "diagnostic.DiagnosticCompletPage",
        "diagnostic.DiagnosticResultatPage",
        "diagnostic.DiagnosticRdvPage",
    ]


# PAGE B — Express
class DiagnosticExpressPage(Page):
    parent_page_types = ["diagnostic.DiagnosticIAIndexPage"]
    template = "diagnostic/diagnostic_express_page.html"

    def serve(self, request):
        if request.method == "POST":
            form = ExpressDiagnosticForm(request.POST)
            if form.is_valid():
                request.session["diag_express"] = form.cleaned_data
                request.session.modified = True
                return redirect("/diagnostic-ia/recevoir-resultat/")
        else:
            form = ExpressDiagnosticForm(
                initial=request.session.get("diag_express", {}))

        return render(request, self.template, {"page": self, "form": form})


# PAGE C — Capture lead (Wagtail Form)
class FormField(AbstractFormField):
    page = ParentalKey(
        "diagnostic.CaptureLeadPage",
        on_delete=models.CASCADE,
        related_name="form_fields",
    )


class CaptureLeadPage(AbstractEmailForm):
    parent_page_types = ["diagnostic.DiagnosticIAIndexPage"]
    template = "diagnostic/capture_lead_page.html"
    landing_page_template = "diagnostic/capture_lead_thanks.html"

    intro = models.TextField(blank=True)

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel("intro"),
        InlinePanel("form_fields", label="Champs du formulaire"),
        FieldPanel("to_address"),
        FieldPanel("from_address"),
        FieldPanel("subject"),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["next_step"] = request.GET.get("next", "")
        return context

    def process_form_submission(self, form):
        submission = super().process_form_submission(form)

        request = form.request  # Wagtail injecte request dans le form
        express = request.session.get("diag_express", {})
        # ✅ si l'utilisateur a fait "complet" avant le lead
        complet = request.session.get("diag_complet", {})

        data = form.cleaned_data
        nom = data.get("nom", "")
        email = data.get("email", "")
        telephone = data.get("telephone", "")
        entreprise = data.get("entreprise", "")
        prefere_whatsapp = bool(data.get("prefere_whatsapp", False))

        # tracking UTM
        utm_source = request.GET.get(
            "utm_source", "") or request.session.get("utm_source", "")
        utm_campaign = request.GET.get(
            "utm_campaign", "") or request.session.get("utm_campaign", "")

        # score minimal sur express (si express absent, score=0)
        score = calcul_score_express(express)
        niveau, gain = niveau_et_gain(score)

        # Crée la soumission persistante CRM
        sub = DiagnosticSubmission.objects.create(
            nom=nom,
            email=email,
            telephone=telephone,
            entreprise=entreprise,
            prefere_whatsapp=prefere_whatsapp,

            q1_secteur=express.get("q1_secteur", ""),
            q2_taille=express.get("q2_taille", ""),
            q3_fonction=express.get("q3_fonction", ""),
            q4_urgence=express.get("q4_urgence", ""),
            q5_donnees=express.get("q5_donnees", ""),

            # complet (si dispo)
            c1_risque_erreur=complet.get("c1_risque_erreur", ""),
            c2_pertes=complet.get("c2_pertes", ""),
            c3_stockage_data=complet.get("c3_stockage_data", ""),
            c4_usage_ia=complet.get("c4_usage_ia", ""),
            c5_objectif=complet.get("c5_objectif", ""),
            c6_frequence_reporting=complet.get("c6_frequence_reporting", ""),
            c7_priorite_process=complet.get("c7_priorite_process", ""),
            complet_done=bool(complet),

            score=score,
            niveau=niveau,
            estimation_gain=gain,

            utm_source=utm_source,
            utm_campaign=utm_campaign,
        )

        # garde l’ID en session pour Résultat/CRM
        request.session["diag_last_id"] = sub.id
        request.session.modified = True

        return submission


# PAGE D — Complet (accessible même sans lead)
class DiagnosticCompletPage(Page):
    parent_page_types = ["diagnostic.DiagnosticIAIndexPage"]
    template = "diagnostic/diagnostic_complet_page.html"

    def serve(self, request):
        last_id = request.session.get("diag_last_id")
        sub = DiagnosticSubmission.objects.filter(
            id=last_id).first() if last_id else None

        if request.method == "POST":
            form = DiagnosticCompletForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data

                # ✅ Si lead existe : on enregistre direct en DB
                if sub:
                    for k, v in data.items():
                        setattr(sub, k, v)
                    sub.complet_done = True

                    # recalcul score (express + pondération complet)
                    express = request.session.get("diag_express", {})
                    score = calcul_score_express(express)

                    score += {"faible": 5, "moyen": 10,
                              "eleve": 15}.get(sub.c1_risque_erreur, 0)
                    score += {"0_1": 5, "1_5": 10, "5_20": 15,
                              "20_plus": 20}.get(sub.c2_pertes, 0)
                    score += {"whatsapp_excel": 0, "drive": 5,
                              "crm_erp": 10, "dwh": 15}.get(sub.c3_stockage_data, 0)
                    score += {"aucun": 0, "ponctuel": 5, "regulier": 10,
                              "industrialise": 15}.get(sub.c4_usage_ia, 0)

                    niveau, gain = niveau_et_gain(score)
                    sub.score = min(score, 100)
                    sub.niveau = niveau
                    sub.estimation_gain = gain
                    sub.save()

                    return redirect("/diagnostic-ia/resultat/")

                # ✅ Sinon : on stocke en session, puis on demande le lead
                request.session["diag_complet"] = data
                request.session.modified = True
                return redirect("/diagnostic-ia/recevoir-resultat/?next=complet")

        else:
            # pré-remplissage
            if sub and sub.complet_done:
                initial = {
                    "c1_risque_erreur": sub.c1_risque_erreur,
                    "c2_pertes": sub.c2_pertes,
                    "c3_stockage_data": sub.c3_stockage_data,
                    "c4_usage_ia": sub.c4_usage_ia,
                    "c5_objectif": sub.c5_objectif,
                    "c6_frequence_reporting": sub.c6_frequence_reporting,
                    "c7_priorite_process": sub.c7_priorite_process,
                }
            else:
                initial = request.session.get("diag_complet", {})

            form = DiagnosticCompletForm(initial=initial)

        return render(request, self.template, {"page": self, "form": form, "lead": sub})


# PAGE E — Résultat
class DiagnosticResultatPage(Page):
    parent_page_types = ["diagnostic.DiagnosticIAIndexPage"]
    template = "diagnostic/diagnostic_resultat_page.html"

    def serve(self, request):
        last_id = request.session.get("diag_last_id")

        # 1) lecture DB
        if last_id:
            sub = DiagnosticSubmission.objects.filter(id=last_id).first()
            if sub:
                return render(request, self.template, {
                    "page": self,
                    "score": sub.score,
                    "niveau": sub.niveau,
                    "estimation_gain": sub.estimation_gain,
                    "lead": sub,
                    "from_db": True,
                })

        # 2) fallback session express
        express = request.session.get("diag_express")
        if express:
            score = calcul_score_express(express)
            niveau, gain = niveau_et_gain(score)
            return render(request, self.template, {
                "page": self,
                "score": score,
                "niveau": niveau,
                "estimation_gain": gain,
                "from_db": False,
            })

        return redirect("/diagnostic-ia/express/")


# PAGE F — RDV
class DiagnosticRdvPage(Page):
    parent_page_types = ["diagnostic.DiagnosticIAIndexPage"]
    template = "diagnostic/diagnostic_rdv_page.html"

    intro = models.TextField(blank=True)
    calendly_url = models.URLField(
        blank=True, help_text="Si renseigné, on affiche Calendly (embed).")

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("calendly_url"),
    ]

    def serve(self, request):
        last_id = request.session.get("diag_last_id")
        sub = DiagnosticSubmission.objects.filter(
            id=last_id).first() if last_id else None

        # Calendly
        if self.calendly_url:
            return render(request, self.template, {"page": self, "lead": sub})

        # Form interne
        if request.method == "POST":
            form = RdvRequestForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                RdvRequest.objects.create(
                    submission=sub,
                    nom=data.get("nom") or (sub.nom if sub else ""),
                    email=data.get("email") or (sub.email if sub else ""),
                    telephone=data["telephone"],
                    creneau=data["creneau"],
                    canal=data["canal"],
                    besoin=data.get("besoin", ""),
                )
                return redirect(self.url + "?ok=1")
        else:
            initial = {}
            if sub:
                initial = {"nom": sub.nom, "email": sub.email,
                           "telephone": sub.telephone}
            form = RdvRequestForm(initial=initial)

        return render(request, self.template, {"page": self, "form": form, "lead": sub})
