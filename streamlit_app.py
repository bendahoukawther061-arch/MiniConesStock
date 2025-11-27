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
# CSS
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
    st.title("🧾 Nouvelle Commande")
    num = 1 if len(data["ventes"])==0 else data["ventes"][-1]["num"]+1
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.write(f"**Commande N° {num} — {date}**")

    col1, col2 = st.columns(2)
    with col1:
        client = st.text_input("Client")
    with col2:
        chauffeur = st.text_input("Chauffeur")

    st.subheader("🧃 Produits")
    total_montant = 0
    vente_produits = {}

    for produit, info in data["stock"].items():
        st.markdown(f"### {produit}")
        qte = st.number_input(f"Quantité {produit}", min_value=0, step=1, key=f"qte_{produit}")
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
            "chauffeur": chauffeur,
            "produits": vente_produits,
            "total": total_montant
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
        col1, col2 = st.columns(2)
        with col1:
            data["stock"][produit]["boites"] = st.number_input("Boîtes", value=info["boites"], key=f"boites_{produit}")
        with col2:
            data["stock"][produit]["prix_vente"] = st.number_input("Prix Vente (DA)", value=info["prix_vente"], key=f"prix_vente_{produit}")
    if st.button("Enregistrer Stock"):
        save_data(data)
        st.success("Stock mis à jour ✅")

# ------------------------------
# PAGE HISTORIQUE
# ------------------------------
elif page == "Historique":
    st.title("📜 Historique des Ventes")
    for idx, vente in enumerate(data["ventes"]):
        st.markdown(f"**Commande N° {vente['num']} — {vente['date']} — Client : {vente['client']}**")
        hist_data = []
        for produit, info in vente["produits"].items():
            hist_data.append({
                "Produit": produit,
                "Quantité": info["qte"],
                "Prix Vente (DA)": info["prix_vente"],
                "Montant (DA)": info["montant"]
            })
        df = pd.DataFrame(hist_data)
        st.dataframe(df)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Modifier", key=f"mod_{idx}"):
                for produit, info in vente["produits"].items():
                    new_qte = st.number_input(f"Quantité {produit}", value=info["qte"], key=f"edit_{idx}_{produit}")
                    vente["produits"][produit]["qte"] = new_qte
                    vente["produits"][produit]["montant"] = new_qte * info["prix_vente"]
                vente["total"] = sum([p["montant"] for p in vente["produits"].values()])
                save_data(data)
                st.success("Commande modifiée ✅")
                st.experimental_rerun()
        with col2:
            if st.button("Supprimer", key=f"del_{idx}"):
                data["ventes"].pop(idx)
                save_data(data)
                st.success("Commande supprimée ✅")
                st.experimental_rerun()
        with col3:
            # Export PDF
            pdf_buffer = BytesIO()
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 16)
            pdf.cell(0, 10, f"Commande N° {vente['num']}", ln=True)
            pdf.set_font("Arial", '', 12)
            pdf.cell(0, 10, f"Client: {vente['client']}  Date: {vente['date']}", ln=True)
            pdf.ln(5)
            pdf.set_font("Arial", '', 12)
            for produit, info in vente["produits"].items():
                pdf.cell(0, 8, f"{produit}: {info['qte']} x {info['prix_vente']} DA = {info['montant']} DA", ln=True)
            pdf.cell(0, 8, f"Total: {vente['total']} DA", ln=True)
            pdf.output(pdf_buffer)
            st.download_button("📄 Export PDF", pdf_buffer.getvalue(), file_name=f"commande_{vente['num']}.pdf", mime="application/pdf")
