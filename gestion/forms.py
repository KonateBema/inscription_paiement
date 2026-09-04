from django import forms
from django.db.models import Sum
from decimal import Decimal
from .models import Candidat
from .models import (
    Preinscription,
    Filiere,
    Niveau,
    AnneeAcademique,
    Etudiant,
    Inscription,
    Classe,
    Scolarite,
    Echeance,
    Paiement,
)
from django import forms


class CandidatForm(forms.ModelForm):

    class Meta:
        model = Candidat

        fields = [
            "nom",
            "prenoms",
            "sexe",
            "date_naissance",
            "lieu_naissance",
            "nationalite",
            "photo",
            "telephone",
            "email",
            "adresse",
            "ville",
            "dernier_diplome",
            "serie_diplome",
            "annee_obtention",
            "etablissement_origine",
            "actif",
        ]

        widgets = {
            "nom": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nom",
                }
            ),

            "prenoms": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Prénoms",
                }
            ),

            "sexe": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "date_naissance": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),

            "lieu_naissance": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Lieu de naissance",
                }
            ),

            "nationalite": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nationalité",
                }
            ),

            "photo": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                }
            ),

            "telephone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex : 0700000000",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "exemple@email.com",
                }
            ),

            "adresse": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Adresse",
                }
            ),

            "ville": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ville",
                }
            ),

            "dernier_diplome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex : Baccalauréat",
                }
            ),

            "serie_diplome": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex : D",
                }
            ),

            "annee_obtention": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex : 2025",
                }
            ),

            "etablissement_origine": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Établissement d'origine",
                }
            ),

            "actif": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
        
        
