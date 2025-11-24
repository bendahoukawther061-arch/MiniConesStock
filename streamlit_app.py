import streamlit as st
import json
from datetime import datetime
import os
from PIL import Image

# ---------------------------------------------
# CONFIGURATION
# ---------------------------------------------
st.set_page_config(page_title="Mini Cones", page_icon="🍦")

PASSWORD = "mehdi123"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Connexion")
    pwd = st.text_input("Mot de passe :", type="password")
    if st.button("Valider"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.success("Connecté ✔")
        else:
            st.error("Mot de passe incorrect ❌")
    st.stop()

# ---------------------------------------------
# LOGO
# ---------------------------------------------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=180)
except:
    st.warning("⚠ Logo introuvable (logo.png)")

# ---------------------------------------------
# CHARGEMENT DATA
# ---------------------------------------------
DATA_FILE = "stock.json"

if not os.path.exists(DATA_FILE):
    data = {
        "stock": {
            "Twine Cones": {"boites": 100, "fardeaux": 0},
            "Au Lait 50g": {"boites": 200, "fardeaux": 0},
            "Bueno 70g": {"boites": 150, "fardeaux": 0},
            "Pistachio": {"boites": 180, "fardeaux": 0}
        },
        "ventes": []
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
else:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

# Correction automatique des anciens stocks (au cas où)
for p, q in data["stock"].items():
    if isinstance(q, int):  
        data["stock"][p] = {"boites": q, "fardeaux": 0}

# Sauvegarde après correction
with open(DATA_FILE, "w") as f:
    json.dump(data, f, indent=4)

# ---------------------------------------------
# MENU
# ---------------------------------------------
page = st.sidebar.selectbox("📌 Menu", ["Nouvelle vente", "Stock", "Historique des ventes"])

# ---------------------------------------------
# PAGE 1 : NOUVELLE VENTE
# ---------------------------------------------
if page == "Nouvelle vente":

    st.title("🧾 Nouvelle vente")
    today = datetime.today().strftime("%Y-%m-%d")

    num_vente = 1 if len(data["ventes"]) == 0 else data["ventes"][-1]["num"] + 1
    st.write(f"📅 Date : **{today}**\n🔢 Numéro : **{num_vente}**")

    client = st.text_input("Client")
    dettes = st.number_input("Dette (non payé)", min_value=0.0)
    opérateur = st.text_input("Opérateur")
    chauffeur = st.text_input("Chauffeur")
    frais = st.number_input("Frais", min_value=0.0)

    produits = ["Twine Cones", "Au Lait 50g", "Bueno 70g", "Pistachio"]
    vente_produits = {}
    total_ventes = 0

    st.subheader("🛒 Produits vendus")

    for p in produits:
        st.markdown(f"### {p}")
        unite = st.selectbox(f"Unité", ["Boîte", "Fardeau"], key=f"{p}_u")
        qte = st.number_input("Quantité", min_value=0, step=1, key=f"{p}_q")
        prix = st.number_input("Prix unitaire", min_value=0.0, step=1.0, key=f"{p}_p")

        montant = qte * prix
        total_ventes += montant

        vente_produits[p] = {
            "unite": unite,
            "qte": qte,
            "prix": prix,
            "montant": montant
        }

    caisse = total_ventes - dettes - frais

    st.subheader("📌 Résumé")
    st.write(f"Total ventes : **{total_ventes}**")
    st.write(f"Dette : **{dettes}**")
    st.write(f"Frais : **{frais}**")
    st.write(f"💵 Caisse : **{caisse}**")

    if st.button("💾 Enregistrer la vente"):

        # Mise à jour du stock
        for p in produits:
            u = vente_produits[p]["unite"]
            q = vente_produits[p]["qte"]

            if u == "Boîte":
                data["stock"][p]["boites"] -= q
            else:
                data["stock"][p]["fardeaux"] -= q

        # Sauvegarde des ventes
        vente = {
            "num": num_vente,
            "date": today,
            "client": client,
            "produits": vente_produits,
            "dettes": dettes,
            "operateur": opérateur,
            "chauffeur": chauffeur,
            "frais": frais,
            "caisse": caisse
        }
        data["ventes"].append(vente)

        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        st.success("✔ Vente enregistrée")
        st.balloons()

# ---------------------------------------------
# PAGE 2 : STOCK
# ---------------------------------------------
elif page == "Stock":
    st.title("📦 Stock actuel")

    for p, q in data["stock"].items():
        st.write(f"**{p}** : {q['boites']} boîtes | {q['fardeaux']} fardeaux")

    st.subheader("➕ Ajouter au stock")
    prod = st.selectbox("Produit", list(data["stock"].keys()))
    add_boites = st.number_input("Ajouter boîtes", min_value=0)
    add_fardeaux = st.number_input("Ajouter fardeaux", min_value=0)

    if st.button("📥 Ajouter au stock"):
        data["stock"][prod]["boites"] += add_boites
        data["stock"][prod]["fardeaux"] += add_fardeaux

        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        st.success("Stock mis à jour ✔")

# ---------------------------------------------
# PAGE 3 : HISTORIQUE (SUPPRIMER + MODIFIER)
# ---------------------------------------------
elif page == "Historique des ventes":

    st.title("📜 Historique des ventes")

    if len(data["ventes"]) == 0:
        st.info("Aucune vente enregistrée.")
        st.stop()

    choix = st.selectbox(
        "Sélectionner une vente",
        [f"Vente {v['num']} - {v['date']} - {v['client']}" for v in data["ventes"]]
    )

    index = int(choix.split()[1]) - 1
    vente = data["ventes"][index]

    st.write("### 📌 Détails")
    st.json(vente)

    # ------------------------
    # SUPPRIMER
    # ------------------------
    if st.button("❌ Supprimer cette vente"):
        # Restaurer le stock
        for p, v in vente["produits"].items():
            if v["unite"] == "Boîte":
                data["stock"][p]["boites"] += v["qte"]
            else:
                data["stock"][p]["fardeaux"] += v["qte"]

        # Supprimer la vente
        data["ventes"].pop(index)

        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        st.success("Vente supprimée ✔")
        st.stop()

    # ------------------------
    # MODIFIER
    # ------------------------
    st.subheader("✏ Modifier la vente")

    new_client = st.text_input("Client", vente["client"])
    new_dette = st.number_input("Dette", min_value=0.0, value=float(vente["dettes"]))
    new_frais = st.number_input("Frais", min_value=0.0, value=float(vente["frais"]))

    if st.button("✔ Enregistrer modifications"):

        vente["client"] = new_client
        vente["dettes"] = new_dette
        vente["frais"] = new_frais

        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        st.success("Modifications enregistrées ✔")
