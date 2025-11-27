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
# CSS Thème clair
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
    st.title("🧾 Nouvelle Commande")
    num = 1 if len(data["ventes"]) == 0 else data["ventes"][-1]["num"] + 1
    date = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.write(f"**Commande N° {num} — {date}**")

    col1, col2 = st.columns(2)
    with col1:
        client = st.text_input("Client")
        revendeur = st.text_input("Revendeur")
        prix_revendeur = st.number_input("Frais Revendeur (DA)", min_value=0.0, key="charge_rev")
    with col2:
        chauffeur = st.text_input("Chauffeur")
        prix_chauffeur = st.number_input("Frais Chauffeur (DA)", min_value=0.0, key="charge_chauffeur")

    charge_van = st.number_input("Frais Van (DA)", min_value=0.0, key="charge_van")
    autres = st.number_input("Autres frais (DA)", min_value=0.0, key="charge_autres")
    total_frais = prix_revendeur + prix_chauffeur + charge_van + autres
    st.info(f"🔸 Total frais : **{total_frais} DA**")

    st.subheader("🧃 Produits")
    vente_produits = {}
    total_ventes = 0

    for produit, info in data["stock"].items():
        st.markdown(f"### {produit}")
        colA, colB = st.columns(2)
        qte = 0
        if produit == "Twine Cones":
            type_qte = colA.selectbox(f"Type pour {produit}", ["Box", "Fardeau"], key=f"type_{produit}")
            qte = colB.number_input(f"Quantité", min_value=0, step=1, key=f"qte_{produit}")
            if type_qte == "Fardeau":
                qte *= 6
        else:
            qte = colB.number_input(f"Quantité", min_value=0, step=1, key=f"qte_{produit}")

        montant = qte * info["prix_vente"]
        benefice = (info["prix_vente"] - info["prix_achat"]) * qte
        total_ventes += montant

        vente_produits[produit] = {
            "qte": qte,
            "prix_achat": info["prix_achat"],
            "prix_vente": info["prix_vente"],
            "montant": montant,
            "benefice": benefice
        }

    st.subheader("📊 Résultat")
    st.write(f"💰 Total ventes : **{total_ventes} DA**")
    st.write(f"💸 Total frais : **{total_frais} DA**")
    st.success(f"🟢 Bénéfice : **{total_ventes - total_frais} DA**")

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
            "benefice_total": total_ventes - total_frais
        }
        data["ventes"].append(vente)
        save_data(data)
        st.success("Commande enregistrée ✔")
        st.experimental_rerun()

# ------------------------------
# PAGE STOCK
# ------------------------------
if page == "Stock":
    st.title("📦 Stock actuel des produits")
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

    if st.button("Enregistrer le stock"):
        save_data(data)
        st.success("Stock sauvegardé ✔")
        st.experimental_rerun()

# ------------------------------
# PAGE HISTORIQUE
# ------------------------------
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
                        "Marge": pinfo.get("benefice",0)
                    })
                df = pd.DataFrame(rows)
                st.dataframe(df)

                # Modification ou suppression
                c1, c2 = st.columns([1,1])
                if c1.button("Modifier quantités", key=f"hist_mod_{idx}"):
                    st.session_state["edit_idx"] = idx
                    st.experimental_rerun()
                if c2.button("Supprimer", key=f"hist_del_{idx}"):
                    data["ventes"].pop(idx)
                    save_data(data)
                    st.success("Vente supprimée ✔")
                    st.experimental_rerun()

                # Mode édition
                if st.session_state.get("edit_idx") == idx:
                    st.info("Mode édition: change les quantités et clique Sauvegarder.")
                    edited = {}
                    for row in rows:
                        k = row["Produit"]
                        newq = st.number_input(f"Nouvelle quantité - {k}", min_value=0, value=int(row["Quantité"]), key=f"edit_q_{idx}_{k}")
                        edited[k] = int(newq)
                    if st.button("Sauvegarder modification", key=f"save_edit_{idx}"):
                        vente_obj = data["ventes"][idx]
                        for pname, newq in edited.items():
                            if pname in vente_obj["produits"]:
                                p = vente_obj["produits"][pname]
                                p["qte"] = int(newq)
                                p["montant"] = round(p["prix_vente"] * p["qte"],2)
                                p["benefice"] = round((p["prix_vente"] - p["prix_achat"]) * p["qte"],2)
                        vente_obj["total_ventes"] = round(sum(p["montant"] for p in vente_obj["produits"].values()),2)
                        vente_obj["benefice_total"] = round(vente_obj["total_ventes"] - vente_obj.get("frais",{}).get("total_frais",0),2)
                        save_data(data)
                        st.success("Modification sauvegardée ✔")
                        st.session_state.pop("edit_idx", None)
                        st.experimental_rerun()
