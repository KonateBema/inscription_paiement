from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.shortcuts import render, get_object_or_404, redirect
from django.db import transaction
import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from .models import Inscription
from .forms import (PreinscriptionForm,InscriptionForm,ScolariteForm,EcheanceForm,PaiementForm,CandidatForm)
from .models import (Candidat,Preinscription,Etudiant,Classe,Scolarite,Paiement,Echeance,Recu,)
import qrcode
from pathlib import Path
from django.utils import timezone
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import logout

@require_POST
def deconnexion(request):

    logout(request)

    return redirect("login")

@login_required
def dashboard(request):

    # ==============================
    # ADMISSIONS
    # ==============================

    total_candidats = Candidat.objects.filter(
        actif=True
    ).count()

    preinscriptions_attente = Preinscription.objects.filter(
        statut="EN_ATTENTE"
    ).count()

    preinscriptions_validees = Preinscription.objects.filter(
        statut="VALIDEE"
    ).count()

    # ==============================
    # SCOLARITÉ
    # ==============================

    total_etudiants = Etudiant.objects.filter(
        actif=True
    ).count()

    total_inscriptions = Inscription.objects.filter(
        statut="INSCRIT"
    ).count()

    total_classes = Classe.objects.filter(
        active=True
    ).count()

    # ==============================
    # FINANCE
    # ==============================

    total_scolarites = (
        Scolarite.objects.aggregate(
            total=Sum("montant_net")
        )["total"]
        or Decimal("0")
    )

    total_encaisse = (
        Paiement.objects.filter(
            statut="VALIDE"
        ).aggregate(
            total=Sum("montant")
        )["total"]
        or Decimal("0")
    )

    reste_a_payer = total_scolarites - total_encaisse

    if reste_a_payer < 0:
        reste_a_payer = Decimal("0")

    # ==============================
    # ACTIVITÉS RÉCENTES
    # ==============================

    derniers_candidats = Candidat.objects.order_by(
        "-date_creation"
    )[:5]

    dernieres_preinscriptions = (
        Preinscription.objects
        .select_related(
            "candidat",
            "filiere",
            "niveau",
        )
        .order_by("-date_demande")[:5]
    )

    derniers_paiements = (
        Paiement.objects
        .select_related(
            "scolarite__inscription__etudiant__candidat",
        )
        .order_by("-date_paiement")[:5]
    )

    context = {
        # Admissions
        "total_candidats": total_candidats,
        "preinscriptions_attente": preinscriptions_attente,
        "preinscriptions_validees": preinscriptions_validees,

        # Scolarité
        "total_etudiants": total_etudiants,
        "total_inscriptions": total_inscriptions,
        "total_classes": total_classes,

        # Finance
        "total_scolarites": total_scolarites,
        "total_encaisse": total_encaisse,
        "reste_a_payer": reste_a_payer,

        # Activités
        "derniers_candidats": derniers_candidats,
        "dernieres_preinscriptions": dernieres_preinscriptions,
        "derniers_paiements": derniers_paiements,
    }

    return render(
        request,
        "gestion/dashboard.html",
        context
    )
    
# =========================================================
# CANDIDATS
# =========================================================


from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q

@login_required
def candidats_liste(request):

    # =========================
    # RÉCUPÉRATION DES CANDIDATS
    # =========================

    candidats = Candidat.objects.all().order_by("-id")

    # =========================
    # RECHERCHE
    # =========================

    recherche = request.GET.get("q", "").strip()

    if recherche:
        candidats = candidats.filter(
            Q(nom__icontains=recherche) |
            Q(prenoms__icontains=recherche) |
            Q(matricule_candidat__icontains=recherche) |
            Q(telephone__icontains=recherche)
        )

    # =========================
    # PAGINATION
    # =========================

    paginator = Paginator(candidats, 10)  # 10 candidats par page

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    # =========================
    # CONTEXT
    # =========================

    context = {
        "candidats": page_obj,
        "page_obj": page_obj,
        "paginator": paginator,
        "recherche": recherche,
    }

    return render(
        request,
        "gestion/candidats/liste.html",
        context
    )

@login_required
def candidat_ajouter(request):

    if request.method == "POST":

        form = CandidatForm(request.POST, request.FILES)

        if form.is_valid():

            candidat = form.save()

            messages.success(
                request,
                f"Le candidat {candidat.nom} {candidat.prenoms} "
                f"a été enregistré avec succès."
            )

            return redirect(
                "gestion:candidat_detail",
                pk=candidat.pk
            )

    else:

        form = CandidatForm()

    return render(
        request,
        "gestion/candidats/formulaire.html",
        {
            "form": form,
            "titre": "Nouveau candidat",
        }
    )


@login_required
def candidat_detail(request, pk):

    candidat = get_object_or_404(
        Candidat,
        pk=pk
    )

    return render(
        request,
        "gestion/candidats/detail.html",
        {
            "candidat": candidat,
        }
    )


@login_required
def candidat_modifier(request, pk):

    candidat = get_object_or_404(
        Candidat,
        pk=pk
    )

    if request.method == "POST":

        form = CandidatForm(
            request.POST,
            request.FILES,
            instance=candidat
        )

        if form.is_valid():

            candidat = form.save()

            messages.success(
                request,
                f"Le candidat {candidat.nom} {candidat.prenoms} "
                f"a été modifié avec succès."
            )

            return redirect(
                "gestion:candidat_detail",
                pk=candidat.pk
            )

    else:

        form = CandidatForm(
            instance=candidat
        )

    return render(
        request,
        "gestion/candidats/formulaire.html",
        {
            "form": form,
            "titre": "Modifier le candidat",
            "candidat": candidat,
        }
    )
    
@login_required
def preinscription_liste(request):

    preinscriptions = (
        Preinscription.objects
        .select_related(
            "candidat",
            "annee_academique",
            "filiere",
            "niveau",
        )
        .all()
    )

    recherche = request.GET.get("q", "").strip()
    statut = request.GET.get("statut", "").strip()

    if recherche:
        preinscriptions = preinscriptions.filter(
            Q(numero__icontains=recherche)
            | Q(candidat__nom__icontains=recherche)
            | Q(candidat__prenoms__icontains=recherche)
        )

    if statut:
        preinscriptions = preinscriptions.filter(
            statut=statut
        )

    context = {
        "preinscriptions": preinscriptions,
        "recherche": recherche,
        "statut_selectionne": statut,
        "statuts": Preinscription.STATUT_CHOICES,
    }

    return render(
        request,
        "gestion/preinscriptions/liste.html",
        context
    )

@login_required
def preinscription_create(request):

    if request.method == "POST":

        form = PreinscriptionForm(request.POST)

        if form.is_valid():

            preinscription = form.save()

            messages.success(
                request,
                f"La préinscription {preinscription.numero} "
                f"a été créée avec succès."
            )

            return redirect(
                "gestion:preinscription_detail",
                pk=preinscription.pk
            )

    else:

        form = PreinscriptionForm()

    return render(
        request,
        "gestion/preinscriptions/form.html",
        {
            "form": form,
            "titre": "Nouvelle préinscription",
            "bouton": "Enregistrer",
        }
    )

@login_required
def preinscription_detail(request, pk):

    preinscription = get_object_or_404(
        Preinscription.objects.select_related(
            "candidat",
            "annee_academique",
            "filiere",
            "niveau",
        ),
        pk=pk
    )

    return render(
        request,
        "gestion/preinscriptions/detail.html",
        {
            "preinscription": preinscription,
        }
    )
    

@login_required
def preinscription_update(request, pk):

    preinscription = get_object_or_404(
        Preinscription,
        pk=pk
    )

    if request.method == "POST":

        form = PreinscriptionForm(
            request.POST,
            instance=preinscription
        )

        if form.is_valid():

            preinscription = form.save()

            messages.success(
                request,
                f"La préinscription {preinscription.numero} a été modifiée avec succès."
            )

            return redirect(
                "gestion:preinscription_detail",
                pk=preinscription.pk
            )

    else:

        form = PreinscriptionForm(
            instance=preinscription
        )

    return render(
        request,
        "gestion/preinscriptions/form.html",
        {
            "form": form,
            "titre": "Modifier la préinscription",
            "bouton": "Enregistrer les modifications",
            "preinscription": preinscription,
        }
    )

