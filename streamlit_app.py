import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd

# -------------------------------------------------------
# CONFIG
# -------------------------------------------------------
st.set_page_config(page_title="Mini Cones", page_icon="🍦")
PASSWORD = "mehdi123"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("BENDAHOU Mehdi")
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("Valider"):
        if pwd.lower().strip() == PASSWORD:
            st.session_state.auth = True
            st.success("Connecté ✔")
        else:
            st.error("Mot de passe incorrect ❌")
    st.stop()

# -------------------------------------------------------
# DATA
# -------------------------------------------------------
DATA_FILE = "stock.json"
DEFAULT_DATA = {
    "stock": {
        "Twine Cones": {"boites": 50, "achat": 10, "vente": 15},
        "Pistache": {"boites": 60, "achat": 12, "vente": 18},
        "Bueno": {"boites": 70, "achat": 13, "vente": 20},
        "Au Lait": {"boites": 80, "achat": 11, "vente": 17},
        "Crêpes": {"boites": 40, "achat": 8, "vente": 12}
    },
    "commandes": []
}

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump(DEFAULT_DATA, f, indent=4)

with open(DATA_FILE, "r") as f:
    data = json.load(f)

def save():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# -------------------------------------------------------
# MENU
# -------------------------------------------------------
menu = st.sidebar.selectbox("Menu", ["Commande", "Stock", "Historique"])

# -------------------------------------------------------
# PAGE 1 : COMMANDE
# -------------------------------------------------------
if menu == "Commande":
    st.title("🧾 Nouvelle commande")

    num = 1 if len(data["commandes"]) == 0 else data["commandes"][-1]["num"] + 1
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    st.write(f"**N° commande :** {num}")
    st.write(f"**Date & Heure :** {date}")

    client = st.text_input("Client")
    revendeur = st.text_input("Revendeur")
    prix_revendeur = st.number_input("Prix revendeur", min_value=0.0, value=0.0)
    chauffeur = st.text_input("Chauffeur")
    prix_chauffeur = st.number_input("Prix chauffeur", min_value=0.0, value=0.0)
    autres_charges = st.number_input("Autres charges", min_value=0.0, value=0.0)

    total_charges = prix_revendeur + prix_chauffeur + autres_charges
    st.info(f"Total charges = {total_charges} DA")

    st.subheader("Produits vendus")
    produits_vente = {}
    total_montant = 0
    total_marge = 0

    for p, s in data["stock"].items():
        q = st.number_input(f"Quantité vendue – {p}", min_value=0, max_value=s["boites"], step=1)
        montant = q * s["vente"]
        marge = q * (s["vente"] - s["achat"])

        produits_vente[p] = {
            "qte": q,
            "prix_achat": s["achat"],
            "prix_vente": s["vente"],
            "montant": montant,
            "marge": marge
        }

        total_montant += montant
        total_marge += marge

    st.subheader("Résultats")
    st.write(f"Montant total : **{total_montant} DA**")
    st.write(f"Marge brute : **{total_marge} DA**")

    benefice_net = total_marge - total_charges
    st.success(f"Bénéfice net : **{benefice_net} DA**")

    if st.button("Enregistrer"):
        for p, info in produits_vente.items():
            data["stock"][p]["boites"] -= info["qte"]

        commande = {
            "num": num,
            "date": date,
            "client": client,
            "revendeur": revendeur,
            "prix_revendeur": prix_revendeur,
            "chauffeur": chauffeur,
            "prix_chauffeur": prix_chauffeur,
            "autres_charges": autres_charges,
            "total_charges": total_charges,
            "produits": produits_vente,
            "montant_total": total_montant,
            "marge_brute": total_marge,
            "benefice_net": benefice_net
        }

        data["commandes"].append(commande)
        save()
        st.success("Commande enregistrée ✔")
        st.experimental_rerun()

# -------------------------------------------------------
# PAGE 2 : STOCK
# -------------------------------------------------------
elif menu == "Stock":
    st.title("📦 Stock")

    for p, s in data["stock"].items():
        st.write(f"**{p}** — {s['boites']} boîtes | Achat : {s['achat']} | Vente : {s['vente']}")

    st.subheader("Modifier un produit")
    prod = st.selectbox("Produit", list(data["stock"].keys()))

    new_qte = st.number_input("Nouvelle quantité", min_value=0, value=data["stock"][prod]["boites"])
    new_achat = st.number_input("Prix d'achat", min_value=0.0, value=float(data["stock"][prod]["achat"]))
    new_vente = st.number_input("Prix de vente", min_value=0.0, value=float(data["stock"][prod]["vente"]))

    if st.button("Mettre à jour"):
        data["stock"][prod]["boites"] = new_qte
        data["stock"][prod]["achat"] = new_achat
        data["stock"][prod]["vente"] = new_vente
        save()
        st.success("Stock mis à jour ✔")
        st.experimental_rerun()

# -------------------------------------------------------
# PAGE 3 : HISTORIQUE
# -------------------------------------------------------
elif menu == "Historique":
    st.title("📜 Historique des commandes")

    if len(data["commandes"]) == 0:
        st.info("Aucune commande enregistrée.")
        st.stop()

    rows = []
    for c in data["commandes"]:
        rows.append({
            "num": c["num"],
            "date": c["date"],
            "client": c["client"],
            "montant": c["montant_total"],
            "charges": c["total_charges"],
            "bénéfice": c["benefice_net"]
        })

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True)

    choix = st.selectbox("N° commande", df["num"])
    col1, col2 = st.columns(2)

    with col1:
        if st.button("❌ Supprimer"):
            data["commandes"] = [c for c in data["commandes"] if c["num"] != choix]
            save()
            st.success("Supprimée ✔")
            st.experimental_rerun()

    with col2:
        st.warning("Modification à venir…")
