# on va l'étendre plus bas si tu veux
from .scoring import calcul_score_express, niveau_et_gain
from .forms import DiagnosticCompletForm
from django.shortcuts import render, redirect
from .scoring import calcul_score_express, niveau_et_gain
from django.db import models
from wagtail.models import Page
from django.shortcuts import redirect, render
from django.urls import reverse
from .forms import ExpressDiagnosticForm
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.admin.panels import FieldPanel, InlinePanel
from modelcluster.fields import ParentalKey
from .forms import RdvRequestForm
# PAGE A — Landing


class DiagnosticIAIndexPage(Page):
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
                # Stockage en session
                request.session["diag_express"] = form.cleaned_data
                request.session.modified = True

                # Redirection vers la capture lead (Page C)
                # Option 1 (simple): URL en dur (ok si stable)
                return redirect("/diagnostic-ia/recevoir-resultat/")

                # Option 2 (propre): retrouver la page enfant "recevoir-resultat"
                # (on le fera ensuite si tu veux)
        else:
            form = ExpressDiagnosticForm(
                initial=request.session.get("diag_express", {}))

        return render(request, self.template, {"page": self, "form": form})


# PAGE C — Capture lead


class CaptureLeadFormField(AbstractFormField):
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

    def process_form_submission(self, form):
        """
        Appelé quand le formulaire Wagtail est validé.
        On sauvegarde 1) la submission Wagtail (pour export)
        + 2) notre DiagnosticSubmission (lead + réponses + score)
        """
        submission = super().process_form_submission(form)

        # 1) Récupérer les réponses Express depuis la session
        request = form.request  # Wagtail ajoute request au form
        express = request.session.get("diag_express", {})

        # 2) Extraire les champs lead (selon les names de tes form_fields)
        data = form.cleaned_data
        nom = data.get("nom", "")
        email = data.get("email", "")
        telephone = data.get("telephone", "")
        entreprise = data.get("entreprise", "")
        prefere_whatsapp = bool(data.get("prefere_whatsapp", False))

        # 3) Calcul score + niveau
        score = calcul_score_express(express)
        niveau, gain = niveau_et_gain(score)

        # 4) Tracking UTM (optionnel)
        utm_source = request.GET.get(
            "utm_source", "") or request.session.get("utm_source", "")
        utm_campaign = request.GET.get(
            "utm_campaign", "") or request.session.get("utm_campaign", "")

        DiagnosticSubmission.objects.create(
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

            score=score,
            niveau=niveau,
            estimation_gain=gain,

            utm_source=utm_source,
            utm_campaign=utm_campaign,
        )

        # 5) Optionnel : garder l’ID en session pour la page Résultat
        last = DiagnosticSubmission.objects.filter(
            email=email).order_by("-created_at").first()
        if last:
            request.session["diag_last_id"] = last.id
            request.session.modified = True

        return submission


# PAGE D — Complet
class DiagnosticCompletPage(Page):
    parent_page_types = ["diagnostic.DiagnosticIAIndexPage"]


# PAGE E — Résultat
class DiagnosticResultatPage(Page):
    parent_page_types = ["diagnostic.DiagnosticIAIndexPage"]
    template = "diagnostic/diagnostic_resultat_page.html"

    def calcul_score(self, data):
        score = 0

        # q5_donnees
        score += {
            "dispersees": 5,
            "partielles": 10,
            "structurees": 20,
            "avancees": 25,
        }.get(data.get("q5_donnees"), 0)

        # q4_urgence
        score += {
            "elevee": 20,
            "moyenne": 10,
            "faible": 5,
        }.get(data.get("q4_urgence"), 0)

        # q2_taille
        score += {
            "1_10": 5,
            "11_50": 10,
            "51_200": 15,
            "200_plus": 20,
        }.get(data.get("q2_taille"), 0)

        # q3_fonction
        if data.get("q3_fonction") == "dirigeant":
            score += 15
        else:
            score += 5

        # q1_secteur
        if data.get("q1_secteur") in ["industrie_btp", "banque"]:
            score += 10
        else:
            score += 5

        return score

    def niveau(self, score):
        if score < 40:
            return "critique"
        elif score < 70:
            return "intermediaire"
        return "avance"

    def serve(self, request):

        # 1️⃣ PRIORITÉ : Lire en base (persistant CRM)
        last_id = request.session.get("diag_last_id")

        if last_id:
            sub = DiagnosticSubmission.objects.filter(id=last_id).first()
            if sub:
                context = {
                    "page": self,
                    "score": sub.score,
                    "niveau": sub.niveau,
                    "estimation_gain": sub.estimation_gain,
                    "lead": sub,
                    "from_db": True,
                }
                return render(request, self.template, context)

        # 2️⃣ SECOURS : Lire la session (avant capture lead)
        express = request.session.get("diag_express")

        if express:
            score = calcul_score_express(express)
            niveau, gain = niveau_et_gain(score)

            context = {
                "page": self,
                "score": score,
                "niveau": niveau,
                "estimation_gain": gain,
                "from_db": False,
            }
            return render(request, self.template, context)

        # 3️⃣ Rien trouvé → retour début tunnel
        return redirect("/diagnostic-ia/express/")


