import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ------------------------------

# Config Streamlit

# ------------------------------

st.set_page_config(page_title="Mini Cones", page_icon="🍦", layout="wide")

# ------------------------------

# Thème CSS clair + animations

# ------------------------------

page_bg = """

<style>
.stApp {
    background: linear-gradient(135deg, #ffe6f2 0%, #fff8fd 40%, #f7e6d5 80%);
    transition: all 0.5s ease;
}

.stButton>button {
    background-color: #b56576 !important;
    color: white !important;
    border-radius: 12px !important;
    height: 3em;
    font-size: 18px;
    font-weight: bold;
    transition: all 0.3s ease;
}

.stDownloadButton>button {
    background-color: #6d6875 !important;
    color: white !important;
    border-radius: 10px !important;
}

h1,h2,h3,h4 {
    color: #b56576 !important;
    font-weight: 800 !important;
}

.stButton>button:hover {
    background-color: #8e4f63 !important;
    transform: scale(1.05);
}

.fade-in {
    animation: fadein 1s;
}

@keyframes fadein {
    from {opacity:0;}
    to {opacity:1;}
}
</style>

"""
st.markdown(page_bg, unsafe_allow_html=True)

# ------------------------------

# Fichier stockage

# ------------------------------

DATA_FILE = "stock.json"

def load_data():
if not os.path.exists(DATA_FILE):
return {
"stock": {
"Twine Cones": {"boites": 0, "prix_achat": 0, "prix_vente": 0},
"Cones Pistache": {"boites": 0, "prix_achat": 0, "prix_vente": 0},
"Au Lait": {"boites": 0, "prix_achat": 0, "prix_vente": 0},
"Bueno": {"boites": 0, "prix_achat": 0, "prix_vente": 0},
"Crêpes": {"boites": 0, "prix_achat": 0, "prix_vente": 0}
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
    prix_revendeur = st.number_input("Charge Revendeur (DA)", min_value=0.0)
with col2:
    chauffeur = st.text_input("Chauffeur")
    prix_chauffeur = st.number_input("Charge Chauffeur (DA)", min_value=0.0)

charge_van = st.number_input("Charge Van (DA)", min_value=0.0)
autres = st.number_input("Autres charges (DA)", min_value=0.0)
total_charges = prix_revendeur + prix_chauffeur + charge_van + autres
st.info(f"🔸 Total Charges : **{total_charges} DA**")

st.subheader("🧃 Produits")
total_montant = 0
vente_produits = {}

for produit, info in data["stock"].items():
    st.markdown(f"### {produit}")
    colA, colB, colC = st.columns(3)
    type_qte = "Box"
    if produit=="Twine Cones":
        type_qte = colA.selectbox(f"Type pour {produit}", ["Box","Fardeau"])
    qte = colB.number_input(f"Quantité", min_value=0, step=1)
    if produit=="Twine Cones" and type_qte=="Fardeau":
        qte *= 6
    prix_vente = colC.number_input(f"Prix Vente unité (DA)", value=float(info["prix_vente"]))
    montant = qte * prix_vente
    total_montant += montant
    vente_produits[produit] = {"qte":qte,"prix_vente":prix_vente,"prix_achat":info["prix_achat"],"montant":montant}

st.subheader("📊 Résultat")
st.write(f"💰 Total ventes : **{total_montant} DA**")
benefice = total_montant - total_charges
st.success(f"🟢 Bénéfice : **{benefice} DA**")

if st.button("Enregistrer la commande"):
    vente = {"num":num,"date":date,"client":client,"revendeur":revendeur,"chauffeur":chauffeur,
             "charges":total_charges,"produits":vente_produits,"total":total_montant,"benefice":benefice}
    data["ventes"].append(vente)
    save_data(data)
    st.success("Commande enregistrée ✔")
    st.experimental_rerun()

if len(data["ventes"])>0:
    df = pd.DataFrame([{
        "Num": v["num"], "Date": v["date"], "Client": v["client"],
        "Total": v["total"], "Charges": v["charges"], "Bénéfice": v["benefice"]
    } for v in data["ventes"]])
    st.download_button(
        "📥 Export PDF tableau",
        df.to_csv(index=False).encode("utf-8"),
        "historique.csv",
        "text/csv"
    )
```

# ------------------------------

# PAGE STOCK

# ------------------------------

elif page == "Stock":
st.image("logo.png", width=150)
st.title("📦 Gestion du Stock")
st.subheader("Stock actuel")
for p, info in data["stock"].items():
st.write(f"**{p}** : {info['boites']} box — Achat {info['prix_achat']} DA — Vente {info['prix_vente']} DA")
st.markdown("---")
st.subheader("➕ Modifier / Ajouter quantité")
prod = st.selectbox("Produit", list(data["stock"].keys()))
new_qte = st.number_input("Quantité à ajouter", min_value=0)
prixA = st.number_input("Prix achat (DA)", value=float(data["stock"][prod]["prix_achat"]))
prixV = st.number_input("Prix vente (DA)", value=float(data["stock"][prod]["prix_vente"]))
if st.button("Mettre à jour le stock"):
data["stock"][prod]["boites"] += new_qte
data["stock"][prod]["prix_achat"] = prixA
data["stock"][prod]["prix_vente"] = prixV
save_data(data)
st.success("Stock mis à jour ✔")
st.experimental_rerun()

# ------------------------------

# PAGE HISTORIQUE

# ------------------------------

elif page == "Historique":
st.image("logo.png", width=150)
st.title("📜 Historique des Commandes")
if len(data["ventes"])==0:
st.info("Aucune commande.")
else:
df = pd.DataFrame([{
"Num": v["num"], "Date": v["date"], "Client": v["client"],
"Total": v["total"], "Charges": v["charges"], "Bénéfice": v["benefice"]
} for v in data["ventes"]])
st.dataframe(df)
st.download_button(
"📥 Export PDF tableau",
df.to_csv(index=False).encode("utf-8"),
"historique.csv",
"text/csv"
)