@login_required
@require_POST
def preinscription_delete(request, pk):

    preinscription = Preinscription.objects.filter(pk=pk).first()

    # Si la préinscription n'existe plus
    if not preinscription:

        messages.warning(
            request,
            "Cette préinscription n'existe plus ou a déjà été supprimée."
        )

        return redirect(
            "gestion:preinscription_liste"
        )

    numero = preinscription.numero

    preinscription.delete()

    messages.success(
        request,
        f"La préinscription {numero} a été supprimée avec succès."
    )

    return redirect(
        "gestion:preinscription_liste"
    )
# =========================================================
# ÉTUDIANTS
# =========================================================

@login_required
def etudiants_liste(request):

    etudiants = (
        Etudiant.objects
        .select_related("candidat")
        .filter(actif=True)
        .order_by(
            "candidat__nom",
            "candidat__prenoms"
        )
    )

    recherche = request.GET.get("q", "").strip()

    if recherche:
        etudiants = etudiants.filter(
            Q(matricule__icontains=recherche)
            | Q(candidat__nom__icontains=recherche)
            | Q(candidat__prenoms__icontains=recherche)
            | Q(candidat__telephone__icontains=recherche)
        )

    return render(
        request,
        "gestion/etudiants/liste.html",
        {
            "etudiants": etudiants,
            "recherche": recherche,
        }
    )


@login_required
def etudiant_detail(request, pk):

    etudiant = get_object_or_404(
        Etudiant.objects.select_related("candidat"),
        pk=pk
    )

    inscriptions = (
        etudiant.inscriptions
        .select_related(
            "annee_academique",
            "filiere",
            "niveau",
            "classe",
        )
        .order_by("-date_inscription")
    )

    return render(
        request,
        "gestion/etudiants/detail.html",
        {
            "etudiant": etudiant,
            "inscriptions": inscriptions,
        }
    )


@login_required
def candidat_creer_etudiant(request, pk):

    candidat = get_object_or_404(
        Candidat,
        pk=pk
    )

    # Vérifier si le candidat est déjà étudiant
    if hasattr(candidat, "etudiant"):

        messages.warning(
            request,
            f"Le candidat {candidat.nom} {candidat.prenoms} "
            f"est déjà enregistré comme étudiant."
        )

        return redirect(
            "gestion:etudiant_detail",
            pk=candidat.etudiant.pk
        )

    # Créer l'étudiant
    etudiant = Etudiant.objects.create(
        candidat=candidat
    )

    messages.success(
        request,
        f"L'étudiant {candidat.nom} {candidat.prenoms} "
        f"a été créé avec succès. "
        f"Matricule : {etudiant.matricule}"
    )

    return redirect(
        "gestion:etudiant_detail",
        pk=etudiant.pk
    )
    
# =========================================================
# INSCRIPTIONS
# =========================================================

@login_required
def inscriptions_liste(request):
    inscriptions = (
        Inscription.objects
        .select_related(
            "etudiant__candidat",
            "annee_academique",
            "filiere",
            "niveau",
            "classe",
        )
        .all()
    )

    recherche = request.GET.get("q", "").strip()
    statut = request.GET.get("statut", "").strip()

    if recherche:
        inscriptions = inscriptions.filter(
            Q(numero__icontains=recherche)
            | Q(etudiant__matricule__icontains=recherche)
            | Q(etudiant__candidat__nom__icontains=recherche)
            | Q(etudiant__candidat__prenoms__icontains=recherche)
        )

    if statut:
        inscriptions = inscriptions.filter(statut=statut)

    context = {
        "inscriptions": inscriptions,
        "recherche": recherche,
        "statut_selectionne": statut,
        "statuts": Inscription.STATUT_CHOICES,
    }

    return render(
        request,
        "gestion/inscriptions/liste.html",
        context
    )


@login_required
def inscription_create(request):
    if request.method == "POST":
        form = InscriptionForm(request.POST)

        if form.is_valid():
            inscription = form.save()

            messages.success(
                request,
                f"L'inscription {inscription.numero} a été créée avec succès."
            )

            return redirect(
                "gestion:inscription_detail",
                pk=inscription.pk
            )
    else:
        form = InscriptionForm()

    return render(
        request,
        "gestion/inscriptions/form.html",
        {
            "form": form,
            "titre": "Nouvelle inscription",
            "bouton": "Enregistrer",
        }
    )


@login_required
def inscription_detail(request, pk):
    inscription = get_object_or_404(
        Inscription.objects.select_related(
            "etudiant__candidat",
            "annee_academique",
            "filiere",
            "niveau",
            "classe",
        ),
        pk=pk
    )

    return render(
        request,
        "gestion/inscriptions/detail.html",
        {
            "inscription": inscription
        }
    )


@login_required
def inscription_update(request, pk):
    inscription = get_object_or_404(
        Inscription,
        pk=pk
    )

    if request.method == "POST":
        form = InscriptionForm(
            request.POST,
            instance=inscription
        )

        if form.is_valid():
            inscription = form.save()

            messages.success(
                request,
                f"L'inscription {inscription.numero} a été modifiée avec succès."
            )

            return redirect(
                "gestion:inscription_detail",
                pk=inscription.pk
            )
    else:
        form = InscriptionForm(
            instance=inscription
        )

    return render(
        request,
        "gestion/inscriptions/form.html",
        {
            "form": form,
            "titre": "Modifier l'inscription",
            "bouton": "Enregistrer les modifications",
            "inscription": inscription,
        }
    )

# =========================================================
# SCOLARITÉS
# =========================================================


@login_required
def scolarites_liste(request):

    scolarites = (
        Scolarite.objects
        .select_related(
            "inscription__etudiant__candidat",
            "inscription__annee_academique",
            "inscription__filiere",
            "inscription__niveau",
            "inscription__classe",
        )
        .all()
    )

    recherche = request.GET.get("q", "").strip()
    statut = request.GET.get("statut", "").strip()

    # =====================================================
    # RECHERCHE
    # =====================================================

    if recherche:

        scolarites = scolarites.filter(
            Q(
                inscription__etudiant__matricule__icontains=recherche
            )
            | Q(
                inscription__etudiant__candidat__nom__icontains=recherche
            )
            | Q(
                inscription__etudiant__candidat__prenoms__icontains=recherche
            )
            | Q(
                inscription__numero__icontains=recherche
            )
        )

    # =====================================================
    # FILTRE STATUT
    # =====================================================

    if statut:

        scolarites = scolarites.filter(
            statut=statut
        )

    context = {

        "scolarites": scolarites,

        "recherche": recherche,

        "statut_selectionne": statut,

        "statuts": Scolarite.STATUT_CHOICES,
    }

    return render(
        request,
        "gestion/scolarites/liste.html",
        context
    )


@login_required
def scolarite_create(request):

    if request.method == "POST":

        form = ScolariteForm(
            request.POST
        )

        if form.is_valid():

            scolarite = form.save()

            messages.success(
                request,
                "La scolarité a été créée avec succès."
            )

            return redirect(
                "gestion:scolarite_detail",
                pk=scolarite.pk
            )

    else:

        form = ScolariteForm()

    return render(
        request,
        "gestion/scolarites/form.html",
        {
            "form": form,
            "titre": "Nouvelle scolarité",
            "bouton": "Enregistrer",
        }
    )


@login_required
def scolarite_detail(request, pk):

    scolarite = get_object_or_404(
        Scolarite.objects.select_related(
            "inscription__etudiant__candidat",
            "inscription__annee_academique",
            "inscription__filiere",
            "inscription__niveau",
            "inscription__classe",
        ),
        pk=pk
    )

    echeances = (
        scolarite.echeances
        .order_by("numero")
    )

    paiements = (
        scolarite.paiements
        .select_related("echeance")
        .order_by("-date_paiement")
    )

    return render(
        request,
        "gestion/scolarites/detail.html",
        {
            "scolarite": scolarite,
            "echeances": echeances,
            "paiements": paiements,
        }
    )


