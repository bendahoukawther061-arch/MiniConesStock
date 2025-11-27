import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
from fpdf import FPDF
from io import BytesIO

# ------------------------------
# Config Streamlit
# ------------------------------
st.set_page_config(page_title="Mini Cones", page_icon="🍦", layout="wide")

# ------------------------------
# CSS
# ------------------------------
page_bg = """
<style>
.stApp {background: linear-gradient(135deg, #ffe6f2, #fff8fd, #f7e6d5);}
.stButton>button {background-color: #b56576 !important; color: white !important; border-radius: 12px !important; font-size: 18px;}
.stDownloadButton>button {background-color: #6d6875 !important; color: white !important; border-radius: 10px !important;}
h1,h2,h3,h4 {color: #b56576 !important; font-weight: 800 !important;}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ------------------------------
# Fichiers
# ------------------------------
DATA_FILE = "stock.json"
AUTO_DIR = "historique_auto"

if not os.path.exists(AUTO_DIR):
    os.makedirs(AUTO_DIR)

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "stock": {
                "Twine Cones": {"boites": 0, "prix_achat": 0, "prix_vente": 200},
                "Cones Pistache": {"boites": 0, "prix_achat": 0, "prix_vente": 250},
                "Bueno au Lait": {"boites": 0, "prix_achat": 0, "prix_vente": 220},
                "Crêpes": {"boites": 0, "prix_achat": 0, "prix_vente": 180}
            },
            "ventes": [],
            "last_export": ""
        }
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ------------------------------
# Export PDF (normal + auto)
# ------------------------------
def generate_pdf(ventes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Historique des ventes", ln=1, align='C')
    pdf.set_font("Arial", '', 12)

    for vente in ventes:
        pdf.cell(0, 10, f"Commande N° {vente['num']} — {vente['date']}", ln=1)
        pdf.cell(0, 8, f"Client: {vente['client']} | Revendeur: {vente['revendeur']} | Chauffeur: {vente['chauffeur']}", ln=1)
        pdf.cell(0, 8, f"Charges totales: {vente['charges']['total']} DA", ln=1)
        pdf.ln(3)
        for prod, info in vente["produits"].items():
            pdf.cell(0, 6, f"{prod}: Qte={info['qte']} | Achat={info['prix_achat']} | Vente={info['prix_vente']} | Montant={info['montant']}", ln=1)
        pdf.ln(2)

    return pdf

def export_pdf_download():
    pdf = generate_pdf(data["ventes"])
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

def auto_export_pdf():
    today = str(date.today())
    if data.get("last_export") != today:
        filename = f"{AUTO_DIR}/historique_{today}.pdf"
        pdf = generate_pdf(data["ventes"])
        pdf.output(filename)
        data["last_export"] = today
        save_data(data)

# ------------------------------
# AUTO SAVE À MINUIT
# ------------------------------
auto_export_pdf()

# ------------------------------
# Login
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
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    st.write(f"**Commande N° {num} — {date_now}**")

    col1, col2 = st.columns(2)
    with col1:
        client = st.text_input("Client")
        revendeur = st.text_input("Revendeur")
        prix_rev = st.number_input("Charge Revendeur (DA)", min_value=0.0)
    with col2:
        chauffeur = st.text_input("Chauffeur")
        prix_chauff = st.number_input("Charge Chauffeur (DA)", min_value=0.0)

    charge_van = st.number_input("Charge Van (DA)", min_value=0.0)
    autres = st.number_input("Autres charges (DA)", min_value=0.0)

    total_charges = prix_rev + prix_chauff + charge_van + autres
    st.info(f"🔸 Total Charges : **{total_charges} DA**")

    # Produits
    st.subheader("🧃 Produits")
    total_ventes = 0
    vente_produits = {}

    for produit, info in data["stock"].items():
        st.markdown(f"### {produit}")
        colA, colB = st.columns(2)

        type_qte = "Box"
        if produit == "Twine Cones":
            type_qte = colA.selectbox(f"Type", ["Box", "Fardeau"])

        qte = colB.number_input("Quantité", min_value=0)

        if produit == "Twine Cones" and type_qte == "Fardeau":
            qte *= 6

        prix_vente = info["prix_vente"]
        prix_achat = info["prix_achat"]
        montant = qte * prix_vente
        total_ventes += montant

        vente_produits[produit] = {
            "qte": qte,
            "prix_vente": prix_vente,
            "prix_achat": prix_achat,
            "montant": montant
        }

    st.subheader("📊 Résultat")
    st.write(f"💰 Total ventes : **{total_ventes} DA**")
    benefice = total_ventes - total_charges
    st.success(f"🟢 Bénéfice : **{benefice} DA**")

    if st.button("Enregistrer la commande"):
        vente = {
            "num": num,
            "date": date_now,
            "client": client,
            "revendeur": revendeur,
            "chauffeur": chauffeur,
            "charges": {
                "revendeur": prix_rev,
                "chauffeur": prix_chauff,
                "van": charge_van,
                "autres": autres,
                "total": total_charges
            },
            "produits": vente_produits,
            "total_ventes": total_ventes,
            "benefice": benefice
        }

        data["ventes"].append(vente)
        save_data(data)
        st.success("Commande enregistrée ✔")
        st.experimental_rerun()

# ------------------------------
# PAGE STOCK
# ------------------------------
if page == "Stock":
    st.title("📦 Stock")
    for produit, info in data["stock"].items():
        st.subheader(produit)
        col1, col2 = st.columns(2)
        with col1:
            boites = st.number_input("Boîtes", value=info["boites"], min_value=0)
        with col2:
            achat = st.number_input("Prix achat", value=info["prix_achat"], min_value=0)
            vente = st.number_input("Prix vente", value=info["prix_vente"], min_value=0)

        data["stock"][produit]["boites"] = boites
        data["stock"][produit]["prix_achat"] = achat
        data["stock"][produit]["prix_vente"] = vente

    if st.button("Mettre à jour"):
        save_data(data)
        st.success("Stock mis à jour ✔")

# ------------------------------
# PAGE HISTORIQUE
# ------------------------------
if page == "Historique":
    st.title("📜 Historique des ventes")

    for vente in data["ventes"]:
        st.subheader(f"Commande N° {vente['num']} — {vente['date']}")

        st.write(f"Client : **{vente['client']}**")
        st.write(f"Revendeur : **{vente['revendeur']}**")
        st.write(f"Chauffeur : **{vente['chauffeur']}**")
        st.write(f"Charges totales : **{vente['charges']['total']} DA**")

        df = pd.DataFrame(vente["produits"]).T
        st.dataframe(df)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Modifier", key=f"mod_{vente['num']}"):
                st.warning("La modification arrive bientôt.")
        with col2:
            if st.button("Supprimer", key=f"sup_{vente['num']}"):
                data["ventes"].remove(vente)
                save_data(data)
                st.success("Commande supprimée ✔")
                st.experimental_rerun()

# ------------------------------
# DOWNLOAD PDF
# ------------------------------
st.sidebar.download_button(
    "📄 Télécharger PDF",
    data=export_pdf_download(),
    file_name="historique_ventes.pdf",
    mime="application/pdf"
)
