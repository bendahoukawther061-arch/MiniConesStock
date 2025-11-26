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
st.warning("Logo introuvable — continue sans logo.")

# ---------------------------

# DATA FILE

# ---------------------------

DATA_FILE = "stock.json"
DEFAULT_STOCK = {
"Mini Cones": {"boites": 50, "prix_achat": 5.0, "prix_vente": 8.0},
"Au Lait 50g": {"boites": 70, "prix_achat": 6.0, "prix_vente": 10.0},
"Bueno 70g": {"boites": 60, "prix_achat": 7.0, "prix_vente": 12.0},
"Pistachio": {"boites": 80, "prix_achat": 8.0, "prix_vente": 15.0},
"Crêpes": {"boites": 50, "prix_achat": 4.0, "prix_vente": 7.0},
}

if not os.path.exists(DATA_FILE):
data = {"stock": DEFAULT_STOCK, "ventes": []}
with open(DATA_FILE, "w") as f:
json.dump(data, f, indent=4)
else:
with open(DATA_FILE, "r") as f:
data = json.load(f)

# Normaliser le stock (tout en boîtes)

for k, v in data["stock"].items():
if isinstance(v, dict) and "fardeaux" in v:
v["boites"] += v.get("fardeaux",0) * 6
v["fardeaux"] = 0
with open(DATA_FILE, "w") as f:
json.dump(data, f, indent=4)

# ---------------------------

# UTIL

# ---------------------------

def save_data():
with open(DATA_FILE, "w") as f:
json.dump(data, f, indent=4)

def calc_total_from_produits(prods):
return sum(item["montant"] for item in prods.values())

def calc_total_achat(prods):
return sum(data["stock"][p]["prix_achat"] * info["qte_boite"] for p, info in prods.items())

def create_pdf_bytes(vente, option="commande"):
if not REPORTLAB_AVAILABLE:
return None
buf = io.BytesIO()
c = canvas.Canvas(buf, pagesize=A4)
width, height = A4
margin = 40
y = height - margin
c.setFont("Helvetica-Bold", 16)
c.drawString(margin, y, "Reçu de vente - Mini Cones")
y -= 25
c.setFont("Helvetica", 11)
c.drawString(margin, y, f"N° Vente: {vente['num']}  Date: {vente['date']}")
y -= 18
c.drawString(margin, y, f"Client: {vente.get('client','')}")
y -= 18
c.drawString(margin, y, f"Revendeur: {vente.get('revendeur','')}  Frais: {vente.get('frais_revendeur',0)}")
y -= 18
c.drawString(margin, y, f"Chauffeur: {vente.get('chauffeur','')}  Frais: {vente.get('frais_chauffeur',0)}")
y -= 25
c.setFont("Helvetica-Bold", 12)
c.drawString(margin, y, "Produits:")
y -= 18
c.setFont("Helvetica", 11)
c.drawString(margin, y, "Produit")
c.drawString(margin+180, y, "Qte")
c.drawString(margin+260, y, "Prix Achat")
c.drawString(margin+350, y, "Prix Vente")
c.drawString(margin+440, y, "Montant")
y -= 12
c.line(margin, y, width-margin, y)
y -= 14
for prod, info in vente["produits"].items():
if y < 80:
c.showPage()
y = height - margin
c.drawString(margin, y, prod)
c.drawString(margin+180, y, str(info["qte_boite"]))
c.drawString(margin+260, y, str(data["stock"][prod]["prix_achat"]))
c.drawString(margin+350, y, str(data["stock"][prod]["prix_vente"]))
c.drawString(margin+440, y, str(info["montant"]))
y -= 16
y -= 8
c.line(margin, y, width-margin, y)
y -= 18
c.drawString(margin, y, f"Total: {calc_total_from_produits(vente['produits'])}")
y -= 18
c.drawString(margin, y, f"Dette: {vente.get('dettes',0)}  Frais total: {vente.get('frais_chauffeur',0)+vente.get('frais_revendeur',0)}  Caisse: {vente.get('caisse',0)}")
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

if page=="Nouvelle vente":
st.title("Nouvelle vente")
num_vente = 1 if len(data["ventes"])==0 else data["ventes"][-1]["num"]+1
today = datetime.today().strftime("%Y-%m-%d")
st.write(f"Date: {today} — N° {num_vente}")

