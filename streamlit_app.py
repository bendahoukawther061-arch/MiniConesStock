import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
from fpdf import FPDF
from io import BytesIO

# ------------------------------
# Configuration
# ------------------------------
st.set_page_config(page_title="Mini Cones", page_icon="🍦", layout="wide")

# CSS theme pastel/chocolat
page_bg = """
<style>
.stApp {
  background: linear-gradient(135deg, #ffe6f2 0%, #fff8fd 40%, #f7e6d5 80%);
}
.stButton>button {
  background-color: #b56576 !important;
  color: white !important;
  border-radius: 12px !important;
  font-size: 15px;
  height: 2.6em;
}
.stDownloadButton>button {
  background-color: #6d6875 !important;
  color: white !important;
  border-radius: 10px !important;
}
h1,h2,h3,h4 { color: #b56576 !important; font-weight: 700 !important; }
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ------------------------------
# Files & initial data
# ------------------------------
DATA_FILE = "stock.json"
AUTO_DIR = "historique_auto"

if not os.path.exists(AUTO_DIR):
    os.makedirs(AUTO_DIR)

def load_data():
    if not os.path.exists(DATA_FILE):
        # initial sample stock (you can edit prices here)
        data0 = {
            "stock": {
                "Twine Cones": {"boites": 0, "prix_achat": 0.0, "prix_vente": 200.0},
                "Cones Pistache": {"boites": 0, "prix_achat": 0.0, "prix_vente": 250.0},
                "Bueno au Lait": {"boites": 0, "prix_achat": 0.0, "prix_vente": 220.0},
                "Crêpes": {"boites": 0, "prix_achat": 0.0, "prix_vente": 180.0}
            },
            "ventes": [],
            "last_export_date": ""  # yyyy-mm-dd
        }
        with open(DATA_FILE, "w") as f:
            json.dump(data0, f, indent=4)
        return data0
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_data()

# ------------------------------
# PDF generation helpers
# ------------------------------
def generate_pdf_bytes(ventes):
    """
    Retourne bytes du PDF (dest='S') pour st.download_button
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Historique des ventes - Mini Cones", ln=True, align="C")
    pdf.ln(4)
    pdf.set_font("Arial", "", 11)

    if not ventes:
        pdf.cell(0, 8, "Aucune vente enregistrée.", ln=True)
    else:
        for v in ventes:
            pdf.set_font("Arial", "B", 12)
            pdf.cell(0, 8, f"Commande N°{v.get('num','?')} - {v.get('date','')}", ln=True)
            pdf.set_font("Arial", "", 11)
            client = v.get("client","")
            rev = v.get("revendeur","")
            chauf = v.get("chauffeur","")
            pdf.cell(0, 6, f"Client: {client} | Revendeur: {rev} | Chauffeur: {chauf}", ln=True)
            frais = v.get("frais", {})
            if frais:
                pdf.cell(0,6, f"Frais -> Revendeur: {frais.get('revendeur',0)} DA - Van: {frais.get('van',0)} DA - Chauffeur: {frais.get('chauffeur',0)} DA (Total: {frais.get('total_frais',0)} DA)", ln=True)
            pdf.ln(1)
            # produits
            for prod, info in v.get("produits", {}).items():
                q = info.get("qte", 0)
                pa = info.get("prix_achat", 0)
                pv = info.get("prix_vente", 0)
                montant = info.get("montant", 0)
                marge = info.get("benefice", None)
                line = f" - {prod}: Qte={q} | Achat={pa} DA | Vente={pv} DA | Montant={montant} DA"
                if marge is not None:
                    line += f" | Marge={marge} DA"
                pdf.cell(0,6, line, ln=True)
            pdf.ln(4)
    # return bytes
    pdf_str = pdf.output(dest='S')  # string
    return pdf_str.encode('latin1')

