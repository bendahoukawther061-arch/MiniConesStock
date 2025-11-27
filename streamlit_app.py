import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from fpdf import FPDF

# ------------------------------
# Config Streamlit
# ------------------------------
st.set_page_config(page_title="Mini Cones", page_icon="🍦", layout="wide")

# ------------------------------
# Thème CSS clair
# ------------------------------
page_bg = """
<style>
.stApp {background: linear-gradient(135deg, #ffe6f2 0%, #fff8fd 40%, #f7e6d5 80%);}
.stButton>button {background-color: #b56576 !important; color: white !important; border-radius: 12px !important; height: 3em; font-size: 18px; font-weight: bold;}
.stDownloadButton>button {background-color: #6d6875 !important; color: white !important; border-radius: 10px !important;}
h1,h2,h3,h4 {color: #b56576 !important; font-weight: 800 !important;}
.stButton>button:hover {background-color: #8e4f63 !important; transform: scale(1.05);}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ------------------------------
# Fichier de stockage
# ------------------------------
DATA_FILE = "stock.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "stock": {
                "Twine Cones": {"boites": 0, "prix_achat": 0, "prix_vente": 200},
                "Cones Pistache": {"boites": 0, "prix_achat": 0, "prix_vente": 250},
                "Bueno au Lait": {"boites": 0, "prix_achat": 0, "prix_vente": 220},
                "Crêpes": {"boites": 0, "prix_achat": 0, "prix_vente": 180}
            },
            "ventes": []
        }
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ------------------------------
# Login simple
# ------------------------------
if 'login' not in st.session_state:
    st.session_state['login'] = False

if not st.session_state['login']:
    st.image("logo.png", width=200)
    st.subheader("🔒 Login")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        if username == "bendahou mehdi" and password == "mehdi123":
            st.session_state['login'] = True
            st.success("Connecté ✔")
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect")
    st.stop()

# ------------------------------
# Sidebar
# ------------------------------
st.sidebar.image("logo.png", width=120)
page = st.sidebar.radio("Navigation", ["Commandes", "Stock", "Historique"])

# ------------------------------
# PAGE COMMANDES
# ------------------------------
if page == "Commandes":
    st.image("logo.png", width=150)
    st.title("🧾 Nouvelle Commande")
    num = 1 if len(data["ventes"])==0 else data["ventes"][-1]["num"]+1
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.write(f"**Commande N° {num} — {date}**")

    col1, col2 = st.columns(2)
    with col1:
        client = st.text_input("Client")
    with col2:
        revendeur = st.text_input("Revendeur")

    st.subheader("🧃 Produits")
    total_montant = 0
    vente_produits = {}
    for produit, info in data["stock"].items():
        qte = st.number_input(f"{produit} - Quantité", min_value=0, step=1, key=f"qte_{produit}")
        prix_vente = info["prix_vente"]
        montant = qte * prix_vente
        total_montant += montant
        vente_produits[produit] = {"qte":qte,"prix_vente":prix_vente,"montant":montant}

    st.subheader("📊 Résultat")
    st.write(f"💰 Total ventes : **{total_montant} DA**")

    if st.button("Enregistrer la commande"):
        vente = {
            "num": num,
            "date": date,
            "client": client,
            "revendeur": revendeur,
            "produits": vente_produits,
            "total": total_montant
        }
        data["ventes"].append(vente)
        save_data(data)
        st.success(f"Commande N° {num} enregistrée ✔")

        # Export PDF directement
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, f"Commande N° {vente['num']}", ln=True)
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 10, f"Client: {vente['client']}  Date: {vente['date']}", ln=True)
        pdf.ln(5)
        for produit, info in vente["produits"].items():
            pdf.cell(0, 8, f"{produit}: {info['qte']} x {info['prix_vente']} DA = {info['montant']} DA", ln=True)
        pdf.cell(0, 8, f"Total: {vente['total']} DA", ln=True)

        pdf_bytes = pdf.output(dest='S').encode('latin1')
        st.download_button("📄 Télécharger PDF", pdf_bytes, file_name=f"commande_{num}.pdf", mime="application/pdf")

# ------------------------------
# PAGE STOCK
# ------------------------------
if page == "Stock":
    st.title("📦 Stock actuel")
    for produit, info in data["stock"].items():
        col1, col2, col3 = st.columns([2,2,2])
        with col1:
            st.write(produit)
        with col2:
            new_qte = st.number_input(f"Quantité {produit}", value=info["boites"], key=f"stock_{produit}")
        with col3:
            new_prix = st.number_input(f"Prix vente {produit}", value=info["prix_vente"], key=f"prix_{produit}")
        if st.button(f"Mettre à jour {produit}"):
            info["boites"] = new_qte
            info["prix_vente"] = new_prix
            save_data(data)
            st.success(f"{produit} mis à jour ✔")

# ------------------------------
# PAGE HISTORIQUE
# ------------------------------
if page == "Historique":
    st.title("📜 Historique des ventes")
    if len(data["ventes"]) == 0:
        st.info("Aucune vente enregistrée.")
    else:
        for i, vente in enumerate(data["ventes"]):
            with st.expander(f"Commande N° {vente['num']} - {vente['client']} ({vente['date']})"):
                df = pd.DataFrame(vente["produits"]).T
                st.dataframe(df)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button(f"Modifier {vente['num']}", key=f"mod_{i}"):
                        st.session_state['edit'] = i
                        st.experimental_rerun()
                with col2:
                    if st.button(f"Supprimer {vente['num']}", key=f"sup_{i}"):
                        del data["ventes"][i]
                        save_data(data)
                        st.experimental_rerun()
