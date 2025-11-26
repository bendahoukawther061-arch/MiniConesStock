import streamlit as st
import json
from datetime import datetime
import os
from PIL import Image
import io
import pandas as pd

# Try to import reportlab for PDF export; fallback to HTML if not available
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    REPORTLAB_AVAILABLE = True
except Exception:
    REPORTLAB_AVAILABLE = False

# ---------------------------
# CONFIG & AUTH (title changed to "bendahou mehdi")
# ---------------------------
st.set_page_config(page_title="Mini Cones", page_icon="🍦")

PASSWORD = "mehdi123"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("bendahou mehdi")  # <-- title requested
    pwd = st.text_input("Entrez le mot de passe :", type="password")
    if st.button("Valider"):
        if pwd == PASSWORD:
            st.session_state.authenticated = True
            st.success("Connecté ✅")
        else:
            st.error("Mot de passe incorrect ❌")
    st.stop()

# ---------------------------
# Files and products
# ---------------------------
DATA_FILE = "stock.json"
PRODUITS = ["Twine Cones", "Au Lait 50g", "Bueno 70g", "Pistachio", "Crepes"]
FARDEAU_TO_BOITES = 6  # Option A: fixed conversion

# Initialize data file if missing
if not os.path.exists(DATA_FILE):
    data = {
        "stock": {p: 100 for p in PRODUITS},  # all stock expressed as boxes
        "ventes": []
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
else:
    with open(DATA_FILE, "r") as f:
        data = json.load(f)

# Ensure stock keys exist (safe upgrade)
for p in PRODUITS:
    if p not in data["stock"]:
        data["stock"][p] = 0

# ---------------------------
# Helpers
# ---------------------------
def save_data():
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def calc_total_from_produits(prod_dict):
    return sum(item.get("montant", 0) for item in prod_dict.values())

def calc_margin_from_produits(prod_dict):
    # each item: prix_achat (per box), prix_vente (per box), qte_boite
    total_margin = 0.0
    for item in prod_dict.values():
        pa = float(item.get("prix_achat", 0.0))
        pv = float(item.get("prix_vente", 0.0))
        q = float(item.get("qte_boite", 0))
        total_margin += (pv - pa) * q
    return total_margin

def create_pdf_bytes_for_vente(vente):
    """Create a PDF (bytes) for a single vente. Use reportlab if available, else return None."""
    if not REPORTLAB_AVAILABLE:
        return None
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    margin = 40
    y = h - margin
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(w/2, y, "Mini Cones - Bon de livraison")
    y -= 30
    c.setFont("Helvetica", 11)
    c.drawString(margin, y, f"N° Vente: {vente['num']}")
    c.drawRightString(w - margin, y, f"Date: {vente['date']}")
    y -= 18
    c.drawString(margin, y, f"Client: {vente.get('client','')}")
    y -= 18
    c.drawString(margin, y, f"Revendeur: {vente.get('revendeur','')}  (Frais: {vente.get('frais_revendeur',0)})")
    y -= 16
    c.drawString(margin, y, f"Chauffeur: {vente.get('chauffeur','')}  (Frais: {vente.get('frais_chauffeur',0)})")
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Produit")
    c.drawString(margin+180, y, "Unité")
    c.drawString(margin+260, y, "Qte(boxes)")
    c.drawString(margin+340, y, "PA")
    c.drawString(margin+400, y, "PV")
    c.drawString(margin+470, y, "Montant")
    y -= 12
    c.line(margin, y, w-margin, y)
    y -= 16
    c.setFont("Helvetica", 11)
    for prod, info in vente["produits"].items():
        if y < 100:
            c.showPage()
            y = h - margin
        c.drawString(margin, y, prod)
        c.drawString(margin+180, y, info.get("unite","Boîte"))
        c.drawRightString(margin+300, y, str(info.get("qte_boite", 0)))
        c.drawRightString(margin+380, y, f"{float(info.get('prix_achat',0)):.2f}")
        c.drawRightString(margin+440, y, f"{float(info.get('prix_vente',0)):.2f}")
        c.drawRightString(margin+520, y, f"{float(info.get('montant',0)):.2f}")
        y -= 16
    y -= 8
    c.line(margin, y, w-margin, y)
    y -= 20
    c.drawString(margin, y, f"Total ventes: {vente.get('total',0):.2f} DA")
    y -= 16
    c.drawString(margin, y, f"Frais total: {vente.get('frais_total',0):.2f} DA")
    y -= 16
    c.drawString(margin, y, f"Caisse: {vente.get('caisse',0):.2f} DA")
    y -= 16
    c.drawString(margin, y, f"Marge totale: {calc_margin_from_produits(vente['produits']):.2f} DA")
    c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

def create_pdf_bytes_all_ventes(ventes_list):
    """Create a single PDF with all ventes (one sale per page)."""
    if not REPORTLAB_AVAILABLE:
        return None
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4
    margin = 40
    for vente in ventes_list:
        y = h - margin
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(w/2, y, f"Mini Cones - Vente N°{vente['num']}")
        y -= 30
        c.setFont("Helvetica", 11)
        c.drawString(margin, y, f"Date: {vente['date']}")
        y -= 16
        c.drawString(margin, y, f"Client: {vente.get('client','')}")
        y -= 14
        c.drawString(margin, y, f"Revendeur: {vente.get('revendeur','')}  (Frais: {vente.get('frais_revendeur',0)})")
        y -= 14
        c.drawString(margin, y, f"Chauffeur: {vente.get('chauffeur','')}  (Frais: {vente.get('frais_chauffeur',0)})")
        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y, "Produit")
        c.drawString(margin+180, y, "Unité")
        c.drawString(margin+260, y, "Qte(boxes)")
        c.drawString(margin+340, y, "PA")
        c.drawString(margin+400, y, "PV")
        c.drawString(margin+470, y, "Montant")
        y -= 12
        c.line(margin, y, w-margin, y)
        y -= 16
        c.setFont("Helvetica", 11)
        for prod, info in vente["produits"].items():
            if y < 100:
                c.showPage()
                y = h - margin
            c.drawString(margin, y, prod)
            c.drawString(margin+180, y, info.get("unite","Boîte"))
            c.drawRightString(margin+300, y, str(info.get("qte_boite", 0)))
            c.drawRightString(margin+380, y, f"{float(info.get('prix_achat',0)):.2f}")
            c.drawRightString(margin+440, y, f"{float(info.get('prix_vente',0)):.2f}")
            c.drawRightString(margin+520, y, f"{float(info.get('montant',0)):.2f}")
            y -= 16
        y -= 8
        c.line(margin, y, w-margin, y)
        y -= 16
        c.drawString(margin, y, f"Total ventes: {vente.get('total',0):.2f} DA")
        y -= 14
        c.drawString(margin, y, f"Frais total: {vente.get('frais_total',0):.2f} DA")
        y -= 14
        c.drawString(margin, y, f"Caisse: {vente.get('caisse',0):.2f} DA")
        y -= 14
        c.drawString(margin, y, f"Marge totale: {calc_margin_from_produits(vente['produits']):.2f} DA")
        c.showPage()
    c.save()
    buf.seek(0)
    return buf.read()

