import streamlit as st
import json
import os
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from PIL import Image

# ---------------------------
# CONFIGURATION
# ---------------------------
st.set_page_config(page_title="Mini Cones", page_icon="🍦")

# Authentification
PASSWORD = "mehdi123"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Mehdi BENDAHOU")
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("Valider"):
        if pwd.lower() == PASSWORD:
            st.session_state.authenticated = True
            st.success("Connecté ✅")
        else:
            st.error("Mot de passe incorrect ❌")
    st.stop()

# ---------------------------
# LOGO
# ---------------------------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=180)
except:
    st.warning("Logo introuvable — continue sans logo.")

# ---------------------------
# FICHIER STOCK
# ---------------------------
DATA_FILE = "stock.json"
DEFAULT_STOCK = {
    "Twine Cones": {"boites": 50, "prix_achat": 10, "prix_vente": 15},
    "Au Lait 50g": {"boites": 70, "prix_achat": 12, "prix_vente": 18},
    "Bueno 70g": {"boites": 60, "prix_achat": 14, "prix_vente": 20},
    "Pistachio": {"boites": 80, "prix_achat": 16, "prix_vente": 22},
    "Crepes": {"boites": 40, "prix_achat": 20, "prix_vente": 30}
}

if not os.path.exists(DATA_FILE):
    data = {"stock": DEFAULT_STOCK, "ventes": []}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
else:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ---------------------------
# UTILITAIRES
# ---------------------------
def calc_total(vente_produits):
    return sum(info["qte"] * info["prix_vente"] for info in vente_produits.values())

def calc_marge(vente_produits):
    return sum((info["prix_vente"] - info["prix_achat"]) * info["qte"] for info in vente_produits.values())

def create_pdf_bytes(vente):
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin
    c.setFont("Helvetica-Bold", 16)
    c.drawString(margin, y, "Reçu de vente - Mini Cones")
    c.setFont("Helvetica", 11)
    y -= 30
    c.drawString(margin, y, f"N° Vente: {vente['num']}")
    y -= 18
    c.drawString(margin, y, f"Date: {vente['date']}")
    y -= 18
    c.drawString(margin, y, f"Client: {vente.get('client','')}")
    y -= 18
    c.drawString(margin, y, f"Revendeur: {vente.get('revendeur','')} - Frais: {vente.get('frais_revendeur',0)}")
    y -= 18
    c.drawString(margin, y, f"Chauffeur: {vente.get('chauffeur','')} - Frais: {vente.get('frais_chauffeur',0)}")
    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Produits:")
    y -= 18
    c.setFont("Helvetica", 11)
    c.drawString(margin, y, "Produit")
    c.drawString(margin+180, y, "Qte")
    c.drawString(margin+260, y, "Prix vente")
    c.drawString(margin+340, y, "Montant")
    c.drawString(margin+420, y, "Marge")
    y -= 12
    c.line(margin, y, width-margin, y)
    y -= 14
    for prod, info in vente["produits"].items():
        if y < 80:
            c.showPage()
            y = height - margin
        c.drawString(margin, y, prod)
        c.drawString(margin+180, y, str(info["qte"]))
        c.drawString(margin+260, y, str(info["prix_vente"]))
        montant = info["qte"] * info["prix_vente"]
        marge = (info["prix_vente"] - info["prix_achat"]) * info["qte"]
        c.drawString(margin+340, y, str(montant))
        c.drawString(margin+420, y, str(marge))
        y -= 16
    y -= 8
    total = calc_total(vente["produits"])
    total_marge = calc_marge(vente["produits"])
    c.line(margin, y, width-margin, y)
    y -= 18
    c.drawString(margin, y, f"Total ventes: {total} | Marge totale: {total_marge}")
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

# ---------------------------
# MENU
# ---------------------------
page = st.sidebar.selectbox("Menu", ["Nouvelle vente", "Stock", "Historique"])

