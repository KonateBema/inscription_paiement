from django.urls import path

from . import views


from django.urls import include, path




app_name = "gestion"


urlpatterns = [
    
    
    # =========================================================
    # TABLEAU DE BORD
    # =========================================================

    path(
        "",
        views.dashboard,
        name="dashboard",
    ),
    path(
    "deconnexion/",
    views.deconnexion,
    name="logout",
),


    # =========================================================
    # CANDIDATS
    # =========================================================

    path(
        "candidats/",
        views.candidats_liste,
        name="candidats_liste",
    ),

    path(
        "candidats/ajouter/",
        views.candidat_ajouter,
        name="candidat_ajouter",
    ),

    path(
        "candidats/<int:pk>/",
        views.candidat_detail,
        name="candidat_detail",
    ),

    path(
        "candidats/<int:pk>/modifier/",
        views.candidat_modifier,
        name="candidat_modifier",
    ),

    path(
        "candidats/<int:pk>/creer-etudiant/",
        views.candidat_creer_etudiant,
        name="candidat_creer_etudiant",
    ),


    # =========================================================
    # PRÉINSCRIPTIONS
    # =========================================================

    path(
        "preinscriptions/",
        views.preinscription_liste,
        name="preinscription_liste",
    ),

    path(
        "preinscriptions/nouvelle/",
        views.preinscription_create,
        name="preinscription_create",
    ),

    path(
        "preinscriptions/<int:pk>/",
        views.preinscription_detail,
        name="preinscription_detail",
    ),

    path(
        "preinscriptions/<int:pk>/modifier/",
        views.preinscription_update,
        name="preinscription_update",
    ),

    path(
        "preinscriptions/<int:pk>/supprimer/",
        views.preinscription_delete,
        name="preinscription_delete",
    ),


    # =========================================================
    # ÉTUDIANTS
    # =========================================================

    path(
        "etudiants/",
        views.etudiants_liste,
        name="etudiants_liste",
    ),

    path(
        "etudiants/<int:pk>/",
        views.etudiant_detail,
        name="etudiant_detail",
    ),


    # =========================================================
    # INSCRIPTIONS
    # =========================================================

    path(
        "inscriptions/",
        views.inscriptions_liste,
        name="inscriptions_liste",
    ),

    path(
        "inscriptions/nouvelle/",
        views.inscription_create,
        name="inscription_create",
    ),

    path(
        "inscriptions/<int:pk>/",
        views.inscription_detail,
        name="inscription_detail",
    ),

    # =========================
    # PREINSCRIPTIONS
    # =========================


    # =========================
    # PREINSCRIPTIONS
    # =========================

    path(
        "preinscriptions/",
        views.preinscription_liste,
        name="preinscription_liste",
    ),

    path(
        "preinscriptions/nouvelle/",
        views.preinscription_create,
        name="preinscription_create",
    ),

    path(
        "preinscriptions/<int:pk>/",
        views.preinscription_detail,
        name="preinscription_detail",
    ),

    path(
        "preinscriptions/<int:pk>/modifier/",
        views.preinscription_update,
        name="preinscription_update",
    ),

    path(
        "preinscriptions/<int:pk>/supprimer/",
        views.preinscription_delete,
        name="preinscription_delete",
    ),



    # =========================
    # INSCRIPTIONS
    # =========================

    path(
        "inscriptions/",
        views.inscriptions_liste,
        name="inscriptions_liste",
    ),

    path(
        "inscriptions/nouvelle/",
        views.inscription_create,
        name="inscription_create",
    ),

    path(
        "inscriptions/<int:pk>/",
        views.inscription_detail,
        name="inscription_detail",
    ),

    path(
        "inscriptions/<int:pk>/modifier/",
        views.inscription_update,
        name="inscription_update",
    ),




    # =========================================================
    # SCOLARITÉS
    # =========================================================

    path(
        "scolarites/",
        views.scolarites_liste,
        name="scolarites_liste",
    ),

    path(
        "scolarites/nouvelle/",
        views.scolarite_create,
        name="scolarite_create",
    ),

    path(
        "scolarites/<int:pk>/",
        views.scolarite_detail,
        name="scolarite_detail",
    ),


    # =========================================================
    # ÉCHÉANCES
    # =========================================================

    path(
        "echeances/",
        views.echeances_liste,
        name="echeances_liste",
    ),

    path(
        "echeances/nouvelle/",
        views.echeance_create,
        name="echeance_create",
    ),

    path(
        "echeances/<int:pk>/",
        views.echeance_detail,
        name="echeance_detail",
    ),
    path(
    "scolarites/<int:pk>/modifier/",
    views.scolarite_update,
    name="scolarite_update",
    ),
 
# ============================================================
# ÉCHÉANCES
# ============================================================

path("echeances/",views.echeances_liste,name="echeances_liste"),

path("echeances/nouvelle/",views.echeance_create,name="echeance_create"),
path( "echeances/<int:pk>/",views.echeance_detail,name="echeance_detail"),

path("echeances/<int:pk>/modifier/", views.echeance_update,name="echeance_update"),
# ============================================================
# PAIEMENTS
# ============================================================

path("paiements/",views.paiements_liste,name="paiements_liste"),
path("paiements/nouveau/",views.paiement_create,name="paiement_create"),
path("paiements/<int:pk>/",views.paiement_detail,name="paiement_detail"),
path("paiements/<int:pk>/modifier/",views.paiement_update,name="paiement_update"),

# =========================================================
# REÇUS
# =========================================================

path("recus/",views.recus_liste,name="recus_liste",),
path("recus/<int:pk>/",views.recu_detail,name="recu_detail",),


# Reçus
path("recus/", views.recus_liste, name="recus_liste"),
path("recus/<int:pk>/", views.recu_detail, name="recu_detail"),
path("recus/<int:pk>/pdf/", views.recu_pdf, name="recu_pdf"),

path("inscriptions/<int:pk>/fiche-pdf/",views.fiche_inscription_pdf,name="fiche_inscription_pdf"),
path("preinscriptions/<int:pk>/valider/",views.preinscription_valider,name="preinscription_valider",),
path("preinscriptions/<int:pk>/activer-etudiant/",views.preinscription_activer_etudiant,name="preinscription_activer_etudiant",),
# path("preinscriptions/<int:pk>/",views.preinscription_detail,name="preinscription_detail",),



]

