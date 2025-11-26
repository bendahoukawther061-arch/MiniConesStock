import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
import io

# ---------------------------
# IMPORT REPORTLAB POUR PDF
# ---------------------------
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    REPORTLAB_AVAILABLE = True
except ImportError:
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
    pwd = st.text_input("Mot de passe", type="password")
    if st.button("Valider"):
        if pwd == PASSWORD:
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
except Exception:
    st.warning("Logo introuvable (logo.png) — continue sans logo.")

# ---------------------------
# DATA FILE
# ---------------------------
DATA_FILE = "stock.json"
DEFAULT_STOCK = {
    "Twine Cones": {"boites": 50, "prix_achat": 10, "prix_vente": 15},
    "Au Lait 50g": {"boites": 70, "prix_achat": 12, "prix_vente": 18},
    "Bueno 70g": {"boites": 60, "prix_achat": 15, "prix_vente": 20},
    "Pistachio": {"boites": 80, "prix_achat": 20, "prix_vente": 28},
    "Crêpes": {"boites": 40, "prix_achat": 8, "prix_vente": 12}
}

if not os.path.exists(DATA_FILE):
    data = {"stock": DEFAULT_STOCK, "ventes": []}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
else:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

# ---------------------------
# FONCTIONS UTILITAIRES
# ---------------------------
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calc_total_from_produits(produits_dict):
    return sum(item["montant"] for item in produits_dict.values())

def create_pdf_bytes(vente):
    if not REPORTLAB_AVAILABLE:
        return None
    buf = io.BytesIO()
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
    c.drawString(margin, y, f"Revendeur: {vente.get('revendeur','')}  Frais Revendeur: {vente.get('frais_revendeur',0)}")
    y -= 18
    c.drawString(margin, y, f"Chauffeur: {vente.get('chauffeur','')}  Frais Chauffeur: {vente.get('frais_chauffeur',0)}")
    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Produits:")
    y -= 18
    c.setFont("Helvetica", 11)
    c.drawString(margin, y, "Produit")
    c.drawString(margin+180, y, "Qte")
    c.drawString(margin+260, y, "Prix achat")
    c.drawString(margin+340, y, "Prix vente")
    c.drawString(margin+420, y, "Montant")
    y -= 12
    c.line(margin, y, width-margin, y)
    y -= 14
    for prod, info in vente["produits"].items():
        if y < 80:
            c.showPage()
            y = height - margin
        c.drawString(margin, y, prod)
        c.drawString(margin+180, y, str(info["qte"]))
        c.drawString(margin+260, y, str(info["prix_achat"]))
        c.drawString(margin+340, y, str(info["prix_vente"]))
        c.drawString(margin+420, y, str(info["montant"]))
        y -= 16
    y -= 8
    c.line(margin, y, width-margin, y)
    y -= 18
    c.drawString(margin, y, f"Total: {calc_total_from_produits(vente['produits'])}")
    y -= 18
    total_frais = vente.get("frais_revendeur",0) + vente.get("frais_chauffeur",0)
    c.drawString(margin, y, f"Total Frais: {total_frais}   Caisse: {vente.get('caisse',0)}")
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
    chauffeur = st.text_input("Chauffeur")

    # Calcul automatique des frais
    frais_revendeur = st.number_input("Frais Revendeur", min_value=0.0, value=0.0)
    frais_chauffeur = st.number_input("Frais Chauffeur", min_value=0.0, value=0.0)

    produits = list(data["stock"].keys())
    vente_produits = {}
    total = 0.0

    st.subheader("Produits")
    for p in produits:
        st.markdown(f"**{p}**")
        qte = st.number_input(f"Quantité {p} (en boîtes)", min_value=0, step=1, key=f"q_new_{p}")
        prix_achat = data["stock"][p]["prix_achat"]
        prix_vente = data["stock"][p]["prix_vente"]
        montant = qte * prix_vente
        vente_produits[p] = {"qte": qte, "prix_achat": prix_achat, "prix_vente": prix_vente, "montant": montant}
        total += montant

    caisse = total - (frais_revendeur + frais_chauffeur)
    st.subheader("Résumé")
    st.write(f"Total ventes : {total}")
    st.write(f"Total frais : {frais_revendeur + frais_chauffeur}")
    st.write(f"Caisse : {caisse}")

    if st.button("Enregistrer la vente"):
        # Vérification stock
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
# STOCK
# ---------------------------
elif page == "Stock":
    st.title("Stock")
    for p, s in data["stock"].items():
        st.write(f"**{p}** — Boîtes: {s['boites']} | Prix achat: {s['prix_achat']} | Prix vente: {s['prix_vente']}")

    st.markdown("---")
    st.subheader("Ajouter / Modifier le stock")
    prod = st.selectbox("Produit", list(data["stock"].keys()))
    new_boites = st.number_input("Boîtes", min_value=0, step=1)
    prix_achat = st.number_input("Prix achat", min_value=0.0, step=0.5)
    prix_vente = st.number_input("Prix vente", min_value=0.0, step=0.5)

    if st.button("Mettre à jour"):
        data["stock"][prod]["boites"] = new_boites
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
        rows.append({
            "num": v["num"],
            "date": v["date"],
            "client": v.get("client",""),
            "revendeur": v.get("revendeur",""),
            "chauffeur": v.get("chauffeur",""),
            "total": calc_total_from_produits(v["produits"]),
            "caisse": v.get("caisse",0)
        })
    df = pd.DataFrame(rows).sort_values(by="num", ascending=False)
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("Actions sur la vente")
    nums = [v["num"] for v in data["ventes"]]
    choix = st.selectbox("Sélectionne N° vente", nums, index=0)
    vente = next((v for v in data["ventes"] if v["num"] == choix), None)

    col_del, col_mod, col_pdf = st.columns([1,1,1])
    with col_del:
        if st.button("❌ Supprimer"):
            for prod, info in vente["produits"].items():
                data["stock"][prod]["boites"] += info["qte"]
            data["ventes"] = [v for v in data["ventes"] if v["num"] != choix]
            save_data()
            st.success("Vente supprimée ✔")
            st.experimental_rerun()

    with col_mod:
        if st.button("✏ Modifier"):
            st.session_state["editing"] = choix
            st.experimental_rerun()

    with col_pdf:
        if st.button("📄 Imprimer"):
            option = st.radio("Option PDF", ["Tout le tableau", "Par commande"])
            if option == "Tout le tableau":
                # Création PDF pour toutes les ventes
                buf = io.BytesIO()
                c = canvas.Canvas(buf, pagesize=A4)
                y = 800
                for v in data["ventes"]:
                    c.drawString(50, y, f"N°{v['num']} - {v['date']} - Client: {v.get('client','')} - Total: {calc_total_from_produits(v['produits'])}")
                    y -= 20
                    if y < 50:
                        c.showPage()
                        y = 800
                c.save()
                buf.seek(0)
                st.download_button("Télécharger PDF Historique", data=buf.read(), file_name="historique.pdf", mime="application/pdf")
            else:
                pdf_bytes = create_pdf_bytes(vente)
                if pdf_bytes:
                    st.download_button("Télécharger PDF Commande", data=pdf_bytes, file_name=f"vente_{vente['num']}.pdf", mime="application/pdf")
