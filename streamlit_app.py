import streamlit as st
import json
from datetime import datetime
import os

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
        if pwd.lower() == PASSWORD:
            st.session_state.authenticated = True
            st.success("Connecté ✅")
        else:
            st.error("Mot de passe incorrect ❌")
    st.stop()

# ---------------------------
# DATA FILE
# ---------------------------
DATA_FILE = "stock.json"
DEFAULT_STOCK = {
    "Twine Cones": {"boites": 50, "prix_achat": 10, "prix_vente": 15},
    "Au Lait 50g": {"boites": 70, "prix_achat": 12, "prix_vente": 18},
    "Bueno 70g": {"boites": 60, "prix_achat": 14, "prix_vente": 20},
    "Pistachio": {"boites": 80, "prix_achat": 13, "prix_vente": 19},
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
# UTIL FUNCTIONS
# ---------------------------
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calc_total_from_produits(produits_dict):
    return sum(item["montant"] for item in produits_dict.values())

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

    revendeur = st.text_input("Nom du revendeur")
    chauffeur = st.text_input("Nom du chauffeur")
    frais = st.number_input("Frais", min_value=0.0, value=0.0)

    produits = list(data["stock"].keys())
    vente_produits = {}
    total = 0.0

    st.subheader("Produits")
    for p in produits:
        st.markdown(f"**{p}**")
        qte = st.number_input(f"Quantité (boîtes) {p}", min_value=0, max_value=data["stock"][p]["boites"], step=1, key=f"q_new_{p}")
        prix_vente = st.number_input(f"Prix vente {p}", min_value=0.0, value=float(data["stock"][p]["prix_vente"]), step=0.5, key=f"pr_new_{p}")
        montant = qte * prix_vente
        vente_produits[p] = {
            "qte": qte,
            "prix_vente": prix_vente,
            "prix_achat": data["stock"][p]["prix_achat"],
            "montant": montant
        }
        total += montant

    st.subheader("Résumé")
    st.write(f"Total ventes : {total}")
    caisse = total - frais
    st.write(f"Caisse : {caisse}")

    if st.button("Enregistrer la vente"):
        ok = True
        for p, info in vente_produits.items():
            if info["qte"] > data["stock"][p]["boites"]:
                st.error(f"Stock insuffisant pour {p}. Disponible: {data['stock'][p]['boites']} boîtes.")
                ok = False
        if ok:
            for p, info in vente_produits.items():
                data["stock"][p]["boites"] -= info["qte"]
            vente = {
                "num": num_vente,
                "date": today,
                "revendeur": revendeur,
                "chauffeur": chauffeur,
                "produits": vente_produits,
                "frais": frais,
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
    st.title("Stock actuel")
    for p, s in data["stock"].items():
        st.write(f"**{p}** — Boîtes: {s['boites']} | Prix achat: {s['prix_achat']} | Prix vente: {s['prix_vente']}")

    st.markdown("---")
    st.subheader("Modifier le stock")
    prod = st.selectbox("Produit", list(data["stock"].keys()))
    add_boites = st.number_input("Nombre de boîtes", min_value=0, step=1)
    prix_achat = st.number_input("Prix achat", min_value=0.0, value=data["stock"][prod]["prix_achat"])
    prix_vente = st.number_input("Prix vente", min_value=0.0, value=data["stock"][prod]["prix_vente"])
    if st.button("Mettre à jour le stock"):
        data["stock"][prod]["boites"] = add_boites
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
        total_vente = calc_total_from_produits(v["produits"])
        rows.append({
            "num": v["num"],
            "date": v["date"],
            "revendeur": v.get("revendeur",""),
            "chauffeur": v.get("chauffeur",""),
            "total": total_vente,
            "frais": v.get("frais",0),
            "caisse": v.get("caisse",0)
        })
    df = pd.DataFrame(rows).sort_values(by="num", ascending=False)
    st.dataframe(df, use_container_width=True)

    choix = st.selectbox("Sélectionne N° vente", df["num"])
    vente = next((v for v in data["ventes"] if v["num"] == choix), None)

    col_del, col_mod = st.columns(2)
    with col_del:
        if st.button("❌ Supprimer cette vente"):
            data["ventes"] = [v for v in data["ventes"] if v["num"] != choix]
            save_data()
            st.success("Vente supprimée ✔")
            st.experimental_rerun()

    with col_mod:
        if st.button("✏ Modifier cette vente"):
            st.warning("Modification manuelle dans l'app non implémentée pour simplifier.")

