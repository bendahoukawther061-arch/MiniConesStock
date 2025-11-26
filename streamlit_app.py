import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
import io

# PDF export

try:
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
REPORTLAB_AVAILABLE = True
except:
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
except:
st.warning("Logo introuvable (logo.png) — continue sans logo.")

# ---------------------------

# DATA FILE

# ---------------------------

DATA_FILE = "stock.json"
DEFAULT_STOCK = {
"Twine Cones": {"boites": 50, "prix_achat": 0.0, "prix_vente": 0.0},
"Au Lait 50g": {"boites": 70, "prix_achat": 0.0, "prix_vente": 0.0},
"Bueno 70g": {"boites": 60, "prix_achat": 0.0, "prix_vente": 0.0},
"Pistachio": {"boites": 80, "prix_achat": 0.0, "prix_vente": 0.0},
"Crepes": {"boites": 30, "prix_achat": 0.0, "prix_vente": 0.0},
}

if not os.path.exists(DATA_FILE):
data = {"stock": DEFAULT_STOCK, "ventes": []}
with open(DATA_FILE, "w") as f:
json.dump(data, f, indent=4)
else:
with open(DATA_FILE, "r") as f:
data = json.load(f)

# Normaliser le stock

for prod, s in data["stock"].items():
if "boites" not in s:
s["boites"] = 0
if "prix_achat" not in s:
s["prix_achat"] = 0.0
if "prix_vente" not in s:
s["prix_vente"] = 0.0

# ---------------------------

# UTIL FUNCTIONS

# ---------------------------

def save_data():
with open(DATA_FILE, "w") as f:
json.dump(data, f, indent=4)

def calc_total(vente_produits):
return sum(item["montant"] for item in vente_produits.values())

def calc_marge(produit):
return produit["prix_vente"] - produit["prix_achat"]

def create_pdf_bytes(ventes_list, type_export="tableau"):
if not REPORTLAB_AVAILABLE:
return None
buf = io.BytesIO()
c = canvas.Canvas(buf, pagesize=A4)
width, height = A4
margin = 40
y = height - margin
c.setFont("Helvetica-Bold", 16)
c.drawString(margin, y, "Mini Cones — Reçu de vente")
y -= 30
for vente in ventes_list:
if type_export == "tableau":
c.setFont("Helvetica-Bold", 12)
c.drawString(margin, y, f"N° Vente: {vente['num']} — Date: {vente['date']} — Client: {vente.get('client','')}")
y -= 18
c.setFont("Helvetica", 11)
c.drawString(margin, y, f"Revendeur: {vente.get('revendeur','')} (Frais: {vente.get('frais_revendeur',0)}) — Chauffeur: {vente.get('chauffeur','')} (Frais: {vente.get('frais_chauffeur',0)})")
y -= 18
c.drawString(margin, y, "Produit | Qte | PU | Montant | Marge")
y -= 12
for prod, info in vente["produits"].items():
if y < 80:
c.showPage()
y = height - margin
marge = calc_marge(info)
c.drawString(margin, y, f"{prod} | {info['qte']} | {info['prix_vente']} | {info['montant']} | {marge}")
y -= 14
y -= 10
else:  # par commande (bon)
c.setFont("Helvetica-Bold", 12)
c.drawString(margin, y, f"Commande N°{vente['num']} - {vente['date']}")
y -= 18
c.setFont("Helvetica", 11)
for prod, info in vente["produits"].items():
marge = calc_marge(info)
c.drawString(margin, y, f"{prod}: Qte {info['qte']}, PU {info['prix_vente']}, Montant {info['montant']}, Marge {marge}")
y -= 14
y -= 10
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