class PreinscriptionForm(forms.ModelForm):

    class Meta:
        model = Preinscription

        fields = [
            "candidat",
            "annee_academique",
            "filiere",
            "niveau",
            "statut",
            "observation",
        ]

        widgets = {
            "candidat": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "annee_academique": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "filiere": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "niveau": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "statut": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "observation": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Observation éventuelle...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["candidat"].queryset = (
            Candidat.objects.all()
            .order_by("nom", "prenoms")
        )

        self.fields["annee_academique"].queryset = (
            AnneeAcademique.objects.all()
            .order_by("-id")
        )

        self.fields["filiere"].queryset = (
            Filiere.objects.all()
            .order_by("nom")
        )

        self.fields["niveau"].queryset = (
            Niveau.objects.all()
            .order_by("nom")
               )

# =========================================================
# FORMULAIRE INSCRIPTION
# =========================================================

# =========================================================
# FORMULAIRE INSCRIPTION
# =========================================================

class InscriptionForm(forms.ModelForm):

    class Meta:
        model = Inscription

        fields = [
            "etudiant",
            "annee_academique",
            "filiere",
            "niveau",
            "classe",
            "type_inscription",
            "statut",
            "observation",
        ]

        widgets = {

            "etudiant": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "annee_academique": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "filiere": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "niveau": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "classe": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "type_inscription": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "statut": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "observation": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Observation éventuelle...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # =====================================================
        # ÉTUDIANTS
        # =====================================================

        self.fields["etudiant"].queryset = (
            Etudiant.objects
            .select_related("candidat")
            .filter(actif=True)
            .order_by(
                "candidat__nom",
                "candidat__prenoms",
            )
        )

        # =====================================================
        # ANNÉES ACADÉMIQUES
        # =====================================================

        self.fields["annee_academique"].queryset = (
            AnneeAcademique.objects
            .order_by("-id")
        )

        # =====================================================
        # FILIÈRES
        # =====================================================

        self.fields["filiere"].queryset = (
            Filiere.objects
            .filter(active=True)
            .order_by("nom")
        )

        # =====================================================
        # NIVEAUX
        # =====================================================

        self.fields["niveau"].queryset = (
            Niveau.objects
            .filter(active=True)
            .order_by("ordre")
        )

        # =====================================================
        # CLASSES
        # =====================================================

        self.fields["classe"].queryset = (
            Classe.objects
            .select_related(
                "filiere",
                "niveau",
                "annee_academique",
            )
            .filter(active=True)
            .order_by(
                "filiere__nom",
                "niveau__ordre",
                "nom",
            )
        )

        # =====================================================
        # LABELS
        # =====================================================

        self.fields["etudiant"].label = "Étudiant"

        self.fields["annee_academique"].label = "Année académique"

        self.fields["filiere"].label = "Filière"

        self.fields["niveau"].label = "Niveau"

        self.fields["classe"].label = "Classe"

        self.fields["type_inscription"].label = "Type d'inscription"

        self.fields["statut"].label = "Statut"

        self.fields["observation"].label = "Observation"

    # =========================================================
    # VALIDATION
    # =========================================================

    def clean(self):

        cleaned_data = super().clean()

        etudiant = cleaned_data.get("etudiant")
        annee_academique = cleaned_data.get("annee_academique")

        # -----------------------------------------------------
        # Vérifier qu'un étudiant n'a pas déjà une inscription
        # pour cette année académique
        # -----------------------------------------------------

        if etudiant and annee_academique:

            inscriptions = Inscription.objects.filter(
                etudiant=etudiant,
                annee_academique=annee_academique,
            )

            # En modification, exclure l'inscription actuelle
            if self.instance and self.instance.pk:

                inscriptions = inscriptions.exclude(
                    pk=self.instance.pk
                )

            if inscriptions.exists():

                raise forms.ValidationError(
                    "Cet étudiant possède déjà une inscription "
                    "pour cette année académique."
                )

        # -----------------------------------------------------
        # Vérifier la cohérence Filière / Niveau / Classe
        # -----------------------------------------------------

        filiere = cleaned_data.get("filiere")
        niveau = cleaned_data.get("niveau")
        classe = cleaned_data.get("classe")

        if classe:

            if filiere and classe.filiere_id != filiere.id:

                self.add_error(
                    "classe",
                    "La classe sélectionnée ne correspond pas "
                    "à la filière choisie."
                )

            if niveau and classe.niveau_id != niveau.id:

                self.add_error(
                    "classe",
                    "La classe sélectionnée ne correspond pas "
                    "au niveau choisi."
                )

            if (
                annee_academique
                and classe.annee_academique_id != annee_academique.id
            ):

                self.add_error(
                    "classe",
                    "La classe sélectionnée ne correspond pas "
                    "à l'année académique choisie."
                )

        return cleaned_data
    
# =========================================================
# FORMULAIRE SCOLARITÉ
# =========================================================

class ScolariteForm(forms.ModelForm):

    class Meta:
        model = Scolarite

        fields = [
            "inscription",
            "montant_total",
            "remise",
            "observation",
        ]

        widgets = {

            "inscription": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "montant_total": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Ex : 500000",
                }
            ),

            "remise": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Ex : 50000",
                }
            ),

            "observation": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Observation éventuelle...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # =====================================================
        # INSCRIPTIONS
        # =====================================================

        self.fields["inscription"].queryset = (
            Inscription.objects
            .select_related(
                "etudiant__candidat",
                "annee_academique",
                "filiere",
                "niveau",
                "classe",
            )
            .filter(
                statut="INSCRIT"
            )
            .order_by(
                "-date_inscription"
            )
        )

        # =====================================================
        # LABELS
        # =====================================================

        self.fields["inscription"].label = "Inscription"

        self.fields["montant_total"].label = "Montant total"

        self.fields["remise"].label = "Remise"

        self.fields["observation"].label = "Observation"

        # =====================================================
        # AIDE
        # =====================================================

        self.fields["montant_total"].help_text = (
            "Montant total de la scolarité en FCFA."
        )

        self.fields["remise"].help_text = (
            "Montant de la remise accordée, le cas échéant."
        )

    # =========================================================
    # VALIDATION
    # =========================================================

    def clean(self):

        cleaned_data = super().clean()

        inscription = cleaned_data.get("inscription")
        montant_total = cleaned_data.get("montant_total")
        remise = cleaned_data.get("remise")

        # -----------------------------------------------------
        # Vérifier qu'une inscription n'a qu'une seule
        # scolarité
        # -----------------------------------------------------

        if inscription:

            scolarites = Scolarite.objects.filter(
                inscription=inscription
            )

            # En modification, exclure la scolarité actuelle
            if self.instance and self.instance.pk:

                scolarites = scolarites.exclude(
                    pk=self.instance.pk
                )

            if scolarites.exists():

                self.add_error(
                    "inscription",
                    "Cette inscription possède déjà une scolarité."
                )

        # -----------------------------------------------------
        # Vérifier la remise
        # -----------------------------------------------------

        if montant_total is not None and remise is not None:

            if remise < 0:

                self.add_error(
                    "remise",
                    "La remise ne peut pas être négative."
                )

            if montant_total < 0:

                self.add_error(
                    "montant_total",
                    "Le montant total ne peut pas être négatif."
                )

            if remise > montant_total:

                self.add_error(
                    "remise",
                    "La remise ne peut pas être supérieure "
                    "au montant total."
                )

        return cleaned_data


