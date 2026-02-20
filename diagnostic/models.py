# diagnostic/models.py
import uuid
from django.db import models
from django.utils import timezone

from wagtail.models import Page
from wagtail.admin.panels import FieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from django.shortcuts import redirect
from .forms import PlanActionForm


class DiagnosticIAIndexPage(RoutablePageMixin, Page):
    template = "diagnostic/index.html"
    intro = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_session_key(self, request):
        if not request.session.session_key:
            request.session.create()
        return request.session.session_key

    @route(r"^express/$")
    def express(self, request):
        from .forms import DiagnosticExpressForm
        from .models import compute_score_express

        if request.method == "POST":
            form = DiagnosticExpressForm(request.POST)
            if form.is_valid():
                reponses = form.cleaned_data
                score = compute_score_express(reponses)

                request.session["diag_express"] = reponses
                request.session["diag_score_express"] = score
                return redirect(self.url + "contact/")
        else:
            form = DiagnosticExpressForm()

        return self.render(
            request,
            template="diagnostic/express.html",
            context_overrides={"form": form},
        )

    @route(r"^contact/$")
    def contact(self, request):
        from .forms import DiagnosticContactForm
        from .models import DiagnosticLead

        if "diag_express" not in request.session:
            return redirect(self.url + "express/")

        if request.method == "POST":
            form = DiagnosticContactForm(request.POST)
            if form.is_valid():
                session_key = self.get_session_key(request)
                reponses_express = request.session.get("diag_express", {})
                score_express = int(
                    request.session.get("diag_score_express", 0))

                lead = DiagnosticLead.objects.create(
                    session_key=session_key,
                    public_id=uuid.uuid4(),
                    nom=form.cleaned_data["nom"],
                    email=form.cleaned_data["email"],
                    telephone=form.cleaned_data.get("telephone", ""),

                    score_express=score_express,
                    score_total=score_express,  # provisoire avant complet
                    taille=reponses_express.get("q1_label", ""),
                    reponses_express=reponses_express,
                )

                request.session["diag_lead_id"] = lead.id
                return redirect(self.url + "complet/")
        else:
            form = DiagnosticContactForm()

        return self.render(
            request,
            template="diagnostic/contact.html",
            context_overrides={"form": form},
        )

    @route(r"^complet/$")
    def complet(self, request):
        from .forms import DiagnosticCompletForm
        from .models import DiagnosticLead, compute_score_complet, compute_niveau

        lead_id = request.session.get("diag_lead_id")
        if not lead_id:
            return redirect(self.url + "express/")

        lead = DiagnosticLead.objects.filter(id=lead_id).first()
        if not lead:
            return redirect(self.url + "express/")

        if request.method == "POST":
            form = DiagnosticCompletForm(request.POST)
            if form.is_valid():
                reponses = form.cleaned_data
                score_complet = compute_score_complet(reponses)

                lead.reponses_complet = reponses
                lead.score_complet = score_complet
                lead.score_total = lead.score_express + score_complet
                lead.niveau = compute_niveau(lead.score_total)

                # infos business utiles
                lead.secteur = reponses.get("q6_label", "")
                lead.priorite = reponses.get("q12_label", "")
                lead.save()

                return redirect(self.url + "resultat/")
        else:
            form = DiagnosticCompletForm()

        return self.render(
            request,
            template="diagnostic/complet.html",
            context_overrides={"form": form, "lead": lead},
        )

    @route(r"^resultat/$")
    def resultat(self, request):
        from .models import DiagnosticLead

        lead_id = request.session.get("diag_lead_id")
        if not lead_id:
            return redirect(self.url + "express/")

        lead = DiagnosticLead.objects.filter(id=lead_id).first()
        if not lead:
            return redirect(self.url + "express/")

        niveau = lead.niveau or "opportunite"
        score = lead.score_total

        if niveau == "sensibilisation":
            titre = "Niveau 1 — Sensibilisation"
            gain = "≈ +5% à +10%"
            reco = [
                "Former les équipes aux bases de l’IA et de la data",
                "Choisir 1 processus répétitif à améliorer rapidement",
                "Centraliser vos fichiers et sécuriser les versions",
            ]
        elif niveau == "opportunite":
            titre = "Niveau 2 — Opportunité d’automatisation"
            gain = "≈ +10% à +25%"
            reco = [
                "Automatiser 1–2 tâches à forte répétition (rapports, saisies, contrôle)",
                "Mettre en place 3 indicateurs clés (tableau de bord)",
                "Structurer le stockage (référentiel + droits + versions)",
            ]
        else:
            titre = "Niveau 3 — Prêt pour un projet IA rentable"
            gain = "≈ +20% à +40%"
            reco = [
                "Cadrer un cas d’usage prioritaire avec ROI (4–6 semaines)",
                "Mettre en place qualité des données + gouvernance",
                "Lancer un POC IA (assistant interne / automatisation / prédiction)",
            ]

        return self.render(
            request,
            template="diagnostic/resultat.html",
            context_overrides={
                "lead": lead,
                "titre": titre,
                "gain": gain,
                "reco": reco,
                "score": score,
            },
        )

    @route(r"^plan-action/$")
    def plan_action(self, request):
        # 1) essayer session

        lead_id = request.session.get("diag_lead_id")
        print("request", lead_id)
        lead = None

        if lead_id:
            lead = DiagnosticLead.objects.filter(id=lead_id).first()
        print("lean", lead)
        # 2) fallback token URL ?k=...
        if not lead:
            token = request.GET.get("k")
            if token:
                lead = DiagnosticLead.objects.filter(public_id=token).first()

        if not lead:
            return redirect(self.url + "express/")
        print("POST", request.method)
        if request.method == "POST":
            form = PlanActionForm(request.POST)
            if form.is_valid():
                req = PlanActionRequest.objects.create(
                    lead=lead,
                    objectif=form.cleaned_data.get(
                        "objectif") or lead.priorite,
                    probleme_principal=form.cleaned_data["probleme_principal"],
                    outils_actuels=form.cleaned_data.get("outils_actuels", ""),
                )

                # email simple (à toi + confirmation)
                from django.core.mail import send_mail
                send_mail(
                    subject="Nouvelle demande de plan d’action",
                    message=f"Nom: {lead.nom}\nEmail: {lead.email}\nTel: {lead.telephone}\n"
                            f"Niveau: {lead.niveau} Score:{lead.score_total}\n"
                            f"Objectif: {req.objectif}\nProblème: {req.probleme_principal}\nOutils: {req.outils_actuels}\n",
                    from_email=None,
                    # mets ton email
                    recipient_list=["contact@kerenes-digital.com"],
                    fail_silently=True,
                )
                return redirect(self.url + "plan-action/merci/")
        else:
            # GET -> afficher le formulaire pré-rempli
            form = PlanActionForm(initial={"objectif": lead.priorite or ""})

        return self.render(
            request,
            template="diagnostic/plan_action.html",
            context_overrides={"form": form, "lead": lead},
        )

    @route(r"^plan-action/merci/?$")
    def plan_action_merci(self, request):
        # Optionnel : récupérer le lead pour personnaliser le message
        lead = None
        lead_id = request.session.get("diag_lead_id")
        if lead_id:
            lead = DiagnosticLead.objects.filter(id=lead_id).first()

        if not lead:
            token = request.GET.get("k")
            if token:
                lead = DiagnosticLead.objects.filter(public_id=token).first()

        return self.render(
            request,
            template="diagnostic/plan_action_thanks.html",
            context_overrides={"lead": lead},
        )