def save_pdf_file_daily(ventes):
    """
    Sauvegarde un fichier PDF dans AUTO_DIR si pas encore sauvegardé aujourd'hui.
    """
    today = date.today().isoformat()
    if data.get("last_export_date") == today:
        return  # déjà exporté aujourd'hui
    filename = os.path.join(AUTO_DIR, f"historique_{today}.pdf")
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Historique des ventes - Mini Cones", ln=True, align="C")
    pdf.ln(4)
    pdf.set_font("Arial", "", 11)
    for v in ventes:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, f"Commande N°{v.get('num','?')} - {v.get('date','')}", ln=True)
        pdf.set_font("Arial", "", 11)
        client = v.get("client","")
        rev = v.get("revendeur","")
        chauf = v.get("chauffeur","")
        pdf.cell(0, 6, f"Client: {client} | Revendeur: {rev} | Chauffeur: {chauf}", ln=True)
        frais = v.get("frais", {})
        if frais:
            pdf.cell(0,6, f"Frais -> Revendeur: {frais.get('revendeur',0)} DA - Van: {frais.get('van',0)} DA - Chauffeur: {frais.get('chauffeur',0)} DA (Total: {frais.get('total_frais',0)} DA)", ln=True)
        pdf.ln(1)
        for prod, info in v.get("produits", {}).items():
            q = info.get("qte", 0)
            pa = info.get("prix_achat", 0)
            pv = info.get("prix_vente", 0)
            montant = info.get("montant", 0)
            marge = info.get("benefice", None)
            line = f" - {prod}: Qte={q} | Achat={pa} DA | Vente={pv} DA | Montant={montant} DA"
            if marge is not None:
                line += f" | Marge={marge} DA"
            pdf.cell(0,6, line, ln=True)
        pdf.ln(4)
    pdf.output(filename)  # write file
    data["last_export_date"] = today
    save_data(data)

# Run daily auto-save (when the app is opened)
try:
    save_pdf_file_daily(data.get("ventes", []))
except Exception as e:
    # ne pas planter l'app si l'export automatique échoue
    st.warning("Auto-export quotidien : erreur (voir logs).")

# ------------------------------
# Simple login
# ------------------------------
if 'login' not in st.session_state:
    st.session_state['login'] = False

if not st.session_state['login']:
    # show logo if present
    if os.path.exists("logo.png"):
        st.image("logo.png", width=200)
    st.subheader("🔒 Connexion")
    username = st.text_input("Nom d'utilisateur", key="login_user")
    password = st.text_input("Mot de passe", type="password", key="login_pass")
    if st.button("Se connecter", key="login_btn"):
        # identifiants par défaut (change si nécessaire)
        if username.strip().lower() in ["bendahou", "bendahou mehdi", "mehdi"] and password == "mehdi123":
            st.session_state['login'] = True
            st.success("Connecté ✔")
            st.experimental_rerun()
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect")
    st.stop()

# ------------------------------
# Sidebar navigation
# ------------------------------
if os.path.exists("logo.png"):
    st.sidebar.image("logo.png", width=100)
page = st.sidebar.radio("Navigation", ["Commandes", "Stock", "Historique"])