@login_required
def scolarite_update(request, pk):

    scolarite = get_object_or_404(
        Scolarite,
        pk=pk
    )

    if request.method == "POST":

        form = ScolariteForm(
            request.POST,
            instance=scolarite
        )

        if form.is_valid():

            scolarite = form.save()

            messages.success(
                request,
                "La scolarité a été modifiée avec succès."
            )

            return redirect(
                "gestion:scolarite_detail",
                pk=scolarite.pk
            )

    else:

        form = ScolariteForm(
            instance=scolarite
        )

    return render(
        request,
        "gestion/scolarites/form.html",
        {
            "form": form,
            "titre": "Modifier la scolarité",
            "bouton": "Enregistrer les modifications",
            "scolarite": scolarite,
        }
    )

# ============================================================
# ÉCHÉANCES
# ============================================================

@login_required
def echeances_liste(request):

    echeances = (
        Echeance.objects
        .select_related(
            "scolarite__inscription__etudiant__candidat",
            "scolarite__inscription__annee_academique",
            "scolarite__inscription__filiere",
            "scolarite__inscription__niveau",
            "scolarite__inscription__classe",
        )
        .all()
    )

    recherche = request.GET.get("q", "").strip()
    statut = request.GET.get("statut", "").strip()

    if recherche:
        echeances = echeances.filter(
            Q(
                scolarite__inscription__etudiant__matricule__icontains=recherche
            )
            | Q(
                scolarite__inscription__etudiant__candidat__nom__icontains=recherche
            )
            | Q(
                scolarite__inscription__etudiant__candidat__prenoms__icontains=recherche
            )
            | Q(
                libelle__icontains=recherche
            )
        )

    if statut:
        echeances = echeances.filter(
            statut=statut
        )

    context = {
        "echeances": echeances,
        "recherche": recherche,
        "statut_selectionne": statut,
        "statuts": Echeance.STATUT_CHOICES,
    }

    return render(
        request,
        "gestion/echeances/liste.html",
        context
    )


@login_required
def echeance_create(request):

    if request.method == "POST":

        form = EcheanceForm(request.POST)

        if form.is_valid():

            echeance = form.save()

            messages.success(
                request,
                "L'échéance a été créée avec succès."
            )

            return redirect(
                "gestion:echeance_detail",
                pk=echeance.pk
            )

    else:

        form = EcheanceForm()

    return render(
        request,
        "gestion/echeances/form.html",
        {
            "form": form,
            "titre": "Nouvelle échéance",
            "bouton": "Enregistrer",
        }
    )


@login_required
def echeance_detail(request, pk):

    echeance = get_object_or_404(
        Echeance.objects.select_related(
            "scolarite__inscription__etudiant__candidat",
            "scolarite__inscription__annee_academique",
            "scolarite__inscription__filiere",
            "scolarite__inscription__niveau",
            "scolarite__inscription__classe",
        ),
        pk=pk
    )

    paiements = (
        echeance.paiements
        .filter(statut="VALIDE")
        .order_by("-date_paiement")
    )

    return render(
        request,
        "gestion/echeances/detail.html",
        {
            "echeance": echeance,
            "paiements": paiements,
        }
    )


@login_required
def echeance_update(request, pk):

    echeance = get_object_or_404(
        Echeance,
        pk=pk
    )

    if request.method == "POST":

        form = EcheanceForm(
            request.POST,
            instance=echeance
        )

        if form.is_valid():

            echeance = form.save()

            messages.success(
                request,
                "L'échéance a été modifiée avec succès."
            )

            return redirect(
                "gestion:echeance_detail",
                pk=echeance.pk
            )

    else:

        form = EcheanceForm(
            instance=echeance
        )

    return render(
        request,
        "gestion/echeances/form.html",
        {
            "form": form,
            "titre": "Modifier l'échéance",
            "bouton": "Enregistrer les modifications",
            "echeance": echeance,
        }
    )

# ============================================================
# PAIEMENTS
# ============================================================

@login_required
def paiements_liste(request):

    paiements = (
        Paiement.objects
        .select_related(
            "scolarite__inscription__etudiant__candidat",
            "scolarite__inscription__annee_academique",
            "echeance",
        )
        .all()
    )

    recherche = request.GET.get("q", "").strip()
    statut = request.GET.get("statut", "").strip()

    if recherche:

        paiements = paiements.filter(
            Q(reference__icontains=recherche)
            | Q(
                scolarite__inscription__etudiant__matricule__icontains=recherche
            )
            | Q(
                scolarite__inscription__etudiant__candidat__nom__icontains=recherche
            )
            | Q(
                scolarite__inscription__etudiant__candidat__prenoms__icontains=recherche
            )
        )

    if statut:
        paiements = paiements.filter(statut=statut)

    context = {
        "paiements": paiements,
        "recherche": recherche,
        "statut_selectionne": statut,
        "statuts": Paiement.STATUT_CHOICES,
    }

    return render(
        request,
        "gestion/paiements/liste.html",
        context
    )


@login_required
def paiement_create(request):

    if request.method == "POST":

        form = PaiementForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                paiement = form.save()

                # Mise à jour de l'échéance
                if paiement.echeance:

                    paiement.echeance.save()

                # Mise à jour de la scolarité
                paiement.scolarite.save()

                # Créer automatiquement le reçu
                if paiement.statut == "VALIDE":

                    Recu.objects.get_or_create(
                        paiement=paiement
                    )

            messages.success(
                request,
                f"Le paiement {paiement.reference} "
                f"a été enregistré avec succès."
            )

            return redirect(
                "gestion:paiement_detail",
                pk=paiement.pk
            )

    else:

        form = PaiementForm()

    return render(
        request,
        "gestion/paiements/form.html",
        {
            "form": form,
            "titre": "Nouveau paiement",
            "bouton": "Enregistrer le paiement",
        }
    )


@login_required
def paiement_detail(request, pk):

    paiement = get_object_or_404(
        Paiement.objects.select_related(
            "scolarite__inscription__etudiant__candidat",
            "scolarite__inscription__annee_academique",
            "scolarite__inscription__filiere",
            "scolarite__inscription__niveau",
            "scolarite__inscription__classe",
            "echeance",
        ),
        pk=pk
    )

    recu = getattr(
        paiement,
        "recu",
        None
    )

    return render(
        request,
        "gestion/paiements/detail.html",
        {
            "paiement": paiement,
            "recu": recu,
        }
    )


@login_required
def paiement_update(request, pk):

    paiement = get_object_or_404(
        Paiement,
        pk=pk
    )

    if request.method == "POST":

        form = PaiementForm(
            request.POST,
            instance=paiement
        )

        if form.is_valid():

            with transaction.atomic():

                paiement = form.save()

                if paiement.echeance:
                    paiement.echeance.save()

                paiement.scolarite.save()

                if paiement.statut == "VALIDE":

                    Recu.objects.get_or_create(
                        paiement=paiement
                    )

                else:

                    Recu.objects.filter(
                        paiement=paiement
                    ).delete()

            messages.success(
                request,
                f"Le paiement {paiement.reference} "
                f"a été modifié avec succès."
            )

            return redirect(
                "gestion:paiement_detail",
                pk=paiement.pk
            )

    else:

        form = PaiementForm(
            instance=paiement
        )

    return render(
        request,
        "gestion/paiements/form.html",
        {
            "form": form,
            "titre": "Modifier le paiement",
            "bouton": "Enregistrer les modifications",
            "paiement": paiement,
        }
    )

# =========================================================
# REÇUS
# =========================================================

# ============================================================
# MONTANT EN LETTRES
# ============================================================