class EcheanceForm(forms.ModelForm):

    class Meta:
        model = Echeance

        fields = [
            "scolarite",
            "numero",
            "libelle",
            "montant",
            "date_echeance",
        ]

        widgets = {
            "scolarite": forms.Select(
                attrs={"class": "form-select"}
            ),

            "numero": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": "1",
                    "placeholder": "Ex : 1",
                }
            ),

            "libelle": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Ex : 1ère tranche",
                }
            ),

            "montant": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0",
                    "placeholder": "Ex : 200000",
                }
            ),

            "date_echeance": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "type": "date",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["scolarite"].queryset = (
            Scolarite.objects
            .select_related(
                "inscription__etudiant__candidat",
                "inscription__annee_academique",
            )
            .order_by(
                "-date_creation"
            )
        )

        self.fields["scolarite"].label = "Scolarité"
        self.fields["numero"].label = "Numéro"
        self.fields["libelle"].label = "Libellé"
        self.fields["montant"].label = "Montant"
        self.fields["date_echeance"].label = "Date d'échéance"

    def clean(self):

        cleaned_data = super().clean()

        scolarite = cleaned_data.get("scolarite")
        numero = cleaned_data.get("numero")
        montant = cleaned_data.get("montant")

        if scolarite and numero:

            echeances = Echeance.objects.filter(
                scolarite=scolarite,
                numero=numero,
            )

            if self.instance and self.instance.pk:
                echeances = echeances.exclude(
                    pk=self.instance.pk
                )

            if echeances.exists():

                self.add_error(
                    "numero",
                    "Ce numéro d'échéance existe déjà pour cette scolarité."
                )

        if montant is not None and montant < 0:

            self.add_error(
                "montant",
                "Le montant ne peut pas être négatif."
            )

        return cleaned_data

class PaiementForm(forms.ModelForm):

    class Meta:
        model = Paiement

        fields = [
            "scolarite",
            "echeance",
            "montant",
            "mode_paiement",
            "statut",
            "observation",
        ]

        widgets = {

            "scolarite": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "echeance": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "montant": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                    "placeholder": "Ex : 100000",
                }
            ),

            "mode_paiement": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "statut": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),

            "observation": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Observation éventuelle...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # =====================================================
        # SCOLARITES
        # =====================================================

        self.fields["scolarite"].queryset = (
            Scolarite.objects
            .select_related(
                "inscription__etudiant__candidat",
                "inscription__annee_academique",
                "inscription__filiere",
                "inscription__niveau",
            )
            .order_by("-date_creation")
        )

        # =====================================================
        # ECHEANCES
        # =====================================================

        self.fields["echeance"].queryset = (
            Echeance.objects
            .select_related(
                "scolarite__inscription__etudiant__candidat",
            )
            .order_by(
                "scolarite",
                "numero",
            )
        )

        # =====================================================
        # LABELS
        # =====================================================

        self.fields["scolarite"].label = "Scolarité"
        self.fields["echeance"].label = "Échéance"
        self.fields["montant"].label = "Montant"
        self.fields["mode_paiement"].label = "Mode de paiement"
        self.fields["statut"].label = "Statut"
        self.fields["observation"].label = "Observation"

        # =====================================================
        # ECHEANCE FACULTATIVE
        # =====================================================

        self.fields["echeance"].required = False

        self.fields["echeance"].empty_label = "Paiement sans échéance précise"

    # =========================================================
    # VALIDATION
    # =========================================================

    def clean(self):

        cleaned_data = super().clean()

        scolarite = cleaned_data.get("scolarite")
        echeance = cleaned_data.get("echeance")
        montant = cleaned_data.get("montant")
        statut = cleaned_data.get("statut")

        # -----------------------------------------------------
        # Vérifier le montant
        # -----------------------------------------------------

        if montant is not None:

            if montant <= 0:

                self.add_error(
                    "montant",
                    "Le montant du paiement doit être supérieur à 0."
                )

        # -----------------------------------------------------
        # Vérifier l'échéance
        # -----------------------------------------------------

        if scolarite and echeance:

            if echeance.scolarite_id != scolarite.id:

                self.add_error(
                    "echeance",
                    "Cette échéance n'appartient pas à la scolarité sélectionnée."
                )

        # -----------------------------------------------------
        # Vérifier le reste de la scolarité
        # -----------------------------------------------------

        if scolarite and montant and statut == "VALIDE":

            reste = scolarite.reste_a_payer

            # En modification, le paiement actuel est déjà
            # comptabilisé dans le montant payé.
            if self.instance and self.instance.pk:

                if self.instance.statut == "VALIDE":

                    reste += self.instance.montant

            if montant > reste:

                self.add_error(
                    "montant",
                    (
                        f"Le montant dépasse le reste à payer de "
                        f"{reste:,.0f} FCFA."
                    )
                )

        # -----------------------------------------------------
        # Vérifier le reste de l'échéance
        # -----------------------------------------------------

        if echeance and montant and statut == "VALIDE":

            reste_echeance = echeance.reste_a_payer

            if self.instance and self.instance.pk:

                if (
                    self.instance.statut == "VALIDE"
                    and self.instance.echeance_id == echeance.id
                ):

                    reste_echeance += self.instance.montant

            if montant > reste_echeance:

                self.add_error(
                    "montant",
                    (
                        f"Le montant dépasse le reste à payer de "
                        f"l'échéance : {reste_echeance:,.0f} FCFA."
                    )
                )

        return cleaned_data