def create_html_for_vente(vente):
    total = vente.get("total",0)
    margin = calc_margin_from_produits(vente["produits"])
    html = f"<html><head><meta charset='utf-8'><title>Vente {vente['num']}</title></head><body>"
    html += f"<h2>Mini Cones - Vente N°{vente['num']}</h2>"
    html += f"<p>Date: {vente['date']}</p>"
    html += f"<p>Client: {vente.get('client','')}</p>"
    html += "<table border='1' cellpadding='6'><tr><th>Produit</th><th>Unité</th><th>Qte(boxes)</th><th>PA</th><th>PV</th><th>Montant</th></tr>"
    for prod, info in vente["produits"].items():
        html += f"<tr><td>{prod}</td><td>{info.get('unite','Boîte')}</td><td>{info.get('qte_boite',0)}</td><td>{info.get('prix_achat',0)}</td><td>{info.get('prix_vente',0)}</td><td>{info.get('montant',0)}</td></tr>"
    html += "</table>"
    html += f"<p>Total: {total}</p>"
    html += f"<p>Frais total: {vente.get('frais_total',0)}</p>"
    html += f"<p>Caisse: {vente.get('caisse',0)}</p>"
    html += f"<p>Marge: {margin}</p>"
    html += "</body></html>"
    return html.encode("utf-8")