def nombre_en_lettres(nombre):
    """
    Convertit un nombre entier en lettres françaises.
    """

    unites = [
        "zéro",
        "un",
        "deux",
        "trois",
        "quatre",
        "cinq",
        "six",
        "sept",
        "huit",
        "neuf",
        "dix",
        "onze",
        "douze",
        "treize",
        "quatorze",
        "quinze",
        "seize",
        "dix-sept",
        "dix-huit",
        "dix-neuf",
    ]

    dizaines = [
        "",
        "",
        "vingt",
        "trente",
        "quarante",
        "cinquante",
        "soixante",
        "soixante",
        "quatre-vingt",
        "quatre-vingt",
    ]

    def moins_de_100(n):

        if n < 20:
            return unites[n]

        dizaine = n // 10
        unite = n % 10

        if dizaine == 7:
            if unite == 0:
                return "soixante-dix"
            return "soixante-" + unites[10 + unite]

        if dizaine == 9:
            if unite == 0:
                return "quatre-vingt-dix"
            return "quatre-vingt-" + unites[10 + unite]

        texte = dizaines[dizaine]

        if unite == 0:
            return texte

        if unite == 1 and dizaine in [2, 3, 4, 5, 6]:
            return texte + "-et-un"

        return texte + "-" + unites[unite]

    def moins_de_1000(n):

        if n < 100:
            return moins_de_100(n)

        centaine = n // 100
        reste = n % 100

        if centaine == 1:
            texte = "cent"
        else:
            texte = unites[centaine] + " cent"

        if reste == 0:
            if centaine > 1:
                texte += "s"
            return texte

        return texte + " " + moins_de_100(reste)

    def convertir(n):

        if n < 1000:
            return moins_de_1000(n)

        millions = n // 1_000_000
        reste = n % 1_000_000

        if millions:
            if millions == 1:
                texte = "un million"
            else:
                texte = convertir(millions) + " millions"

            if reste:
                texte += " " + convertir(reste)

            return texte

        milliers = n // 1000
        reste = n % 1000

        if milliers == 1:
            texte = "mille"
        else:
            texte = convertir(milliers) + " mille"

        if reste:
            texte += " " + convertir(reste)

        return texte

    try:
        nombre = int(Decimal(str(nombre)))
    except (ValueError, TypeError):
        return ""

    if nombre == 0:
        return "zéro"

    return convertir(nombre)



@login_required
def recus_liste(request):

    recus = (
        Recu.objects
        .select_related(
            "paiement",
            "paiement__scolarite__inscription__etudiant__candidat",
            "paiement__scolarite__inscription__annee_academique",
            "paiement__scolarite__inscription__filiere",
            "paiement__scolarite__inscription__niveau",
            "paiement__scolarite__inscription__classe",
            "paiement__echeance",
        )
        .order_by("-date_emission")
    )

    recherche = request.GET.get("q", "").strip()

    if recherche:
        recus = recus.filter(
            Q(numero__icontains=recherche)
            | Q(paiement__reference__icontains=recherche)
            | Q(
                paiement__scolarite__inscription__etudiant__matricule__icontains=recherche
            )
            | Q(
                paiement__scolarite__inscription__etudiant__candidat__nom__icontains=recherche
            )
            | Q(
                paiement__scolarite__inscription__etudiant__candidat__prenoms__icontains=recherche
            )
        )

    return render(
        request,
        "gestion/recus/liste.html",
        {
            "recus": recus,
            "recherche": recherche,
        }
    )


@login_required
def recu_detail(request, pk):

    recu = get_object_or_404(
        Recu.objects.select_related(
            "paiement",
            "paiement__scolarite__inscription__etudiant__candidat",
            "paiement__scolarite__inscription__annee_academique",
            "paiement__scolarite__inscription__filiere",
            "paiement__scolarite__inscription__niveau",
            "paiement__scolarite__inscription__classe",
            "paiement__echeance",
        ),
        pk=pk
    )

    return render(
        request,
        "gestion/recus/detail.html",
        {
            "recu": recu,
        }
    )

# ============================================================
# PDF DU REÇU UIC
# ============================================================

