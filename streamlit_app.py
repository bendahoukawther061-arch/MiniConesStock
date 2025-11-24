import streamlit as st
import json
import os

# Nom du fichier de stockage
STOCK_FILE = "stock_data.json"

# Fonction pour charger le stock depuis JSON
def load_stock():
    if os.path.exists(STOCK_FILE):
        with open(STOCK_FILE, "r") as f:
            return json.load(f)
    else:
        # Stock initial par défaut
        return {
            "Chocolat": {"boites": 0, "fardeaux": 0},
            "Pistache": {"boites": 0, "fardeaux": 0},
            "Bueno": {"boites": 0, "fardeaux": 0}
        }

# Fonction pour sauvegarder le stock
def save_stock(stock):
    with open(STOCK_FILE, "w") as f:
        json.dump(stock, f, indent=4)

# Charger le stock
stock = load_stock()

st.title("Gestion du stock Mini Cones 🍦")

# Formulaire pour mettre à jour le stock
with st.form("update_stock"):
    st.header("Ajouter / Modifier les quantités")
    
    for produit in stock.keys():
        st.subheader(produit)
        stock[produit]["boites"] = st.number_input(f"{produit} (boîtes)", 
                                                   value=stock[produit]["boites"], min_value=0, step=1)
        stock[produit]["fardeaux"] = st.number_input(f"{produit} (fardeaux)", 
                                                     value=stock[produit]["fardeaux"], min_value=0, step=1)
    
    submit = st.form_submit_button("Mettre à jour le stock")
    
    if submit:
        save_stock(stock)
        st.success("Stock mis à jour avec succès ! ✅")

# Affichage du stock actuel
st.header("Stock actuel")
for produit, quantites in stock.items():
    st.write(f"{produit} : {quantites['boites']} boîtes, {quantites['fardeaux']} fardeaux")
