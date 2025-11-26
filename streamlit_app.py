import streamlit as st
import json
import os

STOCK_FILE = "stock.json"


# ------------------------------
#     FONCTIONS JSON STOCK
# ------------------------------
def load_stock():
    if not os.path.exists(STOCK_FILE):
        return {}
    with open(STOCK_FILE, "r") as f:
        return json.load(f)


def save_stock(stock):
    with open(STOCK_FILE, "w") as f:
        json.dump(stock, f, indent=4)


# ------------------------------
#        AUTHENTIFICATION
# ------------------------------
def login():
    st.title("🔐 Connexion")

    user = st.text_input("Nom d'utilisateur")
    pwd = st.text_input("Mot de passe", type="password")

    if st.button("Se connecter"):
        if user == "admin" and pwd == "mehdi123":
            st.session_state.authenticated = True
            st.success("Connecté avec succès !")
        else:
            st.error("Identifiants incorrects.")


# ------------------------------
#        PAGE STOCK
# ------------------------------
def page_stock():
    st.title("📦 Gestion du Stock")

    stock = load_stock()

    st.subheader("➕ Ajouter un produit")

    nom = st.text_input("Nom du produit")
    boites = st.number_input("Nombre de boîtes", min_value=0, step=1)
    prix_achat = st.number_input("Prix d'achat (DA)", min_value=0.0)
    prix_vente = st.number_input("Prix de vente (DA)", min_value=0.0)

    if st.button("Ajouter au stock"):
        if nom == "":
            st.error("Veuillez entrer un nom.")
        else:
            stock[nom] = {
                "boites": boites,
                "prix_achat": prix_achat,
                "prix_vente": prix_vente
            }
            save_stock(stock)
            st.success("Produit ajouté !")

    st.subheader("📋 Stock actuel")

    if not stock:
        st.info("Aucun produit dans le stock.")
        return

    for nom, data in stock.items():
        marge = data["prix_vente"] - data["prix_achat"]

        st.write(f"""
        **{nom}**
        - Boîtes : {data['boites']}
        - Prix d'achat : {data['prix_achat']} DA
        - Prix de vente : {data['prix_vente']} DA
        - 💰 **Marge : {marge} DA**
        """)

        if st.button(f"Supprimer {nom}"):
            del stock[nom]
            save_stock(stock)
            st.warning(f"{nom} supprimé.")
            st.rerun()


# ------------------------------
#        APPLICATION
# ------------------------------
def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        login()
        return

    st.sidebar.title("Menu")
    choix = st.sidebar.selectbox("Navigation", ["Stock"])

    if choix == "Stock":
        page_stock()


main()