@login_required
def recu_pdf(request, pk):

    # ============================================================
    # IMPORTS
    # ============================================================

    import io
    import qrcode

    from pathlib import Path
    from decimal import Decimal

    from django.conf import settings
    from django.db.models import Sum
    from django.http import HttpResponse
    from django.shortcuts import get_object_or_404

    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib.utils import ImageReader

    # ============================================================
    # RÉCUPÉRATION DU REÇU
    # ============================================================

    recu = get_object_or_404(
        Recu.objects.select_related(
            "paiement",
            "paiement__scolarite__inscription__etudiant__candidat",
            "paiement__scolarite__inscription__annee_academique",
            "paiement__scolarite__inscription__filiere",
            "paiement__scolarite__inscription__niveau",
            "paiement__scolarite__inscription__classe",
            "paiement__echeance",
        ),
        pk=pk,
    )

    paiement = recu.paiement
    scolarite = paiement.scolarite
    inscription = scolarite.inscription
    etudiant = inscription.etudiant
    candidat = etudiant.candidat

    # ============================================================
    # INFORMATIONS ÉTUDIANT
    # ============================================================

    nom_complet = f"{candidat.nom} {candidat.prenoms}".upper()
    annee_academique = inscription.annee_academique.libelle
    matricule = etudiant.matricule
    filiere = inscription.filiere.nom
    classe = inscription.classe.nom
    niveau = inscription.niveau.nom

    # ============================================================
    # MONTANTS
    # ============================================================

    montant_total = Decimal(scolarite.montant_total or 0)
    remise = Decimal(scolarite.remise or 0)
    scolarite_nette = Decimal(scolarite.montant_net or 0)

    total_paye = Decimal(
        scolarite.paiements.filter(statut="VALIDE").aggregate(
            total=Sum("montant")
        )["total"] or 0
    )

    reste_a_payer = max(Decimal("0.00"), scolarite_nette - total_paye)

    montant = Decimal(paiement.montant or 0)
    montant_lettres = nombre_en_lettres(montant)

    # ============================================================
    # FORMATAGE DES MONTANTS (convention française : espace pour les
    # milliers, virgule pour les décimales)
    # ============================================================

    def montant_fmt(valeur):
        texte = f"{valeur:,.2f}"
        texte = texte.replace(",", " ").replace(".", ",")
        return f"{texte} FCFA"

    # ============================================================
    # DÉSIGNATION DU PAIEMENT
    # ============================================================

    designation = "Versement"
    if paiement.echeance:
        designation = paiement.echeance.libelle or "Versement"

    designation_lower = designation.lower()

    droit_inscription = Decimal("0.00")
    versement = Decimal("0.00")
    autres = Decimal("0.00")

    if "droit" in designation_lower or "inscription" in designation_lower:
        droit_inscription = montant
    elif "autre" in designation_lower or "divers" in designation_lower:
        autres = montant
    else:
        versement = montant

    mode = paiement.mode_paiement

    # ============================================================
    # DOCUMENT PDF
    # ============================================================

    buffer = io.BytesIO()
    largeur, hauteur = A4

    marge_gauche = 1 * cm
    marge_droite = 1 * cm

    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(f"Reçu {recu.numero}")

    # ============================================================
    # COULEURS
    # ============================================================

    bleu_uic = colors.HexColor("#243F73")
    gris = colors.HexColor("#555555")
    bleu_clair = colors.HexColor("#EAF0FA")
    rouge_clair = colors.HexColor("#FBEAEC")
    gris_bordure = colors.HexColor("#D0D4DA")

    # ============================================================
    # CADRE EXTÉRIEUR
    # ============================================================

    pdf.setStrokeColor(bleu_uic)
    pdf.setLineWidth(1)
    pdf.rect(
        0.65 * cm, 0.65 * cm,
        largeur - 1.30 * cm, hauteur - 1.30 * cm,
        stroke=1, fill=0,
    )

    # ============================================================
    # LOGO
    # ============================================================

    logo = (
        Path(settings.BASE_DIR)
        / "gestion" / "static" / "gestion" / "images" / "logo.jpeg"
    )

    if logo.exists():
        pdf.drawImage(
            str(logo),
            1.15 * cm, hauteur - 3.35 * cm,
            width=4.6 * cm, height=2.35 * cm,
            preserveAspectRatio=True,
            mask="auto",
        )

    # ============================================================
    # TITRE
    # ============================================================

    pdf.setFillColor(bleu_uic)
    pdf.setFont("Helvetica-Bold", 17)
    pdf.drawCentredString(largeur / 2, hauteur - 1.55 * cm, "REÇU")

    pdf.setStrokeColor(bleu_uic)
    pdf.setLineWidth(1)
    pdf.line(8.1 * cm, hauteur - 1.72 * cm, 12.9 * cm, hauteur - 1.72 * cm)

    # ============================================================
    # NUMÉRO DU REÇU
    # ============================================================

    numero_affichage = str(recu.numero)
    if "-" in numero_affichage:
        numero_affichage = numero_affichage.split("-")[-1]

    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.drawString(12.55 * cm, hauteur - 1.48 * cm, "REÇU N°")

    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(13.65 * cm, hauteur - 1.48 * cm, str(numero_affichage).zfill(6))

    # ============================================================
    # DATE
    # ============================================================

    pdf.setFont("Helvetica", 8.5)
    pdf.drawString(13.15 * cm, hauteur - 2.30 * cm, "Date :")

    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.drawString(
        14.35 * cm, hauteur - 2.30 * cm,
        recu.date_emission.strftime("%d/%m/%Y"),
    )

    # ============================================================
    # QR CODE
    # ============================================================

    qr_data = f"""
UNIVERSITÉ INTERNATIONALE DE COCODY
================================

REÇU N° : {str(numero_affichage).zfill(6)}
Date : {recu.date_emission.strftime("%d/%m/%Y")}

Étudiant : {nom_complet}
Matricule : {matricule}

Filière : {filiere}
Niveau : {niveau}
Classe : {classe}

Année académique : {annee_academique}

================================

Montant total : {montant_fmt(montant_total)}
Remise : {montant_fmt(remise)}
Scolarité nette : {montant_fmt(scolarite_nette)}

Total payé : {montant_fmt(total_paye)}
Reste à payer : {montant_fmt(reste_a_payer)}

================================

Paiement de ce reçu : {montant_fmt(montant)}
Montant en lettres : {montant_lettres} FCFA

Mode : {paiement.get_mode_paiement_display()}
Référence : {paiement.reference}
""".strip()

    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color="black", back_color="white")
    qr_buffer = io.BytesIO()
    qr_image.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_reader = ImageReader(qr_buffer)

    qr_size = 1.90 * cm
    qr_x = largeur - marge_droite - qr_size
    qr_y = hauteur - 3.25 * cm

    pdf.drawImage(
        qr_reader, qr_x, qr_y,
        width=qr_size, height=qr_size,
        preserveAspectRatio=True, mask="auto",
    )
    qr_buffer.close()

    # légende sous le QR code, pour que sa fonction soit explicite
    pdf.setFillColor(gris)
    pdf.setFont("Helvetica", 5.5)
    pdf.drawCentredString(qr_x + qr_size / 2, qr_y - 0.28 * cm, "Scanner pour vérifier")

    # ============================================================
    # FONCTION LIGNE POINTILLÉE
    # ============================================================

    def ligne_pointillee(x1, x2, y, couleur=gris):
        pdf.setStrokeColor(couleur)
        pdf.setLineWidth(0.5)
        pdf.setDash(1, 2)
        pdf.line(x1, y, x2, y)
        pdf.setDash()

    # ============================================================
    # INFORMATIONS ÉTUDIANT
    # ============================================================

    y = hauteur - 4.05 * cm
    pdf.setFillColor(colors.black)

    # -- Nom --
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(1 * cm, y, "Nom & Prénoms :")
    ligne_pointillee(6.15 * cm, largeur - marge_droite, y - 0.05 * cm)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(6.2 * cm, y, nom_complet[:65])

    # -- Année + Matricule --
    y -= 0.85 * cm
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(1 * cm, y, "Année académique :")
    ligne_pointillee(4.25 * cm, 11.7 * cm, y - 0.05 * cm)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(4.3 * cm, y, str(annee_academique))

    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(12 * cm, y, "Matricule :")
    ligne_pointillee(15 * cm, largeur - marge_droite, y - 0.05 * cm)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(15.05 * cm, y, str(matricule))

    # -- Filière + N° Carnet --
    y -= 0.85 * cm
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(1 * cm, y, "Filière :")
    ligne_pointillee(2.55 * cm, 14 * cm, y - 0.05 * cm)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(2.6 * cm, y, str(filiere).upper()[:55])

    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(14.2 * cm, y, "N° Carnet :")
    ligne_pointillee(16.7 * cm, largeur - marge_droite, y - 0.05 * cm)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(16.75 * cm, y, "—")

    # ============================================================
    # TABLEAU DES MONTANTS
    # ============================================================

    table_x = marge_gauche
    table_top = y - 0.85 * cm
    table_width = largeur - marge_gauche - marge_droite
    col1 = 10 * cm
    col2 = table_width - col1
    header_height = 0.68 * cm
    row_height = 0.64 * cm

    lignes = [
        ("Montant total", montant_total),
        ("Remise", remise),
        ("Scolarité nette", scolarite_nette),
        ("Droit d'inscription", droit_inscription),
        ("Versement", versement),
        ("Autres : divers, etc...", autres),
        ("TOTAL PAYÉ", total_paye),
        ("RESTE À PAYER", reste_a_payer),
    ]

    total_height = header_height + len(lignes) * row_height
    table_bottom = table_top - total_height

    # -- Fond du tableau --
    pdf.setFillColor(colors.white)
    pdf.setStrokeColor(bleu_uic)
    pdf.setLineWidth(0.8)
    pdf.rect(table_x, table_bottom, table_width, total_height, stroke=1, fill=1)

    # -- En-tête --
    pdf.setFillColor(bleu_uic)
    pdf.rect(table_x, table_top - header_height, table_width, header_height, stroke=0, fill=1)

    pdf.setFillColor(colors.white)
    pdf.setFont("Helvetica-Bold", 8.5)
    pdf.drawString(table_x + 0.25 * cm, table_top - 0.44 * cm, "DÉSIGNATION")
    pdf.drawRightString(table_x + col1 + col2 - 0.25 * cm, table_top - 0.44 * cm, "MONTANT")

    # -- Lignes --
    current_top = table_top - header_height

    for libelle, valeur in lignes:
        row_bottom = current_top - row_height

        if libelle == "TOTAL PAYÉ":
            pdf.setFillColor(bleu_clair)
            pdf.rect(table_x, row_bottom, table_width, row_height, stroke=0, fill=1)
        elif libelle == "RESTE À PAYER":
            pdf.setFillColor(rouge_clair)
            pdf.rect(table_x, row_bottom, table_width, row_height, stroke=0, fill=1)

        pdf.setStrokeColor(gris_bordure)
        pdf.setLineWidth(0.5)
        pdf.line(table_x, row_bottom, table_x + table_width, row_bottom)
        pdf.line(table_x + col1, row_bottom, table_x + col1, current_top)

        if libelle in ("TOTAL PAYÉ", "RESTE À PAYER"):
            pdf.setFont("Helvetica-Bold", 8.5)
        elif libelle == "Remise":
            pdf.setFont("Helvetica-Bold", 8)
        else:
            pdf.setFont("Helvetica", 8)

        pdf.setFillColor(colors.black)
        pdf.drawString(table_x + 0.25 * cm, row_bottom + 0.20 * cm, libelle)
        pdf.drawRightString(
            table_x + table_width - 0.25 * cm,
            row_bottom + 0.20 * cm,
            montant_fmt(valeur),
        )

        current_top = row_bottom

    # ============================================================
    # MONTANT EN LETTRES
    # ============================================================

    y_montant = table_bottom - 0.75 * cm

    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(1 * cm, y_montant, "Montant du présent paiement :")

    pdf.setFont("Helvetica", 8)
    pdf.drawString(6.1 * cm, y_montant, f"{montant_lettres} FCFA"[:100])

    # ============================================================
    # MODE DE PAIEMENT
    # ============================================================

    y_mode = y_montant - 0.85 * cm

    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(1 * cm, y_mode, "Mode de paiement :")

    modes = [
        ("ESPECES", "Espèces"),
        ("CHEQUE", "Chèque"),
        ("VIREMENT", "Virement"),
        ("MOBILE_MONEY", "Mobile Money"),
        ("CARTE", "Carte bancaire"),
        ("AUTRE", "Autre"),
    ]

    x_mode = 4.6 * cm
    pdf.setFont("Helvetica", 7.5)

    for code, libelle in modes:
        pdf.setStrokeColor(gris)
        pdf.setLineWidth(0.6)
        pdf.setFillColor(bleu_uic if mode == code else colors.white)
        pdf.rect(x_mode, y_mode - 0.07 * cm, 0.32 * cm, 0.32 * cm, stroke=1, fill=1)

        if mode == code:
            pdf.setFillColor(colors.white)
            pdf.setFont("Helvetica-Bold", 7)
            pdf.drawString(x_mode + 0.055 * cm, y_mode - 0.01 * cm, "✓")

        pdf.setFillColor(colors.black)
        pdf.setFont("Helvetica", 7.5)
        pdf.drawString(x_mode + 0.42 * cm, y_mode, libelle)

        x_mode += 2.35 * cm

    # ============================================================
    # RÉFÉRENCE PAIEMENT
    # ============================================================

    y_reference = y_mode - 0.85 * cm

    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(1 * cm, y_reference, "Référence paiement :")
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(4.6 * cm, y_reference, paiement.reference)

    # ============================================================
    # NIVEAU / CLASSE
    # ============================================================

    y_classe = y_reference - 0.85 * cm

    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(1 * cm, y_classe, "Niveau :")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(2.25 * cm, y_classe, str(niveau))

    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawString(8.2 * cm, y_classe, "Classe :")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(9.6 * cm, y_classe, str(classe))

    # ============================================================
    # SIGNATURES
    # ============================================================

    y_signature = y_classe - 1.6 * cm

    pdf.setFillColor(colors.black)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(5 * cm, y_signature, "L'ÉTUDIANT")
    pdf.drawCentredString(16 * cm, y_signature, "LA CAISSE")

    ligne_signature_y = y_signature - 1.3 * cm

    pdf.setStrokeColor(colors.HexColor("#999999"))
    pdf.setLineWidth(0.5)
    pdf.line(2.3 * cm, ligne_signature_y, 7.7 * cm, ligne_signature_y)
    pdf.line(13.3 * cm, ligne_signature_y, 18.7 * cm, ligne_signature_y)

    # -- Emplacement cachet (au-dessus de la ligne "LA CAISSE") --
    cachet_rayon = 1.05 * cm
    cachet_cx = 16 * cm
    cachet_cy = ligne_signature_y + 0.35 * cm + cachet_rayon

    pdf.setStrokeColor(gris_bordure)
    pdf.setLineWidth(0.6)
    pdf.setDash(2, 2)
    pdf.circle(cachet_cx, cachet_cy, cachet_rayon, stroke=1, fill=0)
    pdf.setDash()

    pdf.setFillColor(gris)
    pdf.setFont("Helvetica-Oblique", 6.5)
    pdf.drawCentredString(cachet_cx, cachet_cy - 0.1 * cm, "Cachet")

    # ============================================================
    # NOTE
    # ============================================================

    y_note = ligne_signature_y - 1.05 * cm

    pdf.setFillColor(gris)
    pdf.setFont("Helvetica-Oblique", 7)
    pdf.drawCentredString(largeur / 2, y_note, "Ce reçu constitue une preuve de paiement.")
    pdf.drawCentredString(largeur / 2, y_note - 0.32 * cm, "Veuillez conserver ce document.")
    pdf.drawCentredString(
        largeur / 2, y_note - 0.64 * cm,
        "En cas d'erreur, contactez le service de la scolarité sous 48h.",
    )

    # ============================================================
    # PIED DE PAGE
    # ============================================================

    pdf.setStrokeColor(gris_bordure)
    pdf.setLineWidth(0.5)
    pdf.line(marge_gauche + 0.4 * cm, 1.35 * cm, largeur - marge_droite - 0.4 * cm, 1.35 * cm)

    pdf.setFillColor(bleu_uic)
    pdf.setFont("Helvetica-Bold", 7)
    pdf.drawCentredString(largeur / 2, 1.05 * cm, "UNIVERSITÉ INTERNATIONALE DE COCODY")

    pdf.setFont("Helvetica", 6.5)
    pdf.setFillColor(gris)
    pdf.drawCentredString(
        largeur / 2, 0.78 * cm,
        "Document généré automatiquement par le système de gestion.",
    )

    # ============================================================
    # FINALISATION
    # ============================================================

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="recu_{numero_affichage}.pdf"'

    return response

