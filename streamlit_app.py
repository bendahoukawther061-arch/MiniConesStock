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
    st.image(logo, width=200, output_format="PNG")
except FileNotFoundError:
    st.warning("Logo non trouvé ! Vérifie le nom du fichier et son emplacement.")

# --- Fichier de stockage ---
DATA_FILE = "stock.json"

# Initialisation si fichier n'existe pas
if not os.path.exists(DATA_FILE):
    data = {
        "stock": {
            "Twine Cones": {"boites": 100, "fardeaux": 10},
            "Au Lait 50g": {"boites": 200, "fardeaux": 15},
            "Bueno 70g": {"boites": 150, "fardeaux": 20},
            "Pistachio": {"boites": 180, "fardeaux": 25}
        },
        "ventes": []
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
else:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

# --- Numéro de vente automatique ---
num_vente = 1 if len(data["ventes"]) == 0 else data["ventes"][-1]["num"] + 1

# --- Interface principale ---
st.title("💰 Gestion Mini Cones")

today = datetime.today().strftime("%Y-%m-%d")
st.write(f"**Date :** {today}")
st.write(f"**Numéro de vente :** {num_vente}")

# Client et personnel
client = st.text_input("Nom du client")
dettes = st.number_input("Dette du client", min_value=0.0, step=1.0)
operateur = st.text_input("Opérateur")
chauffeur = st.text_input("Chauffeur")
frais = st.number_input("Frais du jour", min_value=0.0, step=1.0)

# --- Produits ---
st.subheader("Produits vendus")
produits = list(data["stock"].keys())
vente_produits = {}
total_ventes = 0

for p in produits:
    st.markdown(f"**{p}**")
    unite = st.selectbox(f"Unité {p}", ["Boîte", "Fardeau"], key=f"{p}_unite")
    qte = st.number_input(f"Quantité vendue {p}", min_value=0, step=1, key=f"{p}_qte")
    prix = st.number_input(f"Prix unitaire {p}", min_value=0.0, step=1.0, key=f"{p}_prix")
    montant = qte * prix
    st.write(f"Montant : {montant}")
    vente_produits[p] = {"unite": unite, "qte": qte, "prix": prix, "montant": montant}
    total_ventes += montant

# --- Calcul caisse ---
caisse = total_ventes - dettes - frais
st.subheader("Résumé du jour")
st.write(f"Total ventes : {total_ventes}")
st.write(f"Dettes : {dettes}")
st.write(f"Frais : {frais}")
st.write(f"💵 Caisse finale : {caisse}")

# --- Enregistrer la vente ---
if st.button("Enregistrer la vente"):
    # Mise à jour du stock
    for p in produits:
        if vente_produits[p]["unite"] == "Boîte":
            data["stock"][p]["boites"] -= vente_produits[p]["qte"]
        else:
            data["stock"][p]["fardeaux"] -= vente_produits[p]["qte"]

    # Enregistrement
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

# --- Affichage stock actuel ---
st.subheader("📦 Stock actuel")
for p, q in data["stock"].items():
    st.write(f"{p} : {q['boites']} boîtes, {q['fardeaux']} fardeaux")

# --- Ajouter au stock ---
st.subheader("Ajouter au stock")
for p in produits:
    ajout_boites = st.number_input(f"{p} - Boîtes à ajouter", min_value=0, step=1, key=f"{p}_ajout_boites")
    ajout_fardeaux = st.number_input(f"{p} - Fardeaux à ajouter", min_value=0, step=1, key=f"{p}_ajout_fardeaux")
    if st.button(f"Mettre à jour {p}"):
        data["stock"][p]["boites"] += ajout_boites
        data["stock"][p]["fardeaux"] += ajout_fardeaux
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)
        st.success(f"Stock de {p} mis à jour !")

# --- Historique des ventes ---
st.subheader("📝 Historique des ventes")
for v in data["ventes"]:
    st.markdown(f"**Vente {v['num']} - {v['date']} - Client : {v['client']}**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button(f"Supprimer {v['num']}"):
            # Retour du stock avant suppression
            for prod, info in v["produits"].items():
                if info["unite"] == "Boîte":
                    data["stock"][prod]["boites"] += info["qte"]
                else:
                    data["stock"][prod]["fardeaux"] += info["qte"]
            data["ventes"] = [x for x in data["ventes"] if x["num"] != v["num"]]
            with open(DATA_FILE, "w") as f:
                json.dump(data, f, indent=4)
            st.experimental_rerun()
    with col2:
        if st.button(f"Modifier {v['num']}"):
            st.session_state.modif_vente = v["num"]
            for prod, info in v["produits"].items():
                qte_modif = st.number_input(f"{prod} ({info['unite']})", value=info["qte"], step=1, key=f"mod_{v['num']}_{prod}")
                info["qte"] = qte_modif
            if st.button(f"Valider modification {v['num']}"):
                # Retour du stock initial
                for prod, info in v["produits"].items():
                    if info["unite"] == "Boîte":
                        data["stock"][prod]["boites"] -= info["qte"]
                    else:
                        data["stock"][prod]["fardeaux"] -= info["qte"]
                # Sauvegarde
                with open(DATA_FILE, "w") as f:
                    json.dump(data, f, indent=4)
                st.success(f"Vente {v['num']} modifiée !")
                st.experimental_rerun()