def create_html_for_all(ventes_list):
    html = "<html><head><meta charset='utf-8'><title>Historique complet</title></head><body>"
    html += "<h1>Historique des ventes - Mini Cones</h1>"
    for vente in ventes_list:
        html += f"<h2>Vente N°{vente['num']} - {vente['date']}</h2>"
        html += "<table border='1' cellpadding='5'><tr><th>Produit</th><th>Unité</th><th>Qte(boxes)</th><th>PA</th><th>PV</th><th>Montant</th></tr>"
        for prod, info in vente["produits"].items():
            html += f"<tr><td>{prod}</td><td>{info.get('unite','Boîte')}</td><td>{info.get('qte_boite',0)}</td><td>{info.get('prix_achat',0)}</td><td>{info.get('prix_vente',0)}</td><td>{info.get('montant',0)}</td></tr>"
        html += "</table>"
        html += f"<p>Total: {vente.get('total',0)} - Frais total: {vente.get('frais_total',0)} - Caisse: {vente.get('caisse',0)} - Marge: {calc_margin_from_produits(vente['produits'])}</p>"
        html += "<hr>"
    html += "</body></html>"
    return html.encode("utf-8")

# ---------------------------
# UI: show logo if present
# ---------------------------
try:
    logo = Image.open("logo.png")
    st.image(logo, width=180)
except Exception:
    pass

# ---------------------------
# MAIN MENU
# ---------------------------
page = st.sidebar.selectbox("Menu", ["Nouvelle vente", "Stock", "Historique"])

# ---------------------------
# PAGE: Nouvelle vente
# ---------------------------
if page == "Nouvelle vente":
    st.title("🛒 Nouvelle vente ")

    num_vente = 1 if len(data["ventes"]) == 0 else data["ventes"][-1]["num"] + 1
    today = datetime.today().strftime("%Y-%m-%d")
    st.write(f"Date: {today} — N° {num_vente}")

    client = st.text_input("Client")

    # Revendeur + frais
    revendeur = st.text_input("Revendeur (nom)")
    frais_revendeur = st.number_input("Frais revendeur", min_value=0.0, value=0.0, step=1.0)

    # Chauffeur + frais
    chauffeur = st.text_input("Chauffeur (nom)")
    frais_chauffeur = st.number_input("Frais chauffeur", min_value=0.0, value=0.0, step=1.0)

    frais_total = frais_revendeur + frais_chauffeur
    st.info(f"Frais total calculé: {frais_total} DA")

    st.markdown("----")
    st.subheader("Produits — pour chaque produit, sa quantité (boîtes) ou fardeaux pour Twine Cones")
    vente_produits = {}
    total = 0.0

    for p in PRODUITS:
        st.markdown(f"**{p}**")
        # Twine Cones: allow unit choice
        if p == "Twine Cones":
            unite = st.selectbox(f"Unité pour {p}", ["Boîte", "Fardeau"], key=f"unit_{p}")
            if unite == "Fardeau":
                q_input = st.number_input(f"Quantité en fardeaux ({p})", min_value=0, step=1, key=f"q_f_{p}")
                q_boites = q_input * FARDEAU_TO_BOITES
            else:
                q_boites = st.number_input(f"Quantité en boîtes ({p})", min_value=0, step=1, key=f"q_b_{p}")
        else:
            unite = "Boîte"
            q_boites = st.number_input(f"Quantité en boîtes ({p})", min_value=0, step=1, key=f"q_b_{p}")

        prix_achat = st.number_input(f"Prix d'achat par boîte ({p})", min_value=0.0, step=0.5, key=f"pa_{p}")
        prix_vente = st.number_input(f"Prix de vente par boîte ({p})", min_value=0.0, step=0.5, key=f"pv_{p}")

        montant = float(prix_vente) * float(q_boites)
        total += montant
        vente_produits[p] = {
            "unite": unite,
            "qte_boite": int(q_boites),
            "prix_achat": float(prix_achat),
            "prix_vente": float(prix_vente),
            "montant": montant
        }
        st.write(f"Montant {p}: {montant:.2f} DA — Marge unitaire: {prix_vente - prix_achat:.2f} DA — Marge totale: {(prix_vente - prix_achat) * q_boites:.2f} DA")

    caisse = total - frais_total
    marge_totale = calc_margin_from_produits(vente_produits)

    st.markdown("----")
    st.write(f"Total ventes: {total:.2f} DA")
    st.write(f"Total marge: {marge_totale:.2f} DA")
    st.success(f"Caisse finale: {caisse:.2f} DA")

    if st.button("Enregistrer la vente"):
        # Validate stock (no negative)
        ok = True
        for prod, info in vente_produits.items():
            if info["qte_boite"] > data["stock"].get(prod, 0):
                st.error(f"Stock insuffisant pour {prod}: dispo {data['stock'].get(prod,0)} boîtes, demandé {info['qte_boite']}")
                ok = False
        if ok:
            # Deduct stock
            for prod, info in vente_produits.items():
                data["stock"][prod] = data["stock"].get(prod,0) - info["qte_boite"]
            vente = {
                "num": num_vente,
                "date": today,
                "client": client,
                "revendeur": revendeur,
                "frais_revendeur": frais_revendeur,
                "chauffeur": chauffeur,
                "frais_chauffeur": frais_chauffeur,
                "frais_total": frais_total,
                "produits": vente_produits,
                "total": total,
                "caisse": caisse
            }
            data["ventes"].append(vente)
            save_data()
            st.success("Vente enregistrée ✔")
            st.rerun()

