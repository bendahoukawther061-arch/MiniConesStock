if st.button("Enregistrer le stock", key="save_stock"):
    save_data(data)
    st.success("Stock sauvegardé ✔")
    st.rerun()

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

                c1