```
client = st.text_input("Client")
revendeur = st.text_input("Revendeur")
frais_revendeur = st.number_input("Frais Revendeur", min_value=0.0, value=0.0)
chauffeur = st.text_input("Chauffeur")
frais_chauffeur = st.number_input("Frais Chauffeur", min_value=0.0, value=0.0)
dettes = st.number_input("Dette (non payé)", min_value=0.0, value=0.0)

st.subheader("Produits")
vente_produits = {}
total = 0.0
for p, s in data["stock"].items():
    st.markdown(f"**{p}**")
    qte = st.number_input(f"Quantité {p}", min_value=0, max_value=s["boites"], step=1, key=f"q_{p}")
    prix = st.number_input(f"Prix Vente {p}", min_value=0.0, value=s["prix_vente"], step=0.5, key=f"pr_{p}")
    montant = qte*prix
    vente_produits[p] = {"qte_boite": qte, "prix_vente": prix, "montant": montant}
    total += montant

caisse = total - dettes - (frais_chauffeur + frais_revendeur)
st.subheader("Résumé")
st.write(f"Total ventes: {total}")
st.write(f"Caisse: {caisse}")

if st.button("Enregistrer la vente"):
    ok = True
    for p, info in vente_produits.items():
        if info["qte_boite"] > data["stock"][p]["boites"]:
            st.error(f"Stock insuffisant pour {p}")
            ok=False
    if ok:
        for p, info in vente_produits.items():
            data["stock"][p]["boites"] -= info["qte_boite"]
        vente = {
            "num": num_vente,
            "date": today,
            "client": client,
            "revendeur": revendeur,
            "frais_revendeur": frais_revendeur,
            "chauffeur": chauffeur,
            "frais_chauffeur": frais_chauffeur,
            "produits": vente_produits,
            "dettes": dettes,
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

elif page=="Stock":
st.title("Stock")
for p, s in data["stock"].items():
st.write(f"**{p}** — Boîtes: {s['boites']} | Prix achat: {s['prix_achat']} | Prix vente: {s['prix_vente']}")

```
st.markdown("---")
st.subheader("Ajouter au stock")
prod = st.selectbox("Produit", list(data["stock"].keys()))
add_boites = st.number_input("Boîtes à ajouter", min_value=0, step=1)
if st.button("Ajouter au stock"):
    data["stock"][prod]["boites"] += add_boites
    save_data()
    st.success("Stock mis à jour ✔")
    st.experimental_rerun()
```

# ---------------------------

# HISTORIQUE

# ---------------------------

elif page=="Historique":
st.title("Historique des ventes")
if len(data["ventes"])==0:
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
        "revendeur": v.get("revendeur",""),
        "chauffeur": v.get("chauffeur",""),
        "total": calc_total_from_produits(v["produits"]),
        "caisse": v.get("caisse",0)
    })
df = pd.DataFrame(rows).sort_values(by="num", ascending=False)
st.dataframe(df, use_container_width=True)

st.subheader("Gérer une vente")
nums = [v["num"] for v in data["ventes"]]
choix = st.selectbox("Sélectionne N° vente", nums, index=0)
vente = next((v for v in data["ventes"] if v["num"]==choix), None)
if vente:
    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        if st.button("❌ Supprimer"):
            for p, info in vente["produits"].items():
                data["stock"][p]["boites"] += info["qte_boite"]
            data["ventes"] = [v for v in data["ventes"] if v["num"]!=choix]
            save_data()
            st.success("Vente supprimée ✔")
            st.experimental_rerun()
    with col2:
        if st.button("✏ Modifier"):
            st.session_state["editing"] = choix
            st.experimental_rerun()
    with col3:
        st.markdown("### Imprimer")
        option = st.radio("Option", ["Par commande","Tout le tableau"])
        if st.button("📄 Export PDF"):
            if option=="Par commande":
                pdf_bytes = create_pdf_bytes(vente, option="commande")
                if pdf_bytes:
                    st.download_button("Télécharger PDF", pdf_bytes, file_name=f"vente_{vente['num']}.pdf", mime="application/pdf")
            else:
                # TODO: générer PDF de tout le tableau
                st.info("Export PDF complet du tableau à implémenter")
```