# ---------------------------
# PAGE: Stock (editable by user)
# ---------------------------
elif page == "Stock":
    st.title("📦 Stock (en boîtes) — modifie manuellement")

    st.markdown("**Quantités actuelles :**")
    cols = st.columns(2)
    i = 0
    for p in PRODUITS:
        cols[i%2].write(f"{p} : {data['stock'].get(p,0)} boîtes")
        i += 1

    st.markdown("---")
    st.subheader("Modifier le stock manuellement")
    prod_to_edit = st.selectbox("Choisir le produit", PRODUITS)
    new_qty = st.number_input("Nouvelle quantité (boîtes)", min_value=0, value=int(data['stock'].get(prod_to_edit,0)), step=1)
    if st.button("Mettre à jour le stock"):
        data['stock'][prod_to_edit] = int(new_qty)
        save_data()
        st.success("Stock mis à jour ✔")
        st.rerun()

# ---------------------------
# PAGE: Historique (tableau + actions + imprimer)
# ---------------------------
elif page == "Historique":
    st.title("📜 Historique des ventes")

    if len(data["ventes"]) == 0:
        st.info("Aucune vente enregistrée.")
        st.stop()

    # Dataframe for summary
    rows = []
    for v in data["ventes"]:
        rows.append({
            "Num": v["num"],
            "Date": v["date"],
            "Client": v.get("client",""),
            "Total": v.get("total",0),
            "Caisse": v.get("caisse",0),
            "Marge": calc_margin_from_produits(v["produits"])
        })
    df = pd.DataFrame(rows).sort_values(by="Num", ascending=False)
    st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("Gérer / Imprimer")

    choix = st.number_input("Numéro de vente (pour modifier/supprimer/imprimer)", min_value=1, step=1)
    vente = next((v for v in data["ventes"] if v["num"] == choix), None)
    if not vente:
        st.warning("Choisis un numéro existant pour gérer la vente.")
    else:
        c1, c2, c3, c4 = st.columns([1,1,1,1])
        with c1:
            if st.button("✏ Modifier cette vente"):
                st.session_state["edit_num"] = choix
                st.rerun()
        with c2:
            if st.button("🗑 Supprimer cette vente"):
                # restore stock
                for prod, info in vente["produits"].items():
                    data['stock'][prod] = data['stock'].get(prod,0) + int(info.get("qte_boite",0))
                data["ventes"] = [v for v in data["ventes"] if v["num"] != choix]
                save_data()
                st.success("Vente supprimée ✔")
                st.rerun()
        with c3:
            if st.button("📄 Imprimer cette vente (PDF/HTML)"):
                pdf_bytes = create_pdf_bytes_for_vente(vente) if REPORTLAB_AVAILABLE else None
                if pdf_bytes:
                    st.download_button("Télécharger PDF (cette vente)", data=pdf_bytes, file_name=f"vente_{vente['num']}.pdf", mime="application/pdf")
                else:
                    html = create_html_for_vente(vente)
                    st.download_button("Télécharger reçu (HTML)", data=html, file_name=f"vente_{vente['num']}.html", mime="text/html")
        with c4:
            if st.button("📄 Imprimer tout l'historique (PDF/HTML)"):
                pdf_all = create_pdf_bytes_all_ventes(data["ventes"]) if REPORTLAB_AVAILABLE else None
                if pdf_all:
                    st.download_button("Télécharger PDF (toutes ventes)", data=pdf_all, file_name="historique_ventes.pdf", mime="application/pdf")
                else:
                    html_all = create_html_for_all(data["ventes"])
                    st.download_button("Télécharger historique (HTML)", data=html_all, file_name="historique_ventes.html", mime="text/html")