```
client = st.text_input("Client")
revendeur = st.text_input("Nom revendeur")
frais_revendeur = st.number_input("Frais revendeur (calcul automatique)", min_value=0.0, value=0.0)
chauffeur = st.text_input("Nom chauffeur")
frais_chauffeur = st.number_input("Frais chauffeur (calcul automatique)", min_value=0.0, value=0.0)

produits = list(data["stock"].keys())
vente_produits = {}
total = 0.0

st.subheader("Produits")
for p in produits:
    st.markdown(f"**{p}**")
    qte = st.number_input(f"Quantité {p}", min_value=0, step=1, key=f"q_new_{p}")
    prix_achat = st.number_input(f"Prix achat {p}", min_value=0.0, step=0.5, key=f"pa_new_{p}", value=float(data['stock'][p]['prix_achat']))
    prix_vente = st.number_input(f"Prix vente {p}", min_value=0.0, step=0.5, key=f"pv_new_{p}", value=float(data['stock'][p]['prix_vente']))
    montant = qte * prix_vente
    vente_produits[p] = {"qte": qte, "prix_achat": prix_achat, "prix_vente": prix_vente, "montant": montant}
    total += montant

total_frais = frais_revendeur + frais_chauffeur
caisse = total - total_frais
st.subheader("Résumé")
st.write(f"Total ventes : {total}")
st.write(f"Total frais : {total_frais}")
st.write(f"Caisse : {caisse}")

if st.button("Enregistrer la vente"):
    # Vérifier stock
    ok = True
    for p, info in vente_produits.items():
        if info["qte"] > data["stock"][p]["boites"]:
            st.error(f"Stock insuffisant pour {p}. Disponible: {data['stock'][p]['boites']}")
            ok = False
    if ok:
        for p, info in vente_produits.items():
            data["stock"][p]["boites"] -= info["qte"]
            data["stock"][p]["prix_achat"] = info["prix_achat"]
            data["stock"][p]["prix_vente"] = info["prix_vente"]
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
```

# ---------------------------

# STOCK

# ---------------------------

elif page == "Stock":
st.title("Stock")
for p, s in data["stock"].items():
st.write(f"**{p}** — Boîtes: {s['boites']} | Prix achat: {s['prix_achat']} | Prix vente: {s['prix_vente']}")

```
st.markdown("---")
st.subheader("Ajouter au stock")
prod = st.selectbox("Produit", list(data["stock"].keys()))
add_boites = st.number_input("Boîtes à ajouter", min_value=0, step=1)
add_prix_achat = st.number_input("Prix achat", min_value=0.0, step=0.5)
add_prix_vente = st.number_input("Prix vente", min_value=0.0, step=0.5)
if st.button("Ajouter au stock"):
    data["stock"][prod]["boites"] += add_boites
    data["stock"][prod]["prix_achat"] = add_prix_achat
    data["stock"][prod]["prix_vente"] = add_prix_vente
    save_data()
    st.success("Stock mis à jour ✔")
    st.experimental_rerun()
```

# ---------------------------

# HISTORIQUE

# ---------------------------

elif page == "Historique":
st.title("Historique des ventes")
if len(data["ventes"]) == 0:
st.info("Aucune vente enregistrée.")
st.stop()

```
import pandas as pd
rows = []
for v in data["ventes"]:
    rows.append({
        "num": v["num"],
        "date": v["date"],
        "client": v.get("client",""),
        "total": calc_total(v["produits"]),
        "caisse": v.get("caisse",0)
    })
df = pd.DataFrame(rows).sort_values(by="num", ascending=False)
st.dataframe(df.rename(columns={"num":"N°","date":"Date","client":"Client","total":"Total","caisse":"Caisse"}), use_container_width=True)

st.subheader("Actions")
nums = [v["num"] for v in data["ventes"]]
choix = st.selectbox("Sélectionne N° vente", nums, index=0)
vente = next((v for v in data["ventes"] if v["num"]==choix), None)

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
        if option=="Tout le tableau":
            pdf_bytes = create_pdf_bytes(data["ventes"], type_export="tableau")
        else:
            pdf_bytes = create_pdf_bytes([vente], type_export="commande")
        st.download_button("Télécharger PDF", data=pdf_bytes, file_name="ventes.pdf", mime="application/pdf")
```
