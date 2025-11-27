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

```
col1, col2 = st.columns(2)
with col1:
    client = st.text_input("Client")
    revendeur = st.text_input("Revendeur")
with col2:
    chauffeur = st.text_input("Chauffeur")

charge_van = st.number_input("Charge Van (DA)", min_value=0.0, key="charge_van")
autres = st.number_input("Autres charges (DA)", min_value=0.0, key="charge_autres")
total_charges = charge_van + autres
st.info(f"🔸 Total Charges : **{total_charges} DA**")

st.subheader("🧃 Produits")
total_montant = 0
vente_produits = {}

for produit, info in data["stock"].items():
    st.markdown(f"### {produit}")
    qte = st.number_input(f"Quantité de {produit}", min_value=0, step=1, key=f"qte_{produit}")
    prix_achat = info["prix_achat"]
    prix_vente = info["prix_vente"]
    montant = qte * prix_vente
    benefice_produit = qte * (prix_vente - prix_achat)
    total_montant += montant
    vente_produits[produit] = {
        "qte": qte,
        "prix_achat": prix_achat,
        "prix_vente": prix_vente,
        "montant": montant,
        "benefice": benefice_produit
    }

st.subheader("📊 Résultat")
st.write(f"💰 Total ventes : **{total_montant} DA**")
benefice_total = total_montant - total_charges
st.success(f"🟢 Bénéfice total : **{benefice_total} DA**")

if st.button("Enregistrer la commande"):
    vente = {
        "num": num,
        "date": date,
        "client": client,
        "revendeur": revendeur,
        "chauffeur": chauffeur,
        "charges": total_charges,
        "produits": vente_produits
    }
    data["ventes"].append(vente)
    save_data(data)
    st.success("✅ Commande enregistrée")
    st.experimental_rerun()
```

# ------------------------------

# PAGE STOCK

# ------------------------------

elif page == "Stock":
st.title("📦 Stock actuel")
df_stock = pd.DataFrame(data["stock"]).T
st.dataframe(df_stock[["boites","prix_achat","prix_vente"]])

# ------------------------------

# PAGE HISTORIQUE

# ------------------------------

elif page == "Historique":
st.title("📚 Historique des ventes")
for i, vente in enumerate(data["ventes"]):
st.subheader(f"Commande N°{vente['num']} - {vente['date']}")
st.write(f"Client : {vente['client']} | Revendeur : {vente['revendeur']} | Chauffeur : {vente['chauffeur']}")
df = pd.DataFrame(vente["produits"]).T
df["Marge"] = df["benefice"]
st.dataframe(df[["qte","prix_achat","prix_vente","montant","Marge"]])
col1, col2 = st.columns(2)
with col1:
if st.button(f"Modifier {vente['num']}", key=f"modif_{i}"):
st.session_state['modif_index'] = i
for produit, info in vente["produits"].items():
new_qte = st.number_input(f"{produit} (ancienne {info['qte']})", min_value=0, value=info['qte'], key=f"modif_{i}*{produit}")
info["qte"] = new_qte
info["montant"] = new_qte * info["prix_vente"]
info["benefice"] = new_qte * (info["prix_vente"] - info["prix_achat"])
save_data(data)
st.success("✅ Commande modifiée")
st.experimental_rerun()
with col2:
if st.button(f"Supprimer {vente['num']}", key=f"supp*{i}"):
data["ventes"].pop(i)
save_data(data)
st.success("🗑 Commande supprimée")
st.experimental_rerun()

# ------------------------------

# Export PDF de l'historique

# ------------------------------

def export_pdf(ventes):
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(0, 10, "Historique des ventes Mini Cones", ln=True, align="C")
pdf.ln(5)
for vente in ventes:
pdf.cell(0, 8, f"Commande {vente['num']} - {vente['date']}", ln=True)
for produit, info in vente["produits"].items():
pdf.cell(0, 8, f"{produit}: {info['qte']} x {info['prix_vente']} DA (achat {info['prix_achat']} DA) = {info['montant']} DA | Marge {info['benefice']} DA", ln=True)
pdf.ln(2)
pdf_buffer = BytesIO()
pdf.output(pdf_buffer)
pdf_buffer.seek(0)
return pdf_buffer

if st.button("Exporter PDF de l'historique"):
pdf_file = export_pdf(data["ventes"])
st.download_button("⬇ Télécharger PDF", pdf_file, file_name="historique_mini_cones.pdf", mime="application/pdf")