class DiagnosticLead(models.Model):
    session_key = models.CharField(max_length=64, db_index=True)
    created_at = models.DateTimeField(default=timezone.now)
    public_id = models.UUIDField(
        null=True, blank=True, editable=False, db_index=True)
    nom = models.CharField(max_length=120)
    email = models.EmailField()
    telephone = models.CharField(max_length=40, blank=True)

    score_express = models.IntegerField(default=0)
    score_complet = models.IntegerField(default=0)
    score_total = models.IntegerField(default=0)
    # sensibilisation / opportunite / pret
    niveau = models.CharField(max_length=20, blank=True)

    taille = models.CharField(max_length=40, blank=True)
    secteur = models.CharField(max_length=50, blank=True)
    priorite = models.CharField(max_length=50, blank=True)

    reponses_express = models.JSONField(default=dict, blank=True)
    reponses_complet = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.nom} - {self.email}"


# --- scoring helpers ---

def score_from_keys(data: dict, keys: list[str]) -> int:
    # attend des valeurs "0".."3" pour chaque clé
    return sum(int(data.get(k, "0")) for k in keys)


def compute_score_express(data: dict) -> int:
    return score_from_keys(data, ["q1", "q2", "q3", "q4"])


def compute_score_complet(data: dict) -> int:
    # Q8 (risque) est un levier fort → bonus si "3"
    base = score_from_keys(data, ["q6", "q7", "q8", "q9", "q10", "q11", "q12"])
    bonus = 2 if data.get("q8") == "3" else 0
    return base + bonus


def compute_niveau(score_total: int) -> str:
    # Ajuste les seuils si besoin après quelques semaines de data
    if score_total <= 12:
        return "sensibilisation"
    if score_total <= 22:
        return "opportunite"
    return "pret"


class PlanActionRequest(models.Model):
    lead = models.ForeignKey("diagnostic.DiagnosticLead",
                             on_delete=models.CASCADE, related_name="plans")
    created_at = models.DateTimeField(default=timezone.now)

    objectif = models.CharField(max_length=100, blank=True)
    probleme_principal = models.CharField(max_length=160)
    outils_actuels = models.CharField(max_length=160, blank=True)

    # nouveau / en_cours / envoyé
    statut = models.CharField(max_length=30, default="nouveau")
