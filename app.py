import streamlit as st

st.set_page_config(page_title="Université Peniel", page_icon="🎓")

st.title("🎓 Université Peniel")
st.write("Bienvenue sur l'application de l'université !")

menu = st.sidebar.selectbox("Menu", ["Accueil", "Inscription Étudiant", "Liste des Étudiants"])

if menu == "Accueil":
    st.header("Accueil")
    st.write("Cette application permet de gérer les étudiants de l'université.")
    st.success("L'application fonctionne !")

elif menu == "Inscription Étudiant":
    st.header("Inscription Étudiant")
    nom = st.text_input("Nom complet")
    filiere = st.selectbox("Filière", ["Informatique", "Droit", "Médecine", "Gestion", "Autre"])
    annee = st.selectbox("Année", ["L1", "L2", "L3", "M1", "M2"])
    if st.button("Inscrire"):
        if nom:
            st.success(f"Étudiant {nom} inscrit en {filiere} - {annee} !")
        else:
            st.error("Écris le nom d'abord !")

elif menu == "Liste des Étudiants":
    st.header("Liste des Étudiants")
    st.write("Ici, on verra bientôt la liste des étudiants inscrits.")
    st.info("Pour l'instant, la liste est vide.")