# ------------------------------
# PAGE: COMMANDES
# ------------------------------
if page == "Commandes":
    st.title("🧾 Nouvelle Commande")

    # numéro automatique
    last_num = data["ventes"][-1]["num"] if data["ventes"] else 0
    num = last_num + 1
    date_now = datetime.now().strftime("%Y-%m-%d %H:%M")

    st.write(f"Commande N° {num} — {date_now}")

    # informations client/frais
    col1, col2 = st.columns(2)
    with col1:
        client = st.text_input("Client", key="client")
        revendeur = st.text_input("Revendeur", key="revendeur")
    with col2:
        chauffeur = st.text_input("Chauffeur", key="chauffeur")

    colf1, colf2, colf3 = st.columns(3)
    frais_revendeur = colf1.number_input("Frais revendeur (DA)", min_value=0.0, value=0.0, key="frais_rev")
    frais_van = colf2.number_input("Frais van (DA)", min_value=0.0, value=0.0, key="frais_van")
    frais_chauffeur = colf3.number_input("Frais chauffeur (DA)", min_value=0.0, value=0.0, key="frais_chauf")
    total_frais = round(frais_revendeur + frais_van + frais_chauffeur, 2)

    st.info(f"Total frais : {total_frais} DA")

    # Produits : loop with unique keys
    st.subheader("Produits")
    vente_produits = {}
    total_ventes = 0.0

    for prod_name, prod_info in data["stock"].items():
        st.markdown(f"**{prod_name}**")
        colp1, colp2, colp3 = st.columns([2,2,2])
        q_key = f"q_{prod_name}"
        type_key = f"type_{prod_name}"
        # only Twine Cones has option Box / Fardeau
        if prod_name == "Twine Cones":
            type_choice = colp1.selectbox("Unité", ["Box", "Fardeau"], key=type_key)
        else:
            type_choice = "Box"

        qte = colp2.number_input("Quantité", min_value=0, value=0, step=1, key=q_key)
        # convert fardeau to box (6 box)
        if prod_name == "Twine Cones" and type_choice == "Fardeau":
            effective_qte = qte * 6
        else:
            effective_qte = qte

        # use stock price values (read-only here)
        pv = float(prod_info.get("prix_vente", 0))
        pa = float(prod_info.get("prix_achat", 0))
        montant = round(effective_qte * pv, 2)
        benefice_prod = round(effective_qte * (pv - pa), 2)

        # show price summary
        colp3.write(f"Prix vente: {pv} DA")
        colp3.write(f"Achat: {pa} DA")
        colp3.write(f"Montant: {montant} DA")

        if effective_qte > 0:
            vente_produits[prod_name] = {
                "qte": int(effective_qte),
                "prix_vente": pv,
                "prix_achat": pa,
                "montant": montant,
                "benefice": benefice_prod
            }
            total_ventes += montant

    st.subheader("Récapitulatif")
    st.write(f"Total produits: **{round(total_ventes,2)} DA**")
    st.write(f"Total frais: **{total_frais} DA**")
    marge_total = round(total_ventes - total_frais - sum(p["prix_achat"]*p["qte"] for p in vente_produits.values()), 2)
    st.success(f"Marge estimée: **{marge_total} DA**")

    if st.button("Enregistrer la commande", key="save_commande"):
        if not vente_produits:
            st.error("Ajoute au moins un produit (quantité>0).")
        else:
            vente = {
                "num": num,
                "date": date_now,
                "client": client,
                "revendeur": revendeur,
                "chauffeur": chauffeur,
                "frais": {
                    "revendeur": frais_revendeur,
                    "van": frais_van,
                    "chauffeur": frais_chauffeur,
                    "total_frais": total_frais
                },
                "produits": vente_produits,
                "total_ventes": round(total_ventes,2),
                "marge": marge_total
            }
            # update stock quantities (decrease)
            for pname, pinfo in vente_produits.items():
                # check stock safety
                if data["stock"].get(pname):
                    data["stock"][pname]["boites"] = max(0, data["stock"][pname]["boites"] - pinfo["qte"])
            data["ventes"].append(vente)
            save_data(data)
            st.success("Commande enregistrée ✔")
            # export today's pdf file if not already saved
            try:
                save_pdf_file_daily(data.get("ventes", []))
            except:
                pass
            st.experimental_rerun()

