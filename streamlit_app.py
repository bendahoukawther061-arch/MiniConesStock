import streamlit as st
import json
from datetime import datetime
import os
from PIL import Image
import io

# Try to import reportlab for PDF export; fallback possible
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
PASSWORD = "mehdi123"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Mehdi BENDAHOU")
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
    "Twine Cones": {"boites": 50, "fardeaux": 10},
    "Au Lait 50g": {"boites": 70, "fardeaux": 15},
    "Bueno 70g": {"boites": 60, "fardeaux": 12},
    "Pistachio": {"boites": 80, "fardeaux": 20},
}

if not os.path.exists(DATA_FILE):
    data = {"stock": DEFAULT_STOCK, "ventes": []}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
else:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

# Convert old numeric stocks to dicts automatically
for k, v in list(data["stock"].items()):
    if isinstance(v, int):
        data["stock"][k] = {"boites": v, "fardeaux": 0}
# Save after normalization
with open(DATA_FILE, "w") as f:
    json.dump(data, f, indent=4)

# ---------------------------
# UTIL FUNCTIONS
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
    c.drawString(margin, y, f"Opérateur: {vente.get('operateur','')}  Chauffeur: {vente.get('chauffeur','')}")
    y -= 25
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Produits:")
    y -= 18
    c.setFont("Helvetica", 11)
    c.drawString(margin, y, "Produit")
    c.drawString(margin+180, y, "Unité")
    c.drawString(margin+260, y, "Qte")
    c.drawString(margin+320, y, "PU")
    c.drawString(margin+400, y, "Montant")
    y -= 12
    c.line(margin, y, width-margin, y)
    y -= 14
    for prod, info in vente["produits"].items():
        if y < 80:
            c.showPage()
            y = height - margin
        c.drawString(margin, y, prod)
        c.drawString(margin+180, y, info["unite"])
        c.drawString(margin+260, y, str(info["qte"]))
        c.drawString(margin+320, y, str(info["prix"]))
        c.drawString(margin+400, y, str(info["montant"]))
        y -= 16
    y -= 8
    c.line(margin, y, width-margin, y)
    y -= 18
    c.drawString(margin, y, f"Total: {calc_total_from_produits(vente['produits'])}")
    y -= 18
    c.drawString(margin, y, f"Dettes: {vente.get('dettes',0)}   Frais: {vente.get('frais',0)}")
    y -= 18
    c.drawString(margin, y, f"Caisse: {vente.get('caisse',0)}")
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

def create_html_bytes(vente):
    total = calc_total_from_produits(vente["produits"])
    html = f"""
    <html><head><meta charset="utf-8"><title>Reçu Vente {vente['num']}</title></head>
    <body>
      <h2>Mini Cones — Reçu de vente</h2>
      <p><b>N° Vente:</b> {vente['num']} &nbsp;&nbsp; <b>Date:</b> {vente['date']}</p>
      <p><b>Client:</b> {vente.get('client','')}</p>
      <table border="1" cellpadding="6" cellspacing="0">
        <tr><th>Produit</th><th>Unité</th><th>Quantité</th><th>PU</th><th>Montant</th></tr>
    """
    for prod, info in vente["produits"].items():
        html += f"<tr><td>{prod}</td><td>{info['unite']}</td><td>{info['qte']}</td><td>{info['prix']}</td><td>{info['montant']}</td></tr>"
    html += f"""
      </table>
      <p><b>Total:</b> {total}</p>
      <p><b>Dette:</b> {vente.get('dettes',0)} &nbsp; <b>Frais:</b> {vente.get('frais',0)} &nbsp; <b>Caisse:</b> {vente.get('caisse',0)}</p>
    </body></html>
    """
    return html.encode("utf-8")