@login_required
def fiche_inscription_pdf(request, pk):

    # ============================================================
    # IMPORTS
    # ============================================================

    import io
    import os
    from datetime import datetime

    from django.shortcuts import get_object_or_404
    from django.http import FileResponse

    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader

    # ============================================================
    # RÉCUPÉRATION DE L'INSCRIPTION
    # ============================================================

    inscription = get_object_or_404(
        Inscription.objects.select_related(
            "etudiant",
            "etudiant__candidat",
            "annee_academique",
            "filiere",
            "niveau",
            "classe",
        ),
        pk=pk,
    )

    candidat = inscription.etudiant.candidat

    # ============================================================
    # PDF
    # ============================================================

    buffer = io.BytesIO()

    largeur, hauteur = A4

    marge_gauche = 1.5 * cm
    marge_droite = 1.5 * cm
    marge_haut = 1.2 * cm
    marge_bas = 1.2 * cm

    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle(f"Fiche d'inscription - {inscription.numero}")

    # ============================================================
    # COULEURS
    # ============================================================

    bleu = colors.HexColor("#0d6efd")
    bleu_fonce = colors.HexColor("#12355B")
    gris = colors.HexColor("#6c757d")
    gris_clair = colors.HexColor("#f5f7fa")
    gris_bordure = colors.HexColor("#d9dee5")
    noir = colors.HexColor("#212529")
    blanc = colors.white

    # ============================================================
    # CADRE GLOBAL
    # ============================================================

    pdf.setStrokeColor(gris_bordure)
    pdf.setLineWidth(0.8)
    pdf.roundRect(
        marge_gauche,
        marge_bas,
        largeur - marge_gauche - marge_droite,
        hauteur - marge_haut - marge_bas,
        8,
        stroke=1,
        fill=0,
    )

    # ============================================================
    # EN-TÊTE (fond blanc, logo à gauche)
    # ============================================================

    entete_h = 2.6 * cm
    entete_y = hauteur - marge_haut - entete_h  # bas de la zone d'en-tête

    # -- Logo (à gauche) --
    logo_taille = 2.0 * cm
    logo_x = marge_gauche + 0.4 * cm
    logo_y = entete_y + (entete_h - logo_taille) / 2

    from django.conf import settings
    from django.contrib.staticfiles import finders

    # cherche d'abord via les staticfiles Django (fonctionne quel que soit
    # l'environnement), puis en repli le chemin relatif au projet
    LOGO_PATH = finders.find("gestion/images/logo.jpeg")
    if not LOGO_PATH:
        LOGO_PATH = os.path.join(settings.BASE_DIR, "gestion", "static", "gestion", "images", "logo.jpeg")

    logo_affiche = False
    if os.path.exists(LOGO_PATH):
        try:
            pdf.drawImage(
                ImageReader(LOGO_PATH),
                logo_x, logo_y,
                width=logo_taille, height=logo_taille,
                preserveAspectRatio=True,
                anchor="c",
                mask="auto",
            )
            logo_affiche = True
        except Exception:
            logo_affiche = False

    if not logo_affiche:
        pdf.setFillColor(gris_clair)
        pdf.setStrokeColor(gris_bordure)
        pdf.setLineWidth(0.8)
        pdf.roundRect(logo_x, logo_y, logo_taille, logo_taille, 4, stroke=1, fill=1)
        pdf.setFillColor(gris)
        pdf.setFont("Helvetica-Bold", 7)
        pdf.drawCentredString(logo_x + logo_taille / 2, logo_y + logo_taille / 2 - 0.1 * cm, "LOGO")

    # -- Texte de l'en-tête (centré sur la page) --
    cursor = hauteur - marge_haut - 0.75 * cm

    pdf.setFillColor(bleu_fonce)
    pdf.setFont("Helvetica-Bold", 15)
    pdf.drawCentredString(largeur / 2, cursor, "UNIVERSITÉ INTERNATIONALE DE COCODY")

    cursor -= 0.5 * cm
    pdf.setFillColor(gris)
    pdf.setFont("Helvetica", 8.5)
    pdf.drawCentredString(largeur / 2, cursor, "Service des Inscriptions et de la Scolarité")

    cursor -= 0.65 * cm
    pdf.setFillColor(bleu)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawCentredString(largeur / 2, cursor, "FICHE D'INSCRIPTION")

    # ============================================================
    # LIGNE SOUS L'EN-TÊTE
    # ============================================================

    cursor = entete_y - 0.4 * cm
    pdf.setStrokeColor(gris_bordure)
    pdf.setLineWidth(0.8)
    pdf.line(marge_gauche + 0.4 * cm, cursor, largeur - marge_droite - 0.4 * cm, cursor)

    cursor -= 0.5 * cm

    # ============================================================
    # RANGÉE INFOS RAPIDES : date d'édition (gauche) / N° inscription (droite)
    # ============================================================

    ligne_h = 0.95 * cm

    # -- N° inscription (droite) — libellé et valeur empilés pour
    #    ne jamais se chevaucher, quelle que soit la longueur du numéro --
    box_w = 5.4 * cm
    box_h = ligne_h
    box_x = largeur - marge_droite - 0.4 * cm - box_w
    box_y = cursor - box_h

    numero_texte = str(inscription.numero)
    taille_numero = 10
    # réduit automatiquement la taille si le numéro est très long
    while pdf.stringWidth(numero_texte, "Helvetica-Bold", taille_numero) > box_w - 0.55 * cm and taille_numero > 7:
        taille_numero -= 0.5

    pdf.setFillColor(gris_clair)
    pdf.setStrokeColor(gris_bordure)
    pdf.setLineWidth(0.8)
    pdf.roundRect(box_x, box_y, box_w, box_h, 5, stroke=1, fill=1)
    pdf.setFillColor(bleu)
    pdf.rect(box_x, box_y, 0.15 * cm, box_h, stroke=0, fill=1)

    pdf.setFillColor(gris)
    pdf.setFont("Helvetica-Bold", 7)
    pdf.drawString(box_x + 0.35 * cm, box_y + box_h - 0.34 * cm, "N° INSCRIPTION")
    pdf.setFillColor(noir)
    pdf.setFont("Helvetica-Bold", taille_numero)
    pdf.drawString(box_x + 0.35 * cm, box_y + 0.28 * cm, numero_texte)

    # -- Date d'édition (gauche) --
    date_edition = datetime.now().strftime("%d/%m/%Y à %H:%M")
    edit_x = marge_gauche + 0.4 * cm

    pdf.setFillColor(gris)
    pdf.setFont("Helvetica", 8)
    # pdf.drawString(edit_x, box_y + box_h / 2 - 0.12 * cm, f"Document édité le {date_edition}")

    # bas réel de cette rangée
    cursor = box_y

    # ============================================================
    # FONCTION CHAMP — renvoie le bas réel du champ
    # ============================================================

    def champ(label, valeur, x, y, largeur_champ=6.2 * cm, taille=9):
        if valeur is None or valeur == "":
            valeur = "Non renseigné"
        valeur = str(valeur)

        pdf.setFillColor(gris)
        pdf.setFont("Helvetica-Bold", 6.8)
        pdf.drawString(x, y, label.upper())

        pdf.setFillColor(noir)
        pdf.setFont("Helvetica", taille)
        pdf.drawString(x, y - 0.38 * cm, valeur[:60])

        pdf.setStrokeColor(gris_bordure)
        pdf.setLineWidth(0.4)
        pdf.line(x, y - 0.52 * cm, x + largeur_champ, y - 0.52 * cm)

        return y - 0.52 * cm

    # ============================================================
    # CONSTANTES DE MISE EN PAGE
    # ============================================================

    TITLE_TO_FIELDS = 0.75 * cm
    ROW_H_1COL = 1.0 * cm
    ROW_H_2COL = 1.05 * cm
    SECTION_GAP = 0.65 * cm

    def titre_section(x, y, numero, texte, largeur_ligne):
        # petit badge numéroté pour un rendu plus soigné
        rayon = 0.32 * cm
        pdf.setFillColor(bleu)
        pdf.circle(x + rayon, y + 0.12 * cm, rayon, stroke=0, fill=1)
        pdf.setFillColor(blanc)
        pdf.setFont("Helvetica-Bold", 8.5)
        pdf.drawCentredString(x + rayon, y - 0.06 * cm, str(numero))

        pdf.setFillColor(bleu_fonce)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(x + 2 * rayon + 0.25 * cm, y, texte)

        pdf.setStrokeColor(bleu)
        pdf.setLineWidth(0.8)
        pdf.line(x, y - 0.28 * cm, x + largeur_ligne, y - 0.28 * cm)

    # ============================================================
    # ZONE DE CONTENU : la photo démarre désormais à la même hauteur
    # que le titre de la section 1, nettement sous la rangée du
    # numéro d'inscription — plus aucun chevauchement possible.
    # ============================================================

    cursor -= SECTION_GAP
    content_top = cursor

    section_x = marge_gauche + 0.4 * cm
    section_width = largeur - marge_gauche - marge_droite - 0.8 * cm

    # ============================================================
    # PHOTO
    # ============================================================

    photo_w = 3.2 * cm
    photo_h = 3.8 * cm
    photo_x = largeur - marge_droite - photo_w - 0.2 * cm
    # le haut de la photo démarre sous la ligne de séparation du titre de
    # section (tracée à content_top - 0.28cm), avec une marge de sécurité
    photo_y = content_top - 0.55 * cm - photo_h

    pdf.setStrokeColor(gris_bordure)
    pdf.setLineWidth(0.8)

    photo_affichee = False
    if getattr(candidat, "photo", None):
        try:
            photo_path = candidat.photo.path
            if os.path.exists(photo_path):
                pdf.drawImage(
                    ImageReader(photo_path),
                    photo_x, photo_y,
                    width=photo_w, height=photo_h,
                    preserveAspectRatio=True,
                    anchor="c",
                    mask="auto",
                )
                pdf.rect(photo_x, photo_y, photo_w, photo_h, fill=0, stroke=1)
                photo_affichee = True
        except Exception:
            photo_affichee = False

    if not photo_affichee:
        pdf.setFillColor(gris_clair)
        pdf.rect(photo_x, photo_y, photo_w, photo_h, fill=1, stroke=1)
        pdf.setFillColor(gris)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawCentredString(photo_x + photo_w / 2, photo_y + photo_h / 2, "PHOTO")

    # ============================================================
    # 1. IDENTIFICATION
    # ============================================================

    titre_section(section_x, content_top, 1, "IDENTIFICATION DE L'ÉTUDIANT", section_width)

    info_x = section_x
    info_y = content_top - TITLE_TO_FIELDS
    largeur_info = 6.3 * cm

    bas1 = champ("Matricule", inscription.etudiant.matricule, info_x, info_y, largeur_info)
    bas2 = champ("Nom", candidat.nom, info_x, info_y - ROW_H_1COL, largeur_info)
    bas3 = champ("Prénoms", candidat.prenoms, info_x, info_y - 2 * ROW_H_1COL, largeur_info)
    bas4 = champ("Sexe", getattr(candidat, "sexe", None), info_x, info_y - 3 * ROW_H_1COL, largeur_info)

    fin_section1 = min(bas4, photo_y)

    # ============================================================
    # 2. INFORMATIONS PERSONNELLES
    # ============================================================

    section_y = fin_section1 - SECTION_GAP
    titre_section(section_x, section_y, 2, "INFORMATIONS PERSONNELLES", section_width)

    col1 = section_x
    col2 = section_x + 8.3 * cm
    info_y = section_y - TITLE_TO_FIELDS

    date_naissance = getattr(candidat, "date_naissance", None)
    if date_naissance:
        date_naissance = date_naissance.strftime("%d/%m/%Y")

    champ("Date de naissance", date_naissance, col1, info_y, 6.5 * cm)
    champ("Lieu de naissance", getattr(candidat, "lieu_naissance", None), col2, info_y, 6.5 * cm)

    champ("Nationalité", getattr(candidat, "nationalite", None), col1, info_y - ROW_H_2COL, 6.5 * cm)
    champ("Téléphone", getattr(candidat, "telephone", None), col2, info_y - ROW_H_2COL, 6.5 * cm)

    champ("Email", getattr(candidat, "email", None), col1, info_y - 2 * ROW_H_2COL, 6.5 * cm, taille=8.5)
    champ("Ville", getattr(candidat, "ville", None), col2, info_y - 2 * ROW_H_2COL, 6.5 * cm)

    bas_adresse = champ(
        "Adresse", getattr(candidat, "adresse", None),
        col1, info_y - 3 * ROW_H_2COL, 13.0 * cm, taille=8.5,
    )

    # ============================================================
    # 3. INFORMATIONS ACADÉMIQUES
    # ============================================================

    section_y = bas_adresse - SECTION_GAP
    titre_section(section_x, section_y, 3, "INFORMATIONS ACADÉMIQUES", section_width)

    info_y = section_y - TITLE_TO_FIELDS

    champ("Année académique", getattr(inscription.annee_academique, "libelle", None), col1, info_y, 6.5 * cm)
    champ("Filière", getattr(inscription.filiere, "nom", None), col2, info_y, 6.5 * cm, taille=8.5)

    champ("Code filière", getattr(inscription.filiere, "code", None), col1, info_y - ROW_H_2COL, 6.5 * cm)
    champ("Niveau", getattr(inscription.niveau, "nom", None), col2, info_y - ROW_H_2COL, 6.5 * cm)

    champ("Classe", getattr(inscription.classe, "nom", None), col1, info_y - 2 * ROW_H_2COL, 6.5 * cm)

    type_inscription = getattr(inscription, "type_inscription", "")
    if type_inscription == "PREMIERE_INSCRIPTION":
        type_label = "Première inscription"
    elif type_inscription:
        type_label = "Réinscription"
    else:
        type_label = "Non renseigné"

    statut = getattr(inscription, "statut", "")
    statut_labels = {
        "INSCRIT": "Inscrit",
        "EN_ATTENTE": "En attente",
        "ANNULE": "Annulé",
    }
    statut_label = statut_labels.get(statut, statut or "Non renseigné")

    champ("Type d'inscription", type_label, col2, info_y - 2 * ROW_H_2COL, 6.5 * cm)
    champ("Statut", statut_label, col1, info_y - 3 * ROW_H_2COL, 6.5 * cm)

    date_inscription = getattr(inscription, "date_inscription", None)
    if date_inscription:
        date_inscription = date_inscription.strftime("%d/%m/%Y à %H:%M")

    bas_section3 = champ("Date d'inscription", date_inscription, col2, info_y - 3 * ROW_H_2COL, 6.5 * cm)

    # ============================================================
    # BADGE STATUT (repère visuel rapide, rendu plus "officiel")
    # ============================================================

    statut_colors = {
        "Inscrit": colors.HexColor("#198754"),
        "En attente": colors.HexColor("#fd7e14"),
        "Annulé": colors.HexColor("#dc3545"),
    }
    couleur_statut = statut_colors.get(statut_label, gris)

    badge_w = 3.2 * cm
    badge_h = 0.6 * cm
    badge_x = largeur - marge_droite - 0.4 * cm - badge_w
    badge_y = bas_section3 + 0.3 * cm

    pdf.setFillColor(couleur_statut)
    pdf.roundRect(badge_x, badge_y, badge_w, badge_h, 4, stroke=0, fill=1)
    pdf.setFillColor(blanc)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawCentredString(badge_x + badge_w / 2, badge_y + 0.19 * cm, statut_label.upper())

    # ============================================================
    # SIGNATURES
    # ============================================================

    signature_y = 4.1 * cm

    pdf.setStrokeColor(gris_bordure)
    pdf.setLineWidth(0.6)
    pdf.line(marge_gauche + 0.4 * cm, signature_y + 0.5 * cm, largeur - marge_droite - 0.4 * cm, signature_y + 0.5 * cm)

    pdf.setFillColor(bleu_fonce)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(marge_gauche + 0.5 * cm, signature_y, "Signature de l'étudiant")
    pdf.drawString(largeur - marge_droite - 6.5 * cm, signature_y, "Visa de l'administration")

    pdf.setDash(2, 2)
    pdf.line(marge_gauche + 0.5 * cm, signature_y - 1.6 * cm, marge_gauche + 6.5 * cm, signature_y - 1.6 * cm)
    pdf.line(
        largeur - marge_droite - 6.5 * cm, signature_y - 1.6 * cm,
        largeur - marge_droite - 0.5 * cm, signature_y - 1.6 * cm,
    )
    pdf.setDash()

    # ============================================================
    # PIED DE PAGE
    # ============================================================

    pdf.setStrokeColor(gris_bordure)
    pdf.setLineWidth(0.5)
    pdf.line(marge_gauche + 0.4 * cm, 1.65 * cm, largeur - marge_droite - 0.4 * cm, 1.65 * cm)

    pdf.setFillColor(gris)
    pdf.setFont("Helvetica", 7)
    pdf.drawCentredString(largeur / 2, 1.35 * cm, "Document généré par le système de gestion des inscriptions")
    pdf.drawCentredString(largeur / 2, 1.0 * cm, "Université Internationale de Cocody")

    # ============================================================
    # FINALISATION
    # ============================================================

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    return FileResponse(
        buffer,
        as_attachment=False,
        filename=f"fiche_inscription_{inscription.numero}.pdf",
        content_type="application/pdf",
    )