# ------------------------------
# PAGE: STOCK
# ------------------------------
if page == "Stock":
    st.title("📦 Gestion du stock")
    st.write("Mets à jour quantité (boîtes) et prix (achat / vente).")
    for pname, pinfo in data["stock"].items():
        st.subheader(pname)
        c1, c2, c3 = st.columns([2,1.5,1.5])
        new_boites = c1.number_input(f"Boîtes ({pname})", min_value=0, value=int(pinfo.get("boites",0)), key=f"boites_{pname}")
        new_pa = c2.number_input(f"Prix achat ({pname})", min_value=0.0, value=float(pinfo.get("prix_achat",0.0)), key=f"pa_{pname}")
        new_pv = c3.number_input(f"Prix vente ({pname})", min_value=0.0, value=float(pinfo.get("prix_vente",0.0)), key=f"pv_{pname}")
        data["stock"][pname]["boites"] = int(new_boites)
        data["stock"][pname]["prix_achat"] = float(new_pa)
        data["stock"][pname]["prix_vente"] = float(new_pv)
    if st.button("Enregistrer le stock", key="save_stock"):
        save_data(data)
        st.success("Stock sauvegardé ✔")
        st.experimental_rerun()

# ------------------------------
# PAGE: HISTORIQUE
# ------------------------------
if page == "Historique":
    st.title("📜 Historique des ventes")
    if not data.get("ventes"):
        st.info("Aucune vente.")
    else:
        # show all ventes as expandable items with table
        for idx, vente in enumerate(data["ventes"]):
            with st.expander(f"N°{vente['num']} — {vente['date']} — Total {vente.get('total_ventes',0)} DA"):
                st.write(f"Client: **{vente.get('client','')}**")
                st.write(f"Revendeur: **{vente.get('revendeur','')}**, Chauffeur: **{vente.get('chauffeur','')}**")
                st.write("Frais:", vente.get("frais", {}))
                # build dataframe for produits
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

                c1, c2, c3 = st.columns([1,1,1])
                if c1.button("Modifier (éditer quantités)", key=f"hist_mod_{idx}"):
                    # simple inline edit: allow updating quantities
                    st.session_state[f"edit_idx"] = idx
                    st.experimental_rerun()
                if c2.button("Supprimer", key=f"hist_del_{idx}"):
                    data["ventes"].pop(idx)
                    save_data(data)
                    st.success("Vente supprimée ✔")
                    st.experimental_rerun()
                # if in edit mode and matches this index show editors
                if st.session_state.get("edit_idx") == idx:
                    st.info("Mode édition: change les quantités et clique Sauvegarder.")
                    edited = {}
                    for row in rows:
                        k = row["Produit"]
                        newq = st.number_input(f"Nouvelle quantité - {k}", min_value=0, value=int(row["Quantité"]), key=f"edit_q_{idx}_{k}")
                        edited[k] = int(newq)
                    if st.button("Sauvegarder modification", key=f"save_edit_{idx}"):
                        # apply changes
                        vente_obj = data["ventes"][idx]
                        for pname, newq in edited.items():
                            if pname in vente_obj["produits"]:
                                p = vente_obj["produits"][pname]
                                p["qte"] = int(newq)
                                p["montant"] = round(p["prix_vente"] * p["qte"],2)
                                p["benefice"] = round((p["prix_vente"] - p["prix_achat"]) * p["qte"],2)
                        # recalc totals and save
                        vente_obj["total_ventes"] = round(sum(p["montant"] for p in vente_obj["produits"].values()),2)
                        vente_obj["marge"] = round(vente_obj["total_ventes"] - vente_obj.get("frais",{}).get("total_frais",0) - sum(p["prix_achat"]*p["qte"] for p in vente_obj["produits"].values()),2)
                        save_data(data)
                        st.success("Modification sauvegardée ✔")
                        # exit edit mode
                        st.session_state.pop("edit_idx", None)
                        st.experimental_rerun()

        # download the entire historique as PDF (bytes)
        pdf_bytes = generate_pdf_bytes(data.get("ventes", []))
        st.download_button("📄 Télécharger l'historique (PDF)", pdf_bytes, file_name="historique_mini_cones.pdf", mime="application/pdf")

# ------------------------------
# End of app
# ------------------------------
