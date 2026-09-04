from django.contrib import admin
from .models import (
    AnneeAcademique,
    Filiere,
    Niveau,
    Classe,
    Candidat,
    Preinscription,
    Etudiant,
    Inscription,
    Scolarite,
    Echeance,
    Paiement,
    Recu,
)


# ============================================================
# 1. ANNÉE ACADÉMIQUE
# ============================================================

@admin.register(AnneeAcademique)
class AnneeAcademiqueAdmin(admin.ModelAdmin):

    list_display = (
        "libelle",
        "date_debut",
        "date_fin",
        "active",
    )

    list_filter = (
        "active",
    )

    search_fields = (
        "libelle",
    )

    ordering = (
        "-libelle",
    )


# ============================================================
# 2. FILIÈRE
# ============================================================

@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "nom",
        "active",
    )

    list_filter = (
        "active",
    )

    search_fields = (
        "code",
        "nom",
    )

    ordering = (
        "nom",
    )


# ============================================================
# 3. NIVEAU
# ============================================================

@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):

    list_display = (
        "code",
        "nom",
        "ordre",
        "active",
    )

    list_filter = (
        "active",
    )

    search_fields = (
        "code",
        "nom",
    )

    ordering = (
        "ordre",
    )


# ============================================================
# 4. CLASSE
# ============================================================

@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):

    list_display = (
        "nom",
        "filiere",
        "niveau",
        "annee_academique",
        "capacite",
        "active",
    )

    list_filter = (
        "filiere",
        "niveau",
        "annee_academique",
        "active",
    )

    search_fields = (
        "nom",
        "filiere__nom",
        "filiere__code",
        "niveau__nom",
        "niveau__code",
    )

    ordering = (
        "filiere",
        "niveau",
        "nom",
    )


# ============================================================
# 5. CANDIDAT
# ============================================================

@admin.register(Candidat)
class CandidatAdmin(admin.ModelAdmin):

    list_display = (
        "matricule_candidat",
        "nom",
        "prenoms",
        "sexe",
        "telephone",
        "ville",
        "actif",
        "date_creation",
    )

    list_filter = (
        "sexe",
        "actif",
        "ville",
    )

    search_fields = (
        "matricule_candidat",
        "nom",
        "prenoms",
        "telephone",
        "email",
        "ville",
    )

    readonly_fields = (
        "matricule_candidat",
        "date_creation",
        "date_modification",
    )

    ordering = (
        "nom",
        "prenoms",
    )


# ============================================================
# 6. PRÉINSCRIPTION
# ============================================================

@admin.register(Preinscription)
class PreinscriptionAdmin(admin.ModelAdmin):

    list_display = (
        "numero",
        "candidat",
        "annee_academique",
        "filiere",
        "niveau",
        "statut",
        "date_demande",
    )

    list_filter = (
        "annee_academique",
        "filiere",
        "niveau",
        "statut",
    )

    search_fields = (
        "numero",
        "candidat__nom",
        "candidat__prenoms",
        "candidat__matricule_candidat",
    )

    readonly_fields = (
        "numero",
        "date_demande",
        "date_traitement",
    )

    ordering = (
        "-date_demande",
    )


# ============================================================
# 7. ÉTUDIANT
# ============================================================

@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):

    list_display = (
        "matricule",
        "candidat",
        "actif",
        "date_creation",
    )

    list_filter = (
        "actif",
    )

    search_fields = (
        "matricule",
        "candidat__nom",
        "candidat__prenoms",
        "candidat__matricule_candidat",
    )

    readonly_fields = (
        "matricule",
        "date_creation",
    )

    ordering = (
        "matricule",
    )


# ============================================================
# 8. INSCRIPTION
# ============================================================

@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):

    list_display = (
        "numero",
        "etudiant",
        "annee_academique",
        "filiere",
        "niveau",
        "classe",
        "type_inscription",
        "statut",
        "date_inscription",
    )

    list_filter = (
        "annee_academique",
        "filiere",
        "niveau",
        "classe",
        "type_inscription",
        "statut",
    )

    search_fields = (
        "numero",
        "etudiant__matricule",
        "etudiant__candidat__nom",
        "etudiant__candidat__prenoms",
    )

    readonly_fields = (
        "numero",
        "date_inscription",
    )

    ordering = (
        "-date_inscription",
    )


# ============================================================
# 9. SCOLARITÉ
# ============================================================

@admin.register(Scolarite)
class ScolariteAdmin(admin.ModelAdmin):

    list_display = (
        "inscription",
        "montant_total",
        "remise",
        "montant_net",
        "montant_paye",
        "reste_a_payer",
        "statut",
        "date_creation",
    )

    list_filter = (
        "statut",
    )

    search_fields = (
        "inscription__numero",
        "inscription__etudiant__matricule",
        "inscription__etudiant__candidat__nom",
        "inscription__etudiant__candidat__prenoms",
    )

    readonly_fields = (
        "montant_net",
        "montant_paye",
        "reste_a_payer",
        "date_creation",
        "date_modification",
    )

    ordering = (
        "-date_creation",
    )


# ============================================================
# 10. ÉCHÉANCE
# ============================================================

@admin.register(Echeance)
class EcheanceAdmin(admin.ModelAdmin):

    list_display = (
        "scolarite",
        "numero",
        "libelle",
        "montant",
        "montant_paye",
        "reste_a_payer",
        "date_echeance",
        "statut",
    )

    list_filter = (
        "statut",
        "date_echeance",
    )

    search_fields = (
        "libelle",
        "scolarite__inscription__numero",
        "scolarite__inscription__etudiant__matricule",
    )

    readonly_fields = (
        "montant_paye",
        "reste_a_payer",
    )

    ordering = (
        "numero",
    )


# ============================================================
# 11. PAIEMENT
# ============================================================

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):

    list_display = (
        "reference",
        "scolarite",
        "echeance",
        "montant",
        "mode_paiement",
        "statut",
        "date_paiement",
    )

    list_filter = (
        "mode_paiement",
        "statut",
        "date_paiement",
    )

    search_fields = (
        "reference",
        "scolarite__inscription__numero",
        "scolarite__inscription__etudiant__matricule",
    )

    readonly_fields = (
        "reference",
        "date_paiement",
    )

    ordering = (
        "-date_paiement",
    )


# ============================================================
# 12. REÇU
# ============================================================

@admin.register(Recu)
class RecuAdmin(admin.ModelAdmin):

    list_display = (
        "numero",
        "paiement",
        "date_emission",
    )

    search_fields = (
        "numero",
        "paiement__reference",
        "paiement__scolarite__inscription__etudiant__matricule",
    )

    readonly_fields = (
        "numero",
        "date_emission",
    )

    ordering = (
        "-date_emission",
    )