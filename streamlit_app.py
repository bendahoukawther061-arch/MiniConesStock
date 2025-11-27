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
                "Crêpes": {"boites": 0, "prix_achat": 0, "prix_vente": 180},
                "Au Lait": {"boites": 0, "prix_achat": 0, "prix_vente": 230}
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
    
    num = 1 if len(data["ventes"]) == 0 else data["ventes"][-1]["num"] + 1
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

    total_frais = prix_revendeur + prix_chauffeur + charge_van + autres
    st.info(f"🔸 Total des frais : **{total_frais} DA**")

    st.subheader("🧃 Produits")
    total_ventes = 0
    total_cout = 0
    vente_produits = {}

    for produit, info in data["stock"].items():
        st.markdown(f"### {produit}")
        colA, colB = st.columns(2)
        qte = colB.number_input(f"Quantité {produit}", min_value=0, step=1, key=f"qte_{produit}")
        prix_vente = info["prix_vente"]
        prix_achat = info["prix_achat"]
        montant = qte * prix_vente
        cout = qte * prix_achat
        total_ventes += montant
        total_cout += cout
        vente_produits[produit] = {
            "qte": qte,
            "prix_vente": prix_vente,
            "prix_achat": prix_achat,
            "montant": montant,
            "cout": cout
        }

    st.subheader("📊 Résultats")
    st.write(f"💰 Total ventes : **{total_ventes} DA**")
    st.write(f"💸 Total frais : **{total_frais} DA**")
    st.write(f"🧾 Coût des produits : **{total_cout} DA**")

    benefice = total_ventes - total_frais - total_cout
    st.success(f"🟢 Bénéfice net : **{benefice} DA**")

    if st.button("Enregistrer la commande"):
        vente = {
            "num": num,
            "date": date,
            "client": client,
            "revendeur": revendeur,
            "chauffeur": chauffeur,
            "frais": {
                "revendeur": prix_revendeur,
                "chauffeur": prix_chauffeur,
                "van": charge_van,
                "autres": autres,
                "total_frais": total_frais
            },
            "produits": vente_produits,
            "total_ventes": total_ventes,
            "total_cout": total_cout,
            "benefice": benefice
        }
        data["ventes"].append(vente)
        save_data(data)
        st.success("✅ Commande enregistrée avec succès !")
        st.experimental_rerun()

# ------------------------------
# PAGE STOCK
# ------------------------------
if page == "Stock":
    st.title("📦 Stock des produits")
    for produit, info in data["stock"].items():
        st.markdown(f"### {produit}")
        col1, col2 = st.columns(2)
        with col1:
            boites = st.number_input("Boîtes", value=info["boites"], min_value=0, key=f"stock_{produit}")
        with col2:
            prix_achat = st.number_input("Prix achat", value=info["prix_achat"], min_value=0, key=f"achat_{produit}")
            prix_vente = st.number_input("Prix vente", value=info["prix_vente"], min_value=0, key=f"vente_{produit}")
        data["stock"][produit]["boites"] = boites
        data["stock"][produit]["prix_achat"] = prix_achat
        data["stock"][produit]["prix_vente"] = prix_vente
    if st.button("Mettre à jour le stock"):
        save_data(data)
        st.success("Stock mis à jour ✔")

# ------------------------------
# PAGE HISTORIQUE
# ------------------------------
def generate_pdf_bytes(ventes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Historique des ventes", ln=1, align='C')
    pdf.set_font("Arial", '', 12)
    for vente in ventes:
        pdf.cell(0, 8, f"Commande N° {vente['num']} — {vente['date']}", ln=1)
        pdf.cell(0, 8, f"Client: {vente['client']}, Revendeur: {vente['revendeur']}, Chauffeur: {vente['chauffeur']}", ln=1)
        pdf.cell(0, 8, f"Total ventes: {vente.get('total_ventes',0)} DA, Frais: {vente['frais']['total_frais']} DA, Bénéfice: {vente['benefice']} DA", ln=1)
        pdf.ln(2)
        for prod, info in vente["produits"].items():
            pdf.cell(0, 6, f"{prod}: Qte={info['qte']} | Achat={info['prix_achat']} | Vente={info['prix_vente']} | Montant={info['montant']}", ln=1)
        pdf.ln(2)
    return pdf.output(dest='S').encode('latin1')

if page == "Historique":
    st.title("📜 Historique des ventes")
    if not data.get("ventes"):
        st.info("Aucune vente.")
    else:
        for idx, vente in enumerate(data["ventes"]):
            with st.expander(f"N°{vente['num']} — {vente['date']} — Total {vente.get('total_ventes',0)} DA"):
                st.write(f"Client: **{vente.get('client','')}**")
                st.write(f"Revendeur: **{vente.get('revendeur','')}**, Chauffeur: **{vente.get('chauffeur','')}**")
                st.write("Frais:", vente.get("frais", {}))
                
                rows = []
                for pname, pinfo in vente.get("produits", {}).items():
                    rows.append({
                        "Produit": pname,
                        "Quantité": pinfo.get("qte",0),
                        "Prix achat": pinfo.get("prix_achat",0),
                        "Prix vente": pinfo.get("prix_vente",0),
                        "Montant": pinfo.get("montant",0),
                    })
                df = pd.DataFrame(rows)
                st.dataframe(df)

                c1, c2 = st.columns(2)
                if c1.button("Supprimer", key=f"hist_del_{idx}"):
                    data["ventes"].pop(idx)
                    save_data(data)
                    st.success("Vente supprimée ✔")
                    st.experimental_rerun()

        pdf_bytes = generate_pdf_bytes(data.get("ventes", []))
        st.download_button("📄 Télécharger l'historique (PDF)", pdf_bytes, file_name="historique_mini_cones.pdf", mime="application/pdf")