from django.contrib.auth.decorators import login_required

@login_required
@transaction.atomic
def preinscription_valider(request, pk):

    preinscription = get_object_or_404(
        Preinscription.objects.select_related(
            "candidat",
            "annee_academique",
            "filiere",
            "niveau",
        ),
        pk=pk,
    )

    # ==========================================
    # VÉRIFICATION DU STATUT
    # ==========================================

    if preinscription.statut == "VALIDEE":

        messages.warning(
            request,
            "Cette préinscription est déjà validée."
        )

        return redirect(
            "gestion:preinscription_detail",
            pk=preinscription.pk
        )

    if preinscription.statut == "REJETEE":

        messages.error(
            request,
            "Impossible de valider une préinscription rejetée."
        )

        return redirect(
            "gestion:preinscription_detail",
            pk=preinscription.pk
        )

    # ==========================================
    # CRÉATION OU RÉCUPÉRATION DE L'ÉTUDIANT
    # ==========================================

    etudiant, created = Etudiant.objects.get_or_create(
        candidat=preinscription.candidat,
        defaults={
            "actif": True,
        }
    )

    # ==========================================
    # SI L'ÉTUDIANT EXISTE DÉJÀ
    # ==========================================

    if not created:

        etudiant.actif = True
        etudiant.save(update_fields=["actif"])

    # ==========================================
    # VALIDATION DE LA PRÉINSCRIPTION
    # ==========================================

    preinscription.statut = "VALIDEE"
    preinscription.date_traitement = timezone.now()
    preinscription.save(
        update_fields=[
            "statut",
            "date_traitement",
        ]
    )

    # ==========================================
    # MESSAGE
    # ==========================================

    if created:

        messages.success(
            request,
            f"La préinscription {preinscription.numero} "
            f"a été validée. "
            f"L'étudiant {etudiant.matricule} "
            f"a été créé avec succès."
        )

    else:

        messages.success(
            request,
            f"La préinscription {preinscription.numero} "
            f"a été validée. "
            f"L'étudiant {etudiant.matricule} "
            f"a été réactivé."
        )

    return redirect(
        "gestion:preinscription_detail",
        pk=preinscription.pk
    )