class PaiementFormAAA(forms.ModelForm):

    class Meta:
        model = Paiement

        fields = [
            "scolarite",
            "echeance",
            "montant",
            "mode_paiement",
            "statut",
            "observation",
        ]

        widgets = {
            "scolarite": forms.Select(
                attrs={"class": "form-select"}
            ),

            "echeance": forms.Select(
                attrs={"class": "form-select"}
            ),

            "montant": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "0.01",
                    "min": "0.01",
                    "placeholder": "Ex : 100000",
                }
            ),

            "mode_paiement": forms.Select(
                attrs={"class": "form-select"}
            ),

            "statut": forms.Select(
                attrs={"class": "form-select"}
            ),

            "observation": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Observation éventuelle...",
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["scolarite"].queryset = (
            Scolarite.objects
            .select_related(
                "inscription__etudiant__candidat",
                "inscription__annee_academique",
            )
            .order_by("-date_creation")
        )

        self.fields["echeance"].queryset = (
            Echeance.objects
            .select_related(
                "scolarite__inscription__etudiant__candidat"
            )
            .order_by(
                "scolarite_id",
                "numero"
            )
        )

        self.fields["scolarite"].label = "Scolarité"
        self.fields["echeance"].label = "Échéance"
        self.fields["montant"].label = "Montant payé"
        self.fields["mode_paiement"].label = "Mode de paiement"
        self.fields["statut"].label = "Statut"
        self.fields["observation"].label = "Observation"

    def clean(self):

        cleaned_data = super().clean()

        scolarite = cleaned_data.get("scolarite")
        echeance = cleaned_data.get("echeance")
        montant = cleaned_data.get("montant")

        if montant is not None and montant <= 0:
            self.add_error(
                "montant",
                "Le montant du paiement doit être supérieur à zéro."
            )

        # L'échéance doit appartenir à la scolarité sélectionnée
        if scolarite and echeance:

            if echeance.scolarite_id != scolarite.id:

                self.add_error(
                    "echeance",
                    "Cette échéance n'appartient pas à la scolarité sélectionnée."
                )

        # Vérifier le montant disponible sur l'échéance
        if montant and echeance:

            montant_deja_paye = (
                echeance.paiements
                .filter(statut="VALIDE")
                .exclude(
                    pk=self.instance.pk
                    if self.instance and self.instance.pk
                    else None
                )
                .aggregate(
                    total=Sum("montant")
                )["total"]
                or Decimal("0")
            )

            reste = echeance.montant - montant_deja_paye

            if montant > reste:

                self.add_error(
                    "montant",
                    f"Le montant dépasse le reste à payer de "
                    f"{reste:.2f} FCFA sur cette échéance."
                )

        return cleaned_data


