import streamlit as st
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
            "produits": vente_produits,
            "total": total_montant
        }
        data["ventes"].append(vente)
        save_data(data)
        st.success("Commande enregistrée !")
        st.experimental_rerun()

# ------------------------------
# PAGE STOCK
# ------------------------------
if page == "Stock":
    st.title("📦 Gestion du Stock")
    for produit, info in data["stock"].items():
        colA, colB = st.columns(2)
        with colA:
            st.markdown(f"**{produit}**")
            info["boites"] = st.number_input(f"Stock (boites) {produit}", min_value=0, value=info["boites"], key=f"stock_{produit}")
        with colB:
            info["prix_vente"] = st.number_input(f"Prix vente (DA) {produit}", min_value=0, value=info["prix_vente"], key=f"prix_{produit}")
    if st.button("Enregistrer le stock"):
        save_data(data)
        st.success("Stock mis à jour !")

# ------------------------------
# PAGE HISTORIQUE
# ------------------------------
if page == "Historique":
    st.title("🕒 Historique des Ventes")

    if len(data["ventes"]) == 0:
        st.info("Aucune vente enregistrée.")
    else:
        for i, vente in enumerate(data["ventes"]):
            st.subheader(f"Vente N° {vente['num']} — {vente['date']}")
            st.write(f"Client: {vente['client']}")
            df = pd.DataFrame(vente["produits"]).T
            df["montant"] = df["montant"]
            st.dataframe(df)

            col1, col2 = st.columns(2)
            if col1.button("Modifier", key=f"mod_{i}"):
                for produit, info in vente["produits"].items():
                    vente["produits"][produit]["qte"] = st.number_input(f"{produit} quantité", value=info["qte"], key=f"mod_qte_{i}_{produit}")
                save_data(data)
                st.success("Vente modifiée !")
                st.experimental_rerun()
            if col2.button("Supprimer", key=f"sup_{i}"):
                data["ventes"].pop(i)
                save_data(data)
                st.success("Vente supprimée !")
                st.experimental_rerun()

    # Export PDF
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
            pdf.cell(0, 6, f"Total: {vente['total']} DA", ln=True)
            pdf.ln(5)
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        buffer = BytesIO(pdf_bytes)
        return buffer

    buffer = export_pdf(data["ventes"])
    st.download_button("📄 Télécharger l'historique en PDF", data=buffer, file_name="historique.pdf", mime="application/pdf")
