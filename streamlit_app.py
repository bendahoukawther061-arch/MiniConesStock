import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
from fpdf import FPDF
import base64

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="Mini Cones", page_icon="🍦")

PASSWORD = "mehdi123"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔒 Connexion")
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("Valider"):
        if pwd.lower() == PASSWORD:
            st.session_state.auth = True
            st.success("Connecté ✔")
        else:
            st.error("Mot de passe incorrect ❌")
    st.stop()

# ---------------------------
# DATA FILE
# ---------------------------
DATA_FILE = "stock.json"

DEFAULT_DATA = {
    "stock": {
        "Twine Cones": {"boites": 50, "prix_achat": 10, "prix_vente": 15},
        "Pistache": {"boites": 60, "prix_achat": 12, "prix_vente": 18},
        "Bueno": {"boites": 40, "prix_achat": 14, "prix_vente": 20},
        "Au Lait": {"boites": 80, "prix_achat": 11, "prix_vente": 17},
        "Crêpes": {"boites": 70, "prix_achat": 9, "prix_vente": 14}
    },
    "ventes": []
}

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump(DEFAULT_DATA, f, indent=4)

with open(DATA_FILE, "r") as f:
    data = json.load(f)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------------------
# MENU
# ---------------------------
page = st.sidebar.selectbox("📌 Menu", ["Commande", "Stock", "Historique"])

# ---------------------------
# PAGE 1 — COMMANDE
# ---------------------------
if page == "Commande":
    st.title("🧾 Nouvelle Commande")

    num = 1 if len(data["ventes"]) == 0 else data["ventes"][-1]["num"] + 1
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    st.write(f"**Commande N° : {num}** — {date}")

    client = st.text_input("Nom du client")
    revendeur = st.text_input("Nom du revendeur")
    prix_revendeur = st.number_input("Prix revendeur", min_value=0.0)
    chauffeur = st.text_input("Nom du chauffeur")
    prix_chauffeur = st.number_input("Prix chauffeur", min_value=0.0)

    charges = st.number_input("Autres charges", min_value=0.0)
    total_charges = prix_revendeur + prix_chauffeur + charges
    st.info(f"Total charges = {total_charges} DA")

    st.subheader("Produits")
    produits = data["stock"].keys()
    vente_produits = {}
    total_vente = 0
    benef_brut = 0

    for p in produits:
        st.markdown(f"### {p}")
        qte = st.number_input(f"Quantité vendue ({p})", min_value=0, max_value=data["stock"][p]["boites"], key=f"q_{p}")
        pa = data["stock"][p]["prix_achat"]
        pv = st.number_input(f"Prix vente ({p})", min_value=0.0, value=float(data["stock"][p]["prix_vente"]), key=f"pv_{p}")

        montant = qte * pv
        marge = (pv - pa) * qte

        vente_produits[p] = {
            "qte": qte,
            "prix_vente": pv,
            "prix_achat": pa,
            "montant": montant,
            "marge": marge
        }

        total_vente += montant
        benef_brut += marge

    benef_net = benef_brut - total_charges

    st.subheader("Résumé")
    st.write(f"💰 **Montant total : {total_vente} DA**")
    st.write(f"📈 **Bénéfice brut : {benef_brut} DA**")
    st.write(f"🟢 **Bénéfice NET : {benef_net} DA**")

    if st.button("💾 Enregistrer la commande"):
        for p, info in vente_produits.items():
            data["stock"][p]["boites"] -= info["qte"]

        vente = {
            "num": num,
            "date": date,
            "client": client,
            "revendeur": revendeur,
            "chauffeur": chauffeur,
            "charges": total_charges,
            "produits": vente_produits,
            "total_vente": total_vente,
            "benef_brut": benef_brut,
            "benef_net": benef_net
        }

        data["ventes"].append(vente)
        save_data()
        st.success("Commande enregistrée ✔")
        st.rerun()

# ---------------------------
# PAGE 2 — STOCK
# ---------------------------
elif page == "Stock":
    st.title("📦 Stock des Produits")

    for p, info in data["stock"].items():
        st.write(f"**{p}** — {info['boites']} boîtes — PA: {info['prix_achat']} — PV: {info['prix_vente']}")

    st.subheader("Modifier un produit")
    prod = st.selectbox("Produit", list(data["stock"].keys()))
    new_boites = st.number_input("Nouvelle quantité", min_value=0)
    new_pa = st.number_input("Prix achat", min_value=0.0, value=float(data["stock"][prod]["prix_achat"]))
    new_pv = st.number_input("Prix vente", min_value=0.0, value=float(data["stock"][prod]["prix_vente"]))

    if st.button("Mettre à jour"):
        data["stock"][prod]["boites"] = new_boites
        data["stock"][prod]["prix_achat"] = new_pa
        data["stock"][prod]["prix_vente"] = new_pv
        save_data()
        st.success("Stock mis à jour ✔")
        st.rerun()

# ---------------------------
# PAGE 3 — HISTORIQUE
# ---------------------------
elif page == "Historique":
    st.title("📚 Historique des Commandes")

    if len(data["ventes"]) == 0:
        st.info("Aucune commande enregistrée.")
        st.stop()

    df = pd.DataFrame([{
        "N°": v["num"],
        "Date": v["date"],
        "Client": v["client"],
        "Total": v["total_vente"],
        "Bénéfice net": v["benef_net"]
    } for v in data["ventes"]])

    st.dataframe(df, use_container_width=True)

    num = st.selectbox("Sélectionner une commande", df["N°"])
    vente = next(v for v in data["ventes"] if v["num"] == num)

    st.write("### Détails")
    st.json(vente)

    # SUPPRIMER
    if st.button("❌ Supprimer cette commande"):
        data["ventes"] = [v for v in data["ventes"] if v["num"] != num]
        save_data()
        st.success("Suppression réussie ✔")
        st.rerun()

    # IMPRIMER PDF
    if st.button("🖨 Imprimer PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.cell(200, 10, txt=f"Commande N° {vente['num']}", ln=True, align="C")
        pdf.cell(200, 10, txt=f"Date : {vente['date']}", ln=True)
        pdf.cell(200, 10, txt=f"Client : {vente['client']}", ln=True)
        pdf.ln(5)

        pdf.cell(200, 10, txt="Produits :", ln=True)
        for p, info in vente["produits"].items():
            line = f"{p}: {info['qte']} boîtes | PV {info['prix_vente']} | PA {info['prix_achat']}"
            pdf.cell(200, 10, txt=line, ln=True)

        pdf.ln(5)
        pdf.cell(200, 10, txt=f"Total vente : {vente['total_vente']} DA", ln=True)
        pdf.cell(200, 10, txt=f"Bénéfice net : {vente['benef_net']} DA", ln=True)

        file_path = f"commande_{vente['num']}.pdf"
        pdf.output(file_path)

        with open(file_path, "rb") as f:
            pdf_bytes = f.read()
            b64 = base64.b64encode(pdf_bytes).decode()

        st.markdown(f'<a download="{file_path}" href="data:application/pdf;base64,{b64}">📥 Télécharger PDF</a>', unsafe_allow_html=True)