# ---------------------------
# PAGE: Editing a sale (modal behavior via session_state)
# ---------------------------
if "edit_num" in st.session_state:
    edit_num = st.session_state["edit_num"]
    vente = next((v for v in data["ventes"] if v["num"] == edit_num), None)
    if vente:
        st.markdown("---")
        st.title(f"✍️ Modifier la vente N°{edit_num}")

        client = st.text_input("Client", value=vente.get("client",""))
        revendeur = st.text_input("Revendeur", value=vente.get("revendeur",""))
        frais_revendeur = st.number_input("Frais revendeur", min_value=0.0, value=float(vente.get("frais_revendeur",0)), step=1.0)
        chauffeur = st.text_input("Chauffeur", value=vente.get("chauffeur",""))
        frais_chauffeur = st.number_input("Frais chauffeur", min_value=0.0, value=float(vente.get("frais_chauffeur",0)), step=1.0)
        frais_total = frais_revendeur + frais_chauffeur
        st.info(f"Frais total: {frais_total} DA")

        st.subheader("Produits (quantités en boîtes)")
        new_prods = {}
        total_new = 0.0
        for p in PRODUITS:
            old = vente["produits"].get(p, {})
            q_old = int(old.get("qte_boite", 0))
            pa_old = float(old.get("prix_achat", 0.0))
            pv_old = float(old.get("prix_vente", 0.0))
            q_new = st.number_input(f"{p} - Quantité (boîtes)", min_value=0, value=q_old, key=f"edit_q_{p}")
            pa_new = st.number_input(f"{p} - Prix d'achat par boîte", min_value=0.0, value=pa_old, step=0.5, key=f"edit_pa_{p}")
            pv_new = st.number_input(f"{p} - Prix de vente par boîte", min_value=0.0, value=pv_old, step=0.5, key=f"edit_pv_{p}")
            mont = q_new * pv_new
            new_prods[p] = {
                "unite": "Boîte",
                "qte_boite": int(q_new),
                "prix_achat": float(pa_new),
                "prix_vente": float(pv_new),
                "montant": mont
            }
            total_new += mont
            st.write(f"{p} - Montant: {mont:.2f} DA — Marge: {(pv_new - pa_new) * q_new:.2f} DA")

        caisse_new = total_new - frais_total

        if st.button("Enregistrer modifications"):
            # restore stock from original sale then apply new deduction
            # first add back original quantities
            for prod, info in vente["produits"].items():
                data['stock'][prod] = data['stock'].get(prod,0) + int(info.get("qte_boite",0))
            # validate new stock availability
            ok = True
            for prod, info in new_prods.items():
                if info["qte_boite"] > data['stock'].get(prod,0):
                    st.error(f"Stock insuffisant pour {prod}: dispo {data['stock'].get(prod,0)} boîtes, demandé {info['qte_boite']}")
                    ok = False
            if ok:
                # apply new deduction
                for prod, info in new_prods.items():
                    data['stock'][prod] = data['stock'].get(prod,0) - int(info['qte_boite'])
                # update vente
                vente['client'] = client
                vente['revendeur'] = revendeur
                vente['frais_revendeur'] = frais_revendeur
                vente['chauffeur'] = chauffeur
                vente['frais_chauffeur'] = frais_chauffeur
                vente['frais_total'] = frais_total
                vente['produits'] = new_prods
                vente['total'] = total_new
                vente['caisse'] = caisse_new
                save_data()
                del st.session_state['edit_num']
                st.success("Modifications enregistrées ✔")
                st.rerun()
    else:
        st.error("La vente à modifier n'existe plus.")
        del st.session_state['edit_num']
        st.rerun()

