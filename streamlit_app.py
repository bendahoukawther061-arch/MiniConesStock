import streamlit as st
import json
from datetime import datetime
import os
from PIL import Image
import io

# PDF
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="Mini Cones", page_icon="🍦")
PASSWORD = "bendahou mehdi"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Connexion")
    pwd = st.text_input("Nom et prénom", type="password")
    if st.button("Valider"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.success("Connecté ✅")
        else:
            st.error("Nom ou mot de passe incorrect ❌")
    st.stop()

# ---------------------------
# LOGO
# ---------------------------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=180)
except Exception:
    st.warning("Logo introuvable — continue sans logo.")

# ---------------------------
# DATA FILE
# ---------------------------
DATA_FILE = "stock.json"
DEFAULT_STOCK = {
    "Twine Cones": {"boites": 50, "prix_achat": 0, "prix_vente": 0},
    "Au Lait 50g": {"boites": 70, "prix_achat": 0, "prix_vente": 0},
    "Bueno 70g": {"boites": 60, "prix_achat": 0, "prix_vente": 0},
    "Pistachio": {"boites": 80, "prix_achat": 0, "prix_vente": 0},
    "Crêpes": {"boites": 50, "prix_achat": 0, "prix_vente": 0},
}

if not os.path.exists(DATA_FILE):
    data = {"stock": DEFAULT_STOCK, "ventes": []}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
else:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

# ---------------------------
# UTIL FUNCTIONS
# ---------------------------
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calc_total_from_produits(produits_dict):
    return sum(item["montant"] for item in produits_dict.values())

def create_pdf_bytes(vente, all_table=False):
    if not REPORTLAB_AVAILABLE:
        return None
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margin = 40
    y = height - margin
    c.setFont("Helvetica-Bold", 16)
    if all_table:
        c.drawString(margin, y, "Historique complet des ventes - Mini Cones")
        y -= 30
        for v in data["ventes"]:
            c.setFont("Helvetica-Bold", 12)
            c.drawString(margin, y, f"N° Vente: {v['num']} | Date: {v['date']} | Client: {v.get('client','')}")
            y -= 18
            c.setFont("Helvetica", 11)
            c.drawString(margin, y, "Produit  Qte  PU  Montant  Prix Achat  Marge")
            y -= 14
            for prod, info in v["produits"].items():
                marge = info['prix'] - data["stock"][prod]["prix_achat"]
                c.drawString(margin, y, f"{prod}  {info['qte']}  {info['prix']}  {info['montant']}  {data['stock'][prod]['prix_achat']}  {marge}")
                y -= 14
            y -= 10
            if y < 80:
                c.showPage()
                y = height - margin
    else:
        c.drawString(margin, y, f"Reçu de vente N° {vente['num']} - Mini Cones")
        y -= 30
        c.setFont("Helvetica", 11)
        c.drawString(margin, y, f"Date: {vente['date']} | Client: {vente.get('client','')}")
        y -= 18
        c.drawString(margin, y, f"Revendeur: {vente.get('revendeur','')} (Frais: {vente.get('frais_revendeur',0)})")
        y -= 18
        c.drawString(margin, y, f"Chauffeur: {vente.get('chauffeur','')} (Frais: {vente.get('frais_chauffeur',0)})")
        y -= 25
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Produits:")
        y -= 18
        c.setFont("Helvetica", 11)
        c.drawString(margin, y, "Produit  Qte  PU  Montant  Prix Achat  Marge")
        y -= 12
        for prod, info in vente["produits"].items():
            marge = info['prix'] - data["stock"][prod]["prix_achat"]
            c.drawString(margin, y, f"{prod}  {info['qte']}  {info['prix']}  {info['montant']}  {data['stock'][prod]['prix_achat']}  {marge}")
            y -= 16
        y -= 10
        c.drawString(margin, y, f"Total: {calc_total_from_produits(vente['produits'])} | Caisse: {vente.get('caisse',0)}")
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

# ---------------------------
# MENU SELECTION
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
    frais_revendeur = st.number_input("Frais Revendeur", min_value=0.0, value=0.0)
    chauffeur = st.text_input("Chauffeur")
    frais_chauffeur = st.number_input("Frais Chauffeur", min_value=0.0, value=0.0)

    produits = list(data["stock"].keys())
    vente_produits = {}
    total = 0.0

    st.subheader("Produits")
    for p in produits:
        st.markdown(f"**{p}**")
        qte = st.number_input(f"Quantité {p} (en boîtes)", min_value=0, step=1, key=f"q_new_{p}")
        prix = st.number_input(f"Prix vente {p}", min_value=0.0, step=0.5, key=f"pr_new_{p}")
        montant = qte * prix
        vente_produits[p] = {"qte": qte, "prix": prix, "montant": montant}
        total += montant

    frais = frais_revendeur + frais_chauffeur
    caisse = total - frais
    st.subheader("Résumé")
    st.write(f"Total ventes : {total}")
    st.write(f"Frais : {frais} (Revendeur + Chauffeur)")
    st.write(f"Caisse : {caisse}")

    if st.button("Enregistrer la vente"):
        ok = True
        for p, info in vente_produits.items():
            if info["qte"] > data["stock"][p]["boites"]:
                st.error(f"Stock insuffisant pour {p}. Disponible: {data['stock'][p]['boites']}")
                ok = False
        if ok:
            for p, info in vente_produits.items():
                data["stock"][p]["boites"] -= info["qte"]
            vente = {
                "num": num_vente,
                "date": today,
                "client": client,
                "revendeur": revendeur,
                "frais_revendeur": frais_revendeur,
                "chauffeur": chauffeur,
                "frais_chauffeur": frais_chauffeur,
                "produits": vente_produits,
                "caisse": caisse
            }
            data["ventes"].append(vente)
            save_data()
            st.success("Vente enregistrée ✔")
            st.experimental_rerun()

# ---------------------------
# STOCK PAGE
# ---------------------------
elif page == "Stock":
    st.title("Stock")
    for p, s in data["stock"].items():
        st.write(f"**{p}** — Boîtes: {s['boites']} | Prix achat: {s['prix_achat']} | Prix vente: {s['prix_vente']}")

    st.markdown("---")
    st.subheader("Modifier le stock et prix")
    prod = st.selectbox("Produit", list(data["stock"].keys()))
    add_boites = st.number_input("Boîtes", min_value=0, step=1)
    prix_achat = st.number_input("Prix achat", min_value=0.0, step=0.5)
    prix_vente = st.number_input("Prix vente", min_value=0.0, step=0.5)
    if st.button("Mettre à jour"):
        data["stock"][prod]["boites"] = add_boites
        data["stock"][prod]["prix_achat"] = prix_achat
        data["stock"][prod]["prix_vente"] = prix_vente
        save_data()
        st.success("Stock mis à jour ✔")
        st.experimental_rerun()

# ---------------------------
# HISTORIQUE PAGE
# ---------------------------
elif page == "Historique":
    st.title("Historique des ventes")
    if len(data["ventes"]) == 0:
        st.info("Aucune vente enregistrée.")
        st.stop()

    import pandas as pd
    rows = []
    for v in data["ventes"]:
        rows.append({
            "num": v["num"],
            "date": v["date"],
            "client": v.get("client",""),
            "total": calc_total_from_produits(v["produits"]),
            "caisse": v.get("caisse",0)
        })
    df = pd.DataFrame(rows).sort_values(by="num", ascending=False)
    st.dataframe(df.rename(columns={"num":"N°","date":"Date","client":"Client","total":"Total","caisse":"Caisse"}), use_container_width=True)

    st.markdown("---")
    st.subheader("Actions")
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("❌ Supprimer une vente"):
            choix = st.selectbox("Sélectionne N° vente", [v["num"] for v in data["ventes"]])
            data["ventes"] = [v for v in data["ventes"] if v["num"] != choix]
            save_data()
            st.success("Vente supprimée ✔")
            st.experimental_rerun()
    with col2:
        if st.button("✏ Modifier une vente"):
            choix = st.selectbox("Sélectionne N° vente", [v["num"] for v in data["ventes"]])
            st.write("Pour modifier, il faut passer par Nouvelle vente avec les nouvelles quantités et prix.")
    with col3:
        st.subheader("Imprimer PDF")
        if st.button("📄 Tout le tableau"):
            pdf_bytes = create_pdf_bytes(None, all_table=True)
            st.download_button("Télécharger PDF complet", data=pdf_bytes, file_name="historique_complet.pdf", mime="application/pdf")
        if st.button("📄 Par commande"):
            choix = st.selectbox("Sélectionne N° vente pour PDF", [v["num"] for v in data["ventes"]])
            vente = next(v for v in data["ventes"] if v["num"]==choix)
            pdf_bytes = create_pdf_bytes(vente)
            st.download_button("Télécharger PDF", data=pdf_bytes, file_name=f"vente_{vente['num']}.pdf", mime="application/pdf")
