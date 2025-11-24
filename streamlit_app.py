import streamlit as st
import json
from datetime import datetime
import os
from PIL import Image

# --- Configuration page ---
st.set_page_config(page_title="Mini Cones", page_icon="🍦")

# --- Authentification simple ---
PASSWORD = "mehdi123"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Connexion")
    pwd = st.text_input("Entrez le mot de passe :", type="password")
    if st.button("Valider"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.success("✅ Mot de passe correct !")
        else:
            st.error("❌ Mot de passe incorrect")
    st.stop()

# --- Logo ---
try:
    logo = Image.open("logo.png")
    st.image(logo, width=200)
except FileNotFoundError:
    st.warning("Logo non trouvé ! Vérifie le nom du fichier et son emplacement.")

# --- Fichier de stockage ---
DATA_FILE = "stock.json"

if not os.path.exists(DATA_FILE):
    data = {
        "stock": {
            "Twine Cones": 100,
            "Au Lait 50g": 200,
            "Bueno 70g": 150,
            "Pistachio": 180
        },
        "ventes": []
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
else:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

# --- Sélection de la page ---
page = st.sidebar.selectbox("Choisir une page", ["Nouvelle vente", "Historique des ventes", "Gestion du stock"])

if page == "Nouvelle vente":
    st.title("💰 Nouvelle vente")

    # Numéro de vente automatique
    num_vente = 1 if len(data["ventes"]) == 0 else data["ventes"][-1]["num"] + 1

    # Date et numéro
    today = datetime.today().strftime("%Y-%m-%d")
    st.write(f"**Date :** {today}")
    st.write(f"**Numéro de vente :** {num_vente}")

    # Client et personnel
    client = st.text_input("Nom du client")
    dettes = st.number_input("Dette du client (montant non payé)", min_value=0.0, step=1.0)
    operateur = st.text_input("Opérateur")
    chauffeur = st.text_input("Chauffeur")
    frais = st.number_input("Frais du jour", min_value=0.0, step=1.0)

    # Produits
    st.subheader("Produits vendus")
    produits = list(data["stock"].keys())
    vente_produits = {}
    total_ventes = 0

    for p in produits:
        st.markdown(f"**{p}**")
        unite = st.selectbox(f"Unité {p}", ["Boîte", "Fardeau"], key=f"{p}_unite")
        qte = st.number_input(f"Quantité vendue {p}", min_value=0, max_value=data["stock"][p], step=1, key=f"{p}_qte")
        prix = st.number_input(f"Prix unitaire {p}", min_value=0.0, step=1.0, key=f"{p}_prix")
        montant = qte * prix
        st.write(f"Montant : {montant}")

        vente_produits[p] = {"unite": unite, "qte": qte, "prix": prix, "montant": montant}
        total_ventes += montant

    # Calcul caisse
    caisse = total_ventes - dettes - frais
    st.subheader("Résumé du jour")
    st.write(f"Total ventes : {total_ventes}")
    st.write(f"Dettes : {dettes}")
    st.write(f"Frais : {frais}")
    st.write(f"💵 Caisse finale : {caisse}")

    # Enregistrer la vente
    if st.button("Enregistrer la vente"):
        for p in produits:
            data["stock"][p] -= vente_produits[p]["qte"]

        vente = {
            "num": num_vente,
            "date": today,
            "client": client,
            "produits": vente_produits,
            "dettes": dettes,
            "operateur": operateur,
            "chauffeur": chauffeur,
            "frais": frais,
            "caisse": caisse
        }
        data["ventes"].append(vente)

        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        st.success("Vente enregistrée avec succès !")
        st.balloons()

elif page == "Historique des ventes":
    st.title("📋 Historique des ventes")
    if len(data["ventes"]) == 0:
        st.info("Aucune vente enregistrée.")
    else:
        for vente in data["ventes"]:
            st.subheader(f"Vente #{vente['num']} - {vente['date']}")
            st.write(f"**Client :** {vente['client']}")
            st.write(f"**Opérateur :** {vente['operateur']}")
            st.write(f"**Chauffeur :** {vente['chauffeur']}")
            st.write(f"**Dettes :** {vente['dettes']}")
            st.write(f"**Frais :** {vente['frais']}")
            st.write(f"💵 **Caisse :** {vente['caisse']}")
            st.write("**Produits vendus :**")
            st.table({p: info["qte"] for p, info in vente["produits"].items()})

elif page == "Gestion du stock":
    st.title("📦 Gestion du stock")
    for p in data["stock"]:
        qte = st.number_input(f"{p} (actuellement {data['stock'][p]})", value=data["stock"][p], step=1, key=f"stock_{p}")
        data["stock"][p] = qte

    if st.button("Mettre à jour le stock"):
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        st.success("Stock mis à jour avec succès !")
