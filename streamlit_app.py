import streamlit as st
import json
import os
from datetime import datetime
from PIL import Image
import io



st.set_page_config(page_title="Mini Cones", page_icon="")
PASSWORD = "bendahou mehdi"

if "authenticated" not in st.session_state:
st.session_state.authenticated = False

if not st.session_state.authenticated:
st.title(" Connexion")
pwd = st.text_input("Mot de passe", type="password")
if st.button("Valider"):
if pwd.lower() == PASSWORD:
st.session_state.authenticated = True
st.success("Connecté ")
else:
st.error("Mot de passe incorrect ")
st.stop()



LOGO


try:
logo = Image.open("logo.png")
st.image(logo, width=180)
except:
st.warning("Logo introuvable — continue sans logo.")


DATA FILE


DATA_FILE = "stock.json"
DEFAULT_STOCK = {
"Twine Cones": {"boites": 50, "prix_achat": 100, "prix_vente": 150},
"Au Lait 50g": {"boites": 70, "prix_achat": 50, "prix_vente": 80},
"Bueno 70g": {"boites": 60, "prix_achat": 60, "prix_vente": 90},
"Pistachio": {"boites": 80, "prix_achat": 70, "prix_vente": 110},
"Crepes": {"boites": 40, "prix_achat": 40, "prix_vente": 60}
}

if not os.path.exists(DATA_FILE):
data = {"stock": DEFAULT_STOCK, "ventes": []}
with open(DATA_FILE, "w") as f:
json.dump(data, f, indent=4)
else:
with open(DATA_FILE, "r") as f:
data = json.load(f)



UTIL FUNCTIONS

def save_data():
with open(DATA_FILE, "w") as f:
json.dump(data, f, indent=4)

def calc_total_from_produits(produits_dict):
return sum(item["montant"] for item in produits_dict.values())

def calc_total_marge(produits_dict):
return sum((item["prix_vente"] - item["prix_achat"]) * item["qte_boite"] for item in produits_dict.values())



MENU SELECTION

page = st.sidebar.selectbox("Menu", ["Stock", "Nouvelle vente", "Historique"])


STOCK PAGE


if page == "Stock":
st.title("Stock actuel")
for p, s in data["stock"].items():
st.write(f"{p} — Boîtes: {s['boites']} | Prix achat: {s['prix_achat']} | Prix vente: {s['prix_vente']} | Marge: {s['prix_vente'] - s['prix_achat']}")
st.markdown("---")
st.subheader("Modifier / Ajouter au stock")
prod = st.selectbox("Produit", list(data["stock"].keys()))
add_boites = st.number_input("Boîtes à ajouter", min_value=0, step=1)
add_prix_achat = st.number_input("Prix d'achat", value=data["stock"][prod]["prix_achat"])
add_prix_vente = st.number_input("Prix de vente", value=data["stock"][prod]["prix_vente"])
if st.button("Mettre à jour le stock"):
data["stock"][prod]["boites"] += add_boites
data["stock"][prod]["prix_achat"] = add_prix_achat
data["stock"][prod]["prix_vente"] = add_prix_vente
save_data()
st.success("Stock mis à jour ")
st.experimental_rerun()

NOUVELLE VENTE


elif page == "Nouvelle vente":
st.title("Nouvelle vente")
num_vente = 1 if len(data["ventes"]) == 0 else data["ventes"][-1]["num"] + 1
today = datetime.today().strftime("%Y-%m-%d")
st.write(f"Date: {today} — N° {num_vente}")

revendeur = st.text_input("Revendeur")
chauffeur = st.text_input("Chauffeur")
st.write("Frais calculés automatiquement: 10% du total de la vente")

produits = list(data["stock"].keys())
vente_produits = {}

st.subheader("Produits")
total = 0
for p in produits:
    qte_boite = st.number_input(f"Quantité de {p} (boîtes)", min_value=0, step=1, key=p)
    prix_achat = data["stock"][p]["prix_achat"]
    prix_vente = data["stock"][p]["prix_vente"]
    montant = qte_boite * prix_vente
    vente_produits[p] = {"qte_boite": qte_boite, "prix_achat": prix_achat, "prix_vente": prix_vente, "montant": montant}
    total += montant

frais = total * 0.1  # 10% frais
caisse = total - frais
marge = calc_total_marge(vente_produits)

st.subheader("Résumé")
st.write(f"Total vente: {total}")
st.write(f"Frais (10%): {frais}")
st.write(f"Caisse: {caisse}")
st.write(f"Marge totale: {marge}")

if st.button("Enregistrer la vente"):
    ok = True
    for p, info in vente_produits.items():
        if info["qte_boite"] > data["stock"][p]["boites"]:
            st.error(f"Stock insuffisant pour {p}. Disponible: {data['stock'][p]['boites']} boîtes")
            ok = False
    if ok:
        for p, info in vente_produits.items():
            data["stock"][p]["boites"] -= info["qte_boite"]
        vente = {
            "num": num_vente,
            "date": today,
            "revendeur": revendeur,
            "chauffeur": chauffeur,
            "produits": vente_produits,
            "frais": frais,
            "caisse": caisse,
            "total": total,
            "marge": marge
        }
        data["ventes"].append(vente)
        save_data()
        st.success("Vente enregistrée ")
        st.experimental_rerun()


HISTORIQUE PAGE


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
        "revendeur": v.get("revendeur",""),
        "chauffeur": v.get("chauffeur",""),
        "total": v["total"],
        "frais": v["frais"],
        "caisse": v["caisse"],
        "marge": v["marge"]
    })
df = pd.DataFrame(rows).sort_values(by="num", ascending=False)
st.dataframe(df, use_container_width=True)

choix = st.selectbox("Sélectionne N° vente pour actions", df["num"])
vente = next((v for v in data["ventes"] if v["num"] == choix), None)
if vente:
    col1, col2 = st.columns(2)
    with col1:
        if st.button(" Supprimer la vente"):
            for p, info in vente["produits"].items():
                data["stock"][p]["boites"] += info["qte_boite"]
            data["ventes"] = [v for v in data["ventes"] if v["num"] != choix]
            save_data()
            st.success("Vente supprimée ")
            st.experimental_rerun()
    with col2:
        if st.button(" Modifier la vente"):
            st.info("Pour l'instant, modification à coder séparément.")

Note: Export PDF/HTML peut être ajouté avec reportlab et option de tout le tableau ou par commande.