# ---------------------------
# NOUVELLE VENTE
# ---------------------------
if page == "Nouvelle vente":
    st.title("Nouvelle vente")
    num_vente = 1 if len(data["ventes"]) == 0 else data["ventes"][-1]["num"] + 1
    today = datetime.today().strftime("%Y-%m-%d")
    st.write(f"Date: {today} — N° {num_vente}")

    client = st.text_input("Client")
    revendeur = st.text_input("Revendeur")
    frais_revendeur = st.number_input("Frais revendeur", min_value=0.0, value=0.0)
    chauffeur = st.text_input("Chauffeur")
    frais_chauffeur = st.number_input("Frais chauffeur", min_value=0.0, value=0.0)

    st.subheader("Produits")
    vente_produits = {}
    for prod, s in data["stock"].items():
        st.markdown(f"**{prod}** — Stock: {s['boites']} boîtes | Prix achat: {s['prix_achat']} | Prix vente: {s['prix_vente']}")
        qte = st.number_input(f"Quantité {prod}", min_value=0, max_value=s["boites"], step=1, key=f"q_{prod}")
        vente_produits[prod] = {
            "qte": qte,
            "prix_achat": s["prix_achat"],
            "prix_vente": s["prix_vente"]
        }

    if st.button("Enregistrer la vente"):
        ok = True
        for prod, info in vente_produits.items():
            if info["qte"] > data["stock"][prod]["boites"]:
                st.error(f"Stock insuffisant pour {prod}")
                ok = False
        if ok:
            for prod, info in vente_produits.items():
                data["stock"][prod]["boites"] -= info["qte"]
            vente = {
                "num": num_vente,
                "date": today,
                "client": client,
                "revendeur": revendeur,
                "frais_revendeur": frais_revendeur,
                "chauffeur": chauffeur,
                "frais_chauffeur": frais_chauffeur,
                "produits": vente_produits
            }
            data["ventes"].append(vente)
            save_data()
            st.success("Vente enregistrée ✔")
            st.experimental_rerun()

# ---------------------------
# STOCK
# ---------------------------
elif page == "Stock":
    st.title("Stock")
    for prod, s in data["stock"].items():
        st.write(f"**{prod}** — Boîtes: {s['boites']} | Prix achat: {s['prix_achat']} | Prix vente: {s['prix_vente']}")

    st.markdown("---")
    st.subheader("Ajouter au stock")
    prod = st.selectbox("Produit", list(data["stock"].keys()))
    add_boites = st.number_input("Boîtes à ajouter", min_value=0, step=1)
    prix_achat = st.number_input("Prix achat", min_value=0.0, value=data["stock"][prod]["prix_achat"])
    prix_vente = st.number_input("Prix vente", min_value=0.0, value=data["stock"][prod]["prix_vente"])
    if st.button("Ajouter / Mettre à jour"):
        data["stock"][prod]["boites"] += add_boites
        data["stock"][prod]["prix_achat"] = prix_achat
        data["stock"][prod]["prix_vente"] = prix_vente
        save_data()
        st.success("Stock mis à jour ✔")
        st.experimental_rerun()

# ---------------------------
# HISTORIQUE
# ---------------------------
elif page == "Historique":
    st.title("Historique des ventes")
    if len(data["ventes"]) == 0:
        st.info("Aucune vente enregistrée.")
        st.stop()

    import pandas as pd
    rows = []
    for v in data["ventes"]:
        total = calc_total(v["produits"])
        marge = calc_marge(v["produits"])
        rows.append({
            "num": v["num"],
            "date": v["date"],
            "client": v.get("client",""),
            "revendeur": v.get("revendeur",""),
            "chauffeur": v.get("chauffeur",""),
            "total": total,
            "marge": marge
        })
    df = pd.DataFrame(rows).sort_values(by="num", ascending=False)
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("Gérer une vente")
    choix = st.selectbox("Sélectionne N° vente", df["num"])
    vente = next((v for v in data["ventes"] if v["num"] == choix), None)

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("❌ Supprimer"):
            for prod, info in vente["produits"].items():
                data["stock"][prod]["boites"] += info["qte"]
            data["ventes"] = [v for v in data["ventes"] if v["num"] != choix]
            save_data()
            st.success("Vente supprimée ✔")
            st.experimental_rerun()
    with col2:
        if st.button("✏ Modifier"):
            st.session_state.editing = choix
            st.experimental_rerun()
    with col3:
        if st.button("📄 Imprimer PDF"):
            pdf_bytes = create_pdf_bytes(vente)
            st.download_button("Télécharger le PDF", data=pdf_bytes, file_name=f"vente_{vente['num']}.pdf", mime="application/pdf")
