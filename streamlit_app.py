import streamlit as st
import json
from datetime import datetime
import os
from PIL import Image
import pandas as pd

# ======================================================
# 🔐 AUTHENTIFICATION
# ======================================================
st.set_page_config(page_title="Mini Cones", page_icon="🍦")

PASSWORD = "mehdi123"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Connexion")
    pwd = st.text_input("Entrez le mot de passe :", type="password")
    if st.button("Valider"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.success("Mot de passe correct ✔️")
        else:
            st.error("Mot de passe incorrect ❌")
    st.stop()

# ======================================================
# 📂 GESTION DES FICHIERS
# ======================================================
DATA_FILE = "stock.json"

PRODUITS = ["Twine Cones", "Au Lait 50g", "Bueno 70g", "Pistachio", "Crepes"]

# Initialisation fichier
if not os.path.exists(DATA_FILE):
    data = {
        "stock": {p: 100 for p in PRODUITS},  # tout en BOITES
        "ventes": []
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
else:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

# ======================================================
# 🖼️ LOGO
# ======================================================
try:
    logo = Image.open("logo.png")
    st.image(logo, width=200)
except:
    st.warning("Logo introuvable")

# ======================================================
# 📌 GESTION DES PAGES
# ======================================================
menu = st.sidebar.radio("📌 Menu", ["Nouvelle vente", "Stock", "Historique"])

# ======================================================
# 🛒 PAGE 1 : NOUVELLE VENTE
# ======================================================
if menu == "Nouvelle vente":

    st.title("🧾 Nouvelle vente")

    # Numéro automatique
    num_vente = 1 if len(data["ventes"]) == 0 else data["ventes"][-1]["num"] + 1
    today = datetime.today().strftime("%Y-%m-%d")

    st.write(f"**Date :** {today}")
    st.write(f"**Numéro de vente :** {num_vente}")

    # CLIENT
    client = st.text_input("Nom du client")

    # REVENDEUR
    revendeur = st.text_input("Nom du revendeur")
    frais_revendeur = st.number_input("Frais revendeur", min_value=0.0, step=1.0)

    # CHAUFFEUR
    chauffeur = st.text_input("Nom du chauffeur")
    frais_chauffeur = st.number_input("Frais chauffeur", min_value=0.0, step=1.0)

    # TOTAL FRAIS
    frais_total = frais_revendeur + frais_chauffeur
    st.info(f"💰 **Frais total : {frais_total} DA**")

    # PRODUITS
    st.subheader("Produits vendus")
    vente_produits = {}
    total_ventes = 0

    for p in PRODUITS:

        st.markdown(f"### {p}")

        # unité seulement pour Twine Cones
        if p == "Twine Cones":
            unite = st.selectbox(f"Unité {p}", ["Boîte", "Fardeau"], key=f"{p}_unite")
        else:
            unite = "Boîte"

        qte = st.number_input(f"Quantité vendue ({unite})", min_value=0, step=1, key=f"{p}_qte")
        prix = st.number_input(f"Prix unitaire (DA)", min_value=0.0, step=1.0, key=f"{p}_prix")

        # Conversion fardeau → boîte
        boites = qte * 6 if p == "Twine Cones" and unite == "Fardeau" else qte

        montant = boites * prix
        total_ventes += montant

        vente_produits[p] = {
            "unite": unite,
            "qte_unite": qte,
            "qte_boite": boites,
            "prix": prix,
            "montant": montant
        }

    st.subheader("Résumé")
    st.write(f"Total ventes : {total_ventes} DA")
    caisse = total_ventes - frais_total
    st.success(f"💵 Caisse finale : {caisse} DA")

    if st.button("Enregistrer"):

        # Mise à jour stock
        for p in PRODUITS:
            data["stock"][p] -= vente_produits[p]["qte_boite"]

        # Sauvegarde
        vente = {
            "num": num_vente,
            "date": today,
            "client": client,
            "revendeur": revendeur,
            "frais_revendeur": frais_revendeur,
            "chauffeur": chauffeur,
            "frais_chauffeur": frais_chauffeur,
            "frais_total": frais_total,
            "produits": vente_produits,
            "total": total_ventes,
            "caisse": caisse
        }

        data["ventes"].append(vente)

        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        st.success("Vente enregistrée ✔️")
        st.balloons()
        st.rerun()

# ======================================================
# 📦 PAGE 2 : STOCK
# ======================================================
elif menu == "Stock":

    st.title("📦 Stock actuel (en boîtes)")

    for p, q in data["stock"].items():
        st.write(f"**{p} :** {q} boîtes")

# ======================================================
# 📜 PAGE 3 : HISTORIQUE
# ======================================================
elif menu == "Historique":

    st.title("📜 Historique des ventes")

    if len(data["ventes"]) == 0:
        st.info("Aucune vente enregistrée.")
        st.stop()

    # Affichage tableau simple
    df = pd.DataFrame([{
        "Num": v["num"],
        "Date": v["date"],
        "Client": v["client"],
        "Total": v["total"],
        "Caisse": v["caisse"]
    } for v in data["ventes"]])

    st.dataframe(df)

    st.subheader("Modifier ou supprimer")

    choix = st.number_input("Numéro de vente", min_value=1, step=1)

    vente = next((v for v in data["ventes"] if v["num"] == choix), None)

    if vente:

        col1, col2 = st.columns(2)

        if col1.button("📝 Modifier"):
            st.session_state["edit_num"] = choix
            st.rerun()

        if col2.button("🗑️ Supprimer"):
            data["ventes"] = [v for v in data["ventes"] if v["num"] != choix]
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)
            st.success("Vente supprimée ✔️")
            st.rerun()

# ======================================================
# 🛠️ PAGE MODIFICATION (automatique)
# ======================================================
if "edit_num" in st.session_state:
    num = st.session_state["edit_num"]
    vente = next((v for v in data["ventes"] if v["num"] == num), None)

    st.title(f"📝 Modifier la vente N°{num}")

    client = st.text_input("Client", vente["client"])

    revendeur = st.text_input("Revendeur", vente["revendeur"])
    frais_revendeur = st.number_input("Frais revendeur", value=float(vente["frais_revendeur"]))

    chauffeur = st.text_input("Chauffeur", vente["chauffeur"])
    frais_chauffeur = st.number_input("Frais chauffeur", value=float(vente["frais_chauffeur"]))

    frais_total = frais_chauffeur + frais_revendeur

    st.info(f"Frais total : {frais_total}")

    st.subheader("Produits")
    total_ventes = 0
    vente_produits = {}

    for p in PRODUITS:
        qte_boite = st.number_input(f"{p} (boîtes)", min_value=0, value=int(vente["produits"][p]["qte_boite"]))
        prix = st.number_input(f"Prix {p}", min_value=0.0, value=float(vente["produits"][p]["prix"]))

        montant = qte_boite * prix
        total_ventes += montant

        vente_produits[p] = {
            "qte_boite": qte_boite,
            "prix": prix,
            "montant": montant
        }

    caisse = total_ventes - frais_total
    st.success(f"Caisse : {caisse}")

    if st.button("Enregistrer les modifications"):

        vente["client"] = client
        vente["revendeur"] = revendeur
        vente["frais_revendeur"] = frais_revendeur
        vente["chauffeur"] = chauffeur
        vente["frais_chauffeur"] = frais_chauffeur
        vente["frais_total"] = frais_total
        vente["produits"] = vente_produits
        vente["total"] = total_ventes
        vente["caisse"] = caisse

        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        del st.session_state["edit_num"]
        st.success("Vente modifiée ✔️")
        st.rerun()
