import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from fpdf import FPDF
from io import BytesIO

# ------------------------------------------------
# CONFIG
# ------------------------------------------------
st.set_page_config(page_title="Mini Cones", page_icon="🍦", layout="wide")

page_bg = """
<style>
.stApp {background: linear-gradient(135deg, #ffe6f2 0%, #fff8fd 40%, #f7e6d5 80%);}
.stButton>button {background-color: #b56576 !important; color: white !important; border-radius: 12px !important; font-size: 18px;}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

DATA_FILE = "stock.json"

# ------------------------------------------------
# LOAD & SAVE
# ------------------------------------------------
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

# ------------------------------------------------
# LOGIN
# ------------------------------------------------
if 'login' not in st.session_state:
    st.session_state['login'] = False

if not st.session_state['login']:
    st.image("logo.png", width=200)
    st.subheader("🔒 Login")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        if username == "bendahou" and password == "mehdi123":
            st.session_state['login'] = True
            st.experimental_rerun()
        else:
            st.error("Identifiants incorrects")
    st.stop()

# ------------------------------------------------
# FONCTION EXPORT PDF
# ------------------------------------------------
def export_pdf(ventes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Historique des ventes", ln=1, align="C")

    for v in ventes:
        pdf.cell(200, 8, txt=f"Date : {v['date']} | Total : {v['total']} DA", ln=1)
        for p, infos in v["produits"].items():
            pdf.cell(200, 8, txt=f" - {p}: {infos['quantite']} boites (achat {infos['prix_achat']} / vente {infos['prix_vente']})", ln=1)

    buffer = BytesIO()
    pdf.output(buffer, "F")
    buffer.seek(0)
    return buffer

# ------------------------------------------------
# PAGE PRINCIPALE
# ------------------------------------------------
st.title("🍦 Mini Cones – Stock & Ventes")

menu = st.sidebar.radio("Navigation", ["Stock", "Vente", "Historique"])

# ------------------------------------------------
# PAGE STOCK
# ------------------------------------------------
if menu == "Stock":
    st.header("📦 Gestion du Stock")

    for produit, infos in data["stock"].items():
        st.subheader(produit)
        colA, colB, colC = st.columns(3)

        nv_boites = colA.number_input(
            f"Boîtes en stock ({produit})",
            min_value=0,
            value=infos["boites"],
            key=f"stk_{produit}"
        )

        prix_achat = colB.number_input(
            f"Prix d'achat ({produit})",
            min_value=0,
            value=infos["prix_achat"],
            key=f"pa_{produit}"
        )

        prix_vente = colC.number_input(
            f"Prix de vente ({produit})",
            min_value=0,
            value=infos["prix_vente"],
            key=f"pv_{produit}"
        )

        data["stock"][produit]["boites"] = nv_boites
        data["stock"][produit]["prix_achat"] = prix_achat
        data["stock"][produit]["prix_vente"] = prix_vente

    if st.button("💾 Enregistrer le stock"):
        save_data(data)
        st.success("Stock mis à jour !")

# ------------------------------------------------
# PAGE VENTE
# ------------------------------------------------
if menu == "Vente":
    st.header("🛒 Nouvelle Vente")

    vente = {"produits": {}, "total": 0}

    for produit, infos in data["stock"].items():
        st.subheader(produit)
        colA, colB = st.columns(2)

        qte = colA.number_input(
            f"Quantité vendue ({produit})",
            min_value=0,
            key=f"qte_{produit}"
        )

        if qte > 0:
            if qte > infos["boites"]:
                st.error(f"Stock insuffisant pour {produit}")
            else:
                vente["produits"][produit] = {
                    "quantite": qte,
                    "prix_achat": infos["prix_achat"],
                    "prix_vente": infos["prix_vente"]
                }
                vente["total"] += qte * infos["prix_vente"]

    if st.button("Valider la vente"):
        if vente["produits"]:
            vente["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            data["ventes"].append(vente)

            for p, infos in vente["produits"].items():
                data["stock"][p]["boites"] -= infos["quantite"]

            save_data(data)
            st.success("Vente enregistrée !")

# ------------------------------------------------
# PAGE HISTORIQUE
# ------------------------------------------------
if menu == "Historique":
    st.header("📜 Historique des ventes")

    if data["ventes"]:
        for i, vente in enumerate(data["ventes"]):
            with st.expander(f"Vente du {vente['date']} - Total {vente['total']} DA"):
                st.write(vente["produits"])

                col1, col2 = st.columns(2)

                if col1.button("📝 Modifier", key=f"edit_{i}"):
                    st.warning("La modification sera ajoutée bientôt.")

                if col2.button("❌ Supprimer", key=f"del_{i}"):
                    data["ventes"].pop(i)
                    save_data(data)
                    st.experimental_rerun()

        if st.button("📄 Télécharger PDF"):
            pdf_file = export_pdf(data["ventes"])
            st.download_button("Télécharger", pdf_file, "historique.pdf")

    else:
        st.info("Aucune vente enregistrée pour le moment.")
