import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from fpdf import FPDF
from io import BytesIO

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
        revendeur = st.text_input("Revendeur")
        prix_revendeur = st.number_input("Charge Revendeur (DA)", min_value=0.0, key="charge_rev")
    with col2:
        chauffeur = st.text_input("Chauffeur")
        prix_chauffeur = st.number_input("Charge Chauffeur (DA)", min_value=0.0, key="charge_chauffeur")

    charge_van = st.number_input("Charge Van (DA)", min_value=0.0, key="charge_van")
    autres = st.number_input("Autres charges (DA)", min_value=0.0, key="charge_autres")
    total_charges = prix_revendeur + prix_chauffeur + charge_van + autres
    st.info(f"🔸 Total Charges : **{total_charges} DA**")

    st.subheader("🧃 Produits")
    total_montant = 0
    vente_produits = {}

    for produit, info in data["stock"].items():
        st.markdown(f"### {produit}")
        colA, colB = st.columns(2)
        qte = colB.number_input(f"Quantité", min_value=0, step=1, key=f"qte_{produit}")
        prix_vente = info["prix_vente"]
        montant = qte * prix_vente
        total_montant += montant
        vente_produits[produit] = {"qte":qte,"prix_vente":prix_vente,"prix_achat":info["prix_achat"],"montant":montant}

    st.subheader("📊 Résultat")
    st.write(f"💰 Total ventes : **{total_montant} DA**")
    benefice = total_montant - total_charges
    st.success(f"🟢 Bénéfice : **{benefice} DA**")

    if st.button("Enregistrer la commande"):
        vente = {
            "num": num,
            "date": date,
            "client": client,
            "revendeur": revendeur,
            "chauffeur": chauffeur,
            "charges": total_charges,
            "produits": vente_produits,
            "benefice": benefice
        }
        data["ventes"].append(vente)
        save_data(data)
        st.success("Commande enregistrée ✅")
        st.experimental_rerun()

# ------------------------------
# PAGE STOCK
# ------------------------------
elif page == "Stock":
    st.title("📦 Gestion du Stock")
    for produit, info in data["stock"].items():
        st.markdown(f"### {produit}")
        col1, col2, col3 = st.columns(3)
        with col1:
            info["boites"] = st.number_input("Quantité", min_value=0, value=info["boites"], key=f"stock_qte_{produit}")
        with col2:
            info["prix_achat"] = st.number_input("Prix Achat", min_value=0.0, value=info["prix_achat"], key=f"stock_achat_{produit}")
        with col3:
            info["prix_vente"] = st.number_input("Prix Vente", min_value=0.0, value=info["prix_vente"], key=f"stock_vente_{produit}")
    if st.button("Mettre à jour le stock"):
        save_data(data)
        st.success("Stock mis à jour ✅")

# ------------------------------
# PAGE HISTORIQUE
# ------------------------------
elif page == "Historique":
    st.title("📜 Historique des ventes")
    ventes_df = pd.DataFrame(data["ventes"])
    if not ventes_df.empty:
        st.dataframe(ventes_df)
        
        # Modifier une vente
        st.subheader("✏️ Modifier une vente")
        num_mod = st.number_input("Numéro de la vente à modifier", min_value=1, max_value=len(data["ventes"]), step=1)
        if st.button("Modifier la vente sélectionnée"):
            st.write("Fonction modification en cours de développement")

        # Supprimer une vente
        st.subheader("🗑 Supprimer une vente")
        num_del = st.number_input("Numéro de la vente à supprimer", min_value=1, max_value=len(data["ventes"]), step=1, key="del_vente")
        if st.button("Supprimer la vente"):
            del data["ventes"][num_del-1]
            save_data(data)
            st.success("Vente supprimée ✅")
            st.experimental_rerun()
    else:
        st.info("Aucune vente enregistrée.")

# ------------------------------
# EXPORT PDF
# ------------------------------
def export_pdf(ventes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Historique des ventes Mini Cones", ln=True, align="C")
    pdf.ln(10)
    for vente in ventes:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Vente N° {vente['num']} - {vente['date']}", ln=True)
        pdf.set_font("Arial", "", 12)
        for produit, info in vente["produits"].items():
            pdf.cell(0, 6, f"{produit}: {info['qte']} x {info['prix_vente']} = {info['montant']} DA", ln=True)
        pdf.cell(0, 6, f"Charges: {vente['charges']} DA", ln=True)
        pdf.cell(0, 6, f"Bénéfice: {vente['benefice']} DA", ln=True)
        pdf.ln(5)
    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer

if page == "Historique" and len(data["ventes"])>0:
    buffer = export_pdf(data["ventes"])
    st.download_button("⬇️ Télécharger l'historique en PDF", data=buffer, file_name="historique_ventes.pdf", mime="application/pdf")