# PAGE F — RDV
class DiagnosticRdvPage(Page):
    parent_page_types = ["diagnostic.DiagnosticIAIndexPage"]


class DiagnosticSubmission(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # Lead
    nom = models.CharField(max_length=120)
    email = models.EmailField()
    telephone = models.CharField(max_length=40, blank=True)
    entreprise = models.CharField(max_length=160, blank=True)
    prefere_whatsapp = models.BooleanField(default=False)

    # Réponses Express (stockées en "valeurs" + libellés si tu veux)
    q1_secteur = models.CharField(max_length=50, blank=True)
    q2_taille = models.CharField(max_length=50, blank=True)
    q3_fonction = models.CharField(max_length=50, blank=True)
    q4_urgence = models.CharField(max_length=50, blank=True)
    q5_donnees = models.CharField(max_length=50, blank=True)

    # Scoring
    score = models.IntegerField(default=0)
    # critique/intermediaire/avance
    niveau = models.CharField(max_length=30, blank=True)
    estimation_gain = models.CharField(max_length=60, blank=True)

    # Optionnel : tracking
    utm_source = models.CharField(max_length=80, blank=True)
    utm_campaign = models.CharField(max_length=80, blank=True)

    def __str__(self):
        return f"{self.nom} - {self.email} ({self.created_at:%Y-%m-%d})"


class RdvRequest(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    # Optionnel : lien vers le lead du diagnostic (si tu as DiagnosticSubmission)
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
        # On tente de récupérer le lead du diagnostic (si existant)
        sub = None
        last_id = request.session.get("diag_last_id")
        if last_id:
            sub = DiagnosticSubmission.objects.filter(id=last_id).first()

        # Si Calendly est configuré → on affiche juste l’embed
        if self.calendly_url:
            return render(request, self.template, {"page": self, "lead": sub})

        # Sinon : formulaire interne
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


# --- Réponses Diagnostic complet ---
c1_risque_erreur = models.CharField(max_length=50, blank=True)
c2_pertes = models.CharField(max_length=50, blank=True)
c3_stockage_data = models.CharField(max_length=50, blank=True)
c4_usage_ia = models.CharField(max_length=50, blank=True)
c5_objectif = models.CharField(max_length=50, blank=True)
c6_frequence_reporting = models.CharField(max_length=50, blank=True)
c7_priorite_process = models.CharField(max_length=50, blank=True)

# Marqueur
complet_done = models.BooleanField(default=False)


class DiagnosticCompletPage(Page):
    parent_page_types = ["diagnostic.DiagnosticIAIndexPage"]
    template = "diagnostic/diagnostic_complet_page.html"

    def serve(self, request):
        # Il faut un lead enregistré (après capture)
        last_id = request.session.get("diag_last_id")
        if not last_id:
            return redirect("/diagnostic-ia/recevoir-resultat/")

        # récupère la soumission
        sub = DiagnosticSubmission.objects.filter(id=last_id).first()
        if not sub:
            return redirect("/diagnostic-ia/recevoir-resultat/")

        if request.method == "POST":
            form = DiagnosticCompletForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data

                # Sauvegarde dans DiagnosticSubmission
                for k, v in data.items():
                    setattr(sub, k, v)
                sub.complet_done = True

                # Option: recalcul score (express + complet)
                # Pour l’instant on garde score existant si déjà calculé, sinon express.
                express = request.session.get("diag_express", {})
                score = calcul_score_express(express)

                # Bonus : pondération "complet" simple
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
        else:
            # pré-remplir si déjà répondu
            initial = {
                "c1_risque_erreur": sub.c1_risque_erreur,
                "c2_pertes": sub.c2_pertes,
                "c3_stockage_data": sub.c3_stockage_data,
                "c4_usage_ia": sub.c4_usage_ia,
                "c5_objectif": sub.c5_objectif,
                "c6_frequence_reporting": sub.c6_frequence_reporting,
                "c7_priorite_process": sub.c7_priorite_process,
            }
            form = DiagnosticCompletForm(initial=initial)

        return render(request, self.template, {"page": self, "form": form, "lead": sub})