@login_required
@transaction.atomic
def preinscription_activer_etudiant(request, pk):

    if request.method != "POST":
        return redirect(
            "gestion:preinscription_detail",
            pk=pk
        )

    preinscription = get_object_or_404(
        Preinscription.objects.select_related(
            "candidat",
            "annee_academique",
            "filiere",
            "niveau",
        ),
        pk=pk,
    )

    # ==============================
    # VÉRIFICATION DU STATUT
    # ==============================

    if preinscription.statut != "VALIDEE":

        messages.error(
            request,
            "Cette préinscription doit être validée avant "
            "de pouvoir activer l'étudiant."
        )

        return redirect(
            "gestion:preinscription_detail",
            pk=preinscription.pk
        )

    # ==============================
    # RECHERCHE / CRÉATION ÉTUDIANT
    # ==============================

    etudiant, created = Etudiant.objects.get_or_create(
        candidat=preinscription.candidat,
        defaults={
            "actif": True,
        }
    )

    # ==============================
    # CAS : ÉTUDIANT EXISTANT
    # ==============================

    if not created:

        if etudiant.actif:

            messages.info(
                request,
                f"L'étudiant {etudiant.matricule} est déjà actif."
            )

        else:

            etudiant.actif = True
            etudiant.save(
                update_fields=["actif"]
            )

            messages.success(
                request,
                f"L'étudiant {etudiant.matricule} "
                f"a été réactivé avec succès."
            )

    # ==============================
    # CAS : NOUVEL ÉTUDIANT
    # ==============================

    else:

        messages.success(
            request,
            f"L'étudiant {etudiant.matricule} "
            f"a été créé et activé avec succès."
        )

    return redirect(
        "gestion:preinscription_detail",
        pk=preinscription.pk
    )