# ---------------------------
# MENU SELECTION
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
    dettes = st.number_input("Dette (non payé)", min_value=0.0, value=0.0)
    operateur = st.text_input("Opérateur")
    chauffeur = st.text_input("Chauffeur")
    frais = st.number_input("Frais", min_value=0.0, value=0.0)

    produits = list(data["stock"].keys())
    vente_produits = {}
    total = 0.0

    st.subheader("Produits")
    for p in produits:
        st.markdown(f"**{p}**")
        unite = st.selectbox(f"Unité {p}", ["Boîte", "Fardeau"], key=f"u_new_{p}")
        qte = st.number_input(f"Quantité {p}", min_value=0, step=1, key=f"q_new_{p}")
        prix = st.number_input(f"Prix unitaire {p}", min_value=0.0, step=0.5, key=f"pr_new_{p}")
        montant = qte * prix
        vente_produits[p] = {"unite": unite, "qte": qte, "prix": prix, "montant": montant}
        total += montant

    caisse = total - dettes - frais
    st.subheader("Résumé")
    st.write(f"Total ventes : {total}")
    st.write(f"Caisse : {caisse}")

    if st.button("Enregistrer la vente"):
        ok = True
        for p, info in vente_produits.items():
            if info["unite"] == "Boîte" and info["qte"] > data["stock"][p]["boites"]:
                st.error(f"Stock insuffisant pour {p} en boîtes.")
                ok = False
            if info["unite"] == "Fardeau" and info["qte"] > data["stock"][p]["fardeaux"]:
                st.error(f"Stock insuffisant pour {p} en fardeaux.")
                ok = False
        if ok:
            for p, info in vente_produits.items():
                if info["unite"] == "Boîte":
                    data["stock"][p]["boites"] -= info["qte"]
                else:
                    data["stock"][p]["fardeaux"] -= info["qte"]
            vente = {
                "num": num_vente,
                "date": today,
                "client": client,
                "produits": vente_produits,
                "dettes": dettes,
                "operateur": operateur,
                "chauffeur": chauffeur,
                "frais": frais,
                "caisse": caisse
            }
            data["ventes"].append(vente)
            save_data()
            st.success("Vente enregistrée ✔")
            st.rerun()  # <-- remplacé experimental_rerun

# ---------------------------
# STOCK PAGE
# ---------------------------
elif page == "Stock":
    st.title("Stock")
    for p, s in data["stock"].items():
        st.write(f"**{p}** — Boîtes: {s['boites']} | Fardeaux: {s['fardeaux']}")

    st.markdown("---")
    st.subheader("Ajouter au stock")
    prod = st.selectbox("Produit", list(data["stock"].keys()))
    add_boites = st.number_input("Boîtes à ajouter", min_value=0, step=1)
    add_fardeaux = st.number_input("Fardeaux à ajouter", min_value=0, step=1)
    if st.button("Ajouter au stock"):
        data["stock"][prod]["boites"] += add_boites
        data["stock"][prod]["fardeaux"] += add_fardeaux
        save_data()
        st.success("Stock mis à jour ✔")
        st.rerun()  # <-- remplacé experimental_rerun

# ---------------------------
# HISTORIQUE PAGE
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
            "total": calc_total_from_produits(v["produits"]),
            "caisse": v.get("caisse",0)
        })
    df = pd.DataFrame(rows).sort_values(by="num", ascending=False)
    st.dataframe(df[["num","date","client","total","caisse"]].rename(
        columns={"num":"N°","date":"Date","client":"Client","total":"Total","caisse":"Caisse"}
    ), use_container_width=True)

    st.markdown("---")
    st.subheader("Gérer une vente")
    nums = [v["num"] for v in data["ventes"]]
    choix = st.selectbox("Sélectionne N° vente", nums, index=0)

    vente = next((v for v in data["ventes"] if v["num"] == choix), None)
    if vente is None:
        st.error("Vente introuvable.")
        st.stop()

    col_del, col_mod, col_pdf = st.columns([1,1,1])
    with col_del:
        if st.button("❌ Supprimer"):
            for prod, info in vente["produits"].items():
                if info["unite"] == "Boîte":
                    data["stock"][prod]["boites"] += info["qte"]
                else:
                    data["stock"][prod]["fardeaux"] += info["qte"]
            data["ventes"] = [v for v in data["ventes"] if v["num"] != choix]
            save_data()
            st.success("Vente supprimée ✔")
            st.rerun()  # <-- remplacé experimental_rerun

    with col_mod:
        if st.button("✏ Modifier"):
            st.session_state["editing"] = choix
            st.rerun()  # <-- remplacé experimental_rerun

    with col_pdf:
        if st.button("📄 Export PDF / HTML"):
            pdf_bytes = create_pdf_bytes(vente) if REPORTLAB_AVAILABLE else None
            if pdf_bytes:
                st.download_button("Télécharger le PDF", data=pdf_bytes, file_name=f"vente_{vente['num']}.pdf", mime="application/pdf")
            else:
                html_bytes = create_html_bytes(vente)
                st.download_button("Télécharger le reçu (HTML)", data=html_bytes, file_name=f"vente_{vente['num']}.html", mime="text/html")
            st.success("Préparation terminée — téléchargez votre reçu")

    if "editing" in st.session_state and st.session_state["editing"] == choix:
        st.markdown("## ✍️ Modifier la vente (tous les champs)")
        original = vente
        for prod, info in original["produits"].items():
            if info["unite"] == "Boîte":
                data["stock"][prod]["boites"] += info["qte"]
            else:
                data["stock"][prod]["fardeaux"] += info["qte"]

        new_client = st.text_input("Client", value=original.get("client",""))
        new_operateur = st.text_input("Opérateur", value=original.get("operateur",""))
        new_chauffeur = st.text_input("Chauffeur", value=original.get("chauffeur",""))
        new_dettes = st.number_input("Dette", min_value=0.0, value=float(original.get("dettes",0)))
        new_frais = st.number_input("Frais", min_value=0.0, value=float(original.get("frais",0)))

        st.markdown("### Produits (modifie quantité / prix / unité)")
        new_produits = {}
        for prod, info in original["produits"].items():
            st.markdown(f"**{prod}**")
            new_unite = st.selectbox(f"Unité {prod}", ["Boîte","Fardeau"], index=0 if info["unite"]=="Boîte" else 1, key=f"edit_u_{prod}")
            new_qte = st.number_input(f"Quantité {prod}", min_value=0, value=int(info["qte"]), key=f"edit_q_{prod}")
            new_prix = st.number_input(f"Prix unitaire {prod}", min_value=0.0, value=float(info["prix"]), step=0.5, key=f"edit_pr_{prod}")
            new_montant = new_qte * new_prix
            new_produits[prod] = {"unite": new_unite, "qte": new_qte, "prix": new_prix, "montant": new_montant}
            st.write(f"Montant: {new_montant}")

        if st.button("💾 Enregistrer modifications"):
            ok = True
            for prod, info in new_produits.items():
                if info["unite"] == "Boîte" and info["qte"] > data["stock"][prod]["boites"]:
                    st.error(f"Stock insuffisant pour {prod} (boîtes). Disponible: {data['stock'][prod]['boites']}")
                    ok = False
                if info["unite"] == "Fardeau" and info["qte"] > data["stock"][prod]["fardeaux"]:
                    st.error(f"Stock insuffisant pour {prod} (fardeaux). Disponible: {data['stock'][prod]['fardeaux']}")
                    ok = False
            if ok:
                for prod, info in new_produits.items():
                    if info["unite"] == "Boîte":
                        data["stock"][prod]["boites"] -= info["qte"]
                    else:
                        data["stock"][prod]["fardeaux"] -= info["qte"]
                total_new = calc_total_from_produits(new_produits)
                new_caisse = total_new - new_dettes - new_frais
                updated = {
                    "num": original["num"],
                    "date": original["date"],
                    "client": new_client,
                    "produits": new_produits,
                    "dettes": new_dettes,
                    "operateur": new_operateur,
                    "chauffeur": new_chauffeur,
                    "frais": new_frais,
                    "caisse": new_caisse
                }
                for i, v in enumerate(data["ventes"]):
                    if v["num"] == original["num"]:
                        data["ventes"][i] = updated
                        break
                save_data()
                st.success("Modifications enregistrées ✔")
                del st.session_state["editing"]
                st.rerun()  # <-- remplacé experimental_rerun

