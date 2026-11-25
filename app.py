import streamlit as st
import hashlib
import time
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="MIT Tunis - Monplaisir", page_icon="🎓", layout="wide")

ADMIN_HASH = hashlib.sha256("MIT2026".encode()).hexdigest()
def verifier_mdp(mdp):
    return hashlib.sha256(mdp.encode()).hexdigest() == ADMIN_HASH

st.markdown("""
<style>
.main { background-color: #F0F6FF; }
h1, h2, h3 { color: #0B3D91 !important; }
.stButton>button { background-color: #0B3D91; color: white; border-radius: 12px; font-weight: bold; }
.admin-box { background-color: #FFE8E8; padding: 15px; border-radius: 12px; border: 2px solid red; }
</style>
""", unsafe_allow_html=True)

lang = st.sidebar.selectbox("🌍 Langue / Language / اللغة", ["Français", "English", "العربية"])
T = {
"Français": {"titre":"Mediterranean Institute of Tunisia","sous":"MIT Tunis - Monplaisir | Excellence, Innovation, Avenir","bienvenue":"Bienvenue au MIT Tunis - Monplaisir","formations":"Nos Formations","biblio":"📚 Bibliothèque","etudiants":"👨‍🎓 Étudiants (Excel)","events":"🎉 Événements","test":"📝 Test Étudiants","admin":"🔐 Admin","recherche":"Rechercher un livre, auteur...","admin_titre":"Zone Administrative","mdp_label":"Mot de passe Admin","bienvenue_admin":"Bienvenue Administrateur","ajouter_livre":"Ajouter un livre","excel_titre":"Importer Excel Étudiants","excel_info":"Ton fichier Excel doit avoir les colonnes : Nom | Prénom | Email | Filière | Note | ID (ID Unique)","deconnexion":"Se déconnecter","test_titre":"Test de Connaissances","nom_label":"Ton nom complet","valider":"Valider mon test"},
"English": {"titre":"Mediterranean Institute of Tunisia","sous":"MIT Tunis - Monplaisir | Excellence, Innovation, Future","bienvenue":"Welcome to MIT Tunis - Monplaisir","formations":"Our Programs","biblio":"📚 Library","etudiants":"👨‍🎓 Students (Excel)","events":"🎉 Events","test":"📝 Student Test","admin":"🔐 Admin","recherche":"Search a book, author...","admin_titre":"Admin Area","mdp_label":"Admin Password","bienvenue_admin":"Welcome Administrator","ajouter_livre":"Add a book","excel_titre":"Import Students Excel","excel_info":"Your Excel must have columns : Nom | Prénom | Email | Filière | Note | ID","deconnexion":"Log out","test_titre":"Knowledge Test","nom_label":"Your full name","valider":"Submit my test"},
"العربية": {"titre":"معهد البحر الأبيض المتوسط بتونس","sous":"MIT Tunis - Monplaisir | التميز، الابتكار، المستقبل","bienvenue":"مرحباً بكم في MIT Tunis","formations":"برامجنا","biblio":"📚 المكتبة","etudiants":"👨‍🎓 الطلاب (Excel)","events":"🎉 الفعاليات","test":"📝 اختبار الطلاب","admin":"🔐 الإدارة","recherche":"ابحث عن كتاب...","admin_titre":"منطقة الإدارة","mdp_label":"كلمة مرور الإدارة","bienvenue_admin":"مرحباً أيها المدير","ajouter_livre":"إضافة كتاب","excel_titre":"استيراد Excel للطلاب","excel_info":"يجب أن يحتوي ملف Excel على: Nom | Prénom | Email | Filière | Note | ID","deconnexion":"تسجيل الخروج","test_titre":"اختبار المعرفة","nom_label":"اسمك الكامل","valider":"تأكيد الاختبار"},
}
t = T[lang]

LIVRES_DE_BASE = [
    {"titre": "Python pour débutants", "auteur": "A. Ben Ali", "filiere": "Génie Logiciel", "annee": 2023, "dispo": True},
    {"titre": "Apprendre Python en 30 jours", "auteur": "S. Gharbi", "filiere": "Génie Logiciel", "annee": 2024, "dispo": True},
    {"titre": "Algorithme et Langage C", "auteur": "M. Trabelsi", "filiere": "Génie Logiciel", "annee": 2022, "dispo": True},
    {"titre": "Développement Web - HTML, CSS, JS", "auteur": "Y. Mansour", "filiere": "Génie Logiciel", "annee": 2024, "dispo": False},
    {"titre": "Développement Mobile Flutter", "auteur": "K. Ayari", "filiere": "Génie Logiciel", "annee": 2024, "dispo": True},
    {"titre": "Intelligence Artificielle pour tous", "auteur": "L. Ben Salah", "filiere": "Génie Logiciel", "annee": 2025, "dispo": True},
    {"titre": "Bases de Données SQL & MySQL", "auteur": "S. Gharbi", "filiere": "Systèmes d'Information", "annee": 2023, "dispo": True},
    {"titre": "Réseaux Informatiques - CCNA", "auteur": "K. Ayari", "filiere": "Systèmes d'Information", "annee": 2023, "dispo": False},
    {"titre": "Cybersécurité Essentielle", "auteur": "M. Haddad", "filiere": "Systèmes d'Information", "annee": 2025, "dispo": True},
    {"titre": "Cloud Computing & AWS", "auteur": "A. Kefi", "filiere": "Systèmes d'Information", "annee": 2024, "dispo": True},
    {"titre": "Management des Entreprises", "auteur": "N. Ben Ahmed", "filiere": "Management", "annee": 2023, "dispo": True},
    {"titre": "Marketing Digital", "auteur": "R. Slim", "filiere": "Management", "annee": 2024, "dispo": True},
    {"titre": "Comptabilité & Finance", "auteur": "F. Bouzid", "filiere": "Management", "annee": 2022, "dispo": True},
    {"titre": "Entrepreneuriat en Tunisie", "auteur": "Y. Ben Romdhane", "filiere": "Management", "annee": 2025, "dispo": True},
    {"titre": "Communication Professionnelle", "auteur": "S. Mejri", "filiere": "Management", "annee": 2023, "dispo": True},
    {"titre": "Mathématiques pour l'Informatique", "auteur": "H. Karray", "filiere": "Génie Logiciel", "annee": 2024, "dispo": True},
    {"titre": "Anglais pour Informaticiens", "auteur": "E. Ben Youssef", "filiere": "Management", "annee": 2023, "dispo": True},
    {"titre": "Python Facile - Le Guide Pratique", "auteur": "MIT Tunis", "filiere": "Génie Logiciel", "annee": 2026, "dispo": True,
     "lire": "📖 CHAPITRE 1 - Commencer en Python\n\nPython c'est comme parler à l'ordinateur.\n\nPour dire Bonjour, tu écris :\nprint('Bonjour')\n\nPour calculer :\nprint(2 + 3) -> ça donne 5\n\nPour poser une question :\nprenom = input('Ton prénom ?')\nprint('Bonjour', prenom)\n\nEXERCICE CHEZ TOI :\n1. Ouvre ton téléphone ou ton PC\n2. Va sur python.org ou utilise ton app\n3. Essaie print('Je suis étudiant MIT')\n\nBravo, tu as fait ton premier programme !"},
    {"titre": "HTML & CSS - Crée ton premier site", "auteur": "MIT Tunis", "filiere": "Génie Logiciel", "annee": 2026, "dispo": True,
     "lire": "📖 CHAPITRE 1 - Ton premier site en 5 minutes\n\nHTML = la structure, comme les murs d'une maison.\nCSS = la décoration, comme la peinture.\n\nTon premier site :\n<html>\n<h1>Bonjour, je suis étudiant MIT</h1>\n<p>Je vais créer mon site</p>\n</html>\n\nEXERCICE CHEZ TOI :\n1. Crée un fichier test.html\n2. Colle ce code dedans\n3. Ouvre-le dans Chrome\n\nTu viens de créer ton premier site web !"},
    {"titre": "Les Bases de l'Algorithme", "auteur": "MIT Tunis", "filiere": "Génie Logiciel", "annee": 2026, "dispo": True,
     "lire": "📖 CHAPITRE 1 - C'est quoi un algorithme ?\n\nUn algorithme = une recette de cuisine, étape par étape.\n\nExemple : Faire un thé\n1. Prendre de l'eau\n2. Faire bouillir l'eau\n3. Mettre le thé\n4. Servir\n\nEn informatique c'est pareil :\n1. Demander le nom\n2. Demander la note\n3. Si note >= 10 -> Réussi\n4. Sinon -> Échoué\n\nEXERCICE : Écris l'algorithme pour aller de chez toi à MIT Tunis, étape par étape."},
]

QUESTIONS = [
    {"q": "1. En Python, comment on affiche 'Bonjour' ?", "options": ["print('Bonjour')", "echo Bonjour", "show('Bonjour')"], "bonne": "print('Bonjour')"},
    {"q": "2. Quel symbole on utilise pour un commentaire en Python ?", "options": ["//", "#", "/*"], "bonne": "#"},
    {"q": "3. Combien font 2 * 3 en Python ?", "options": ["5", "6", "23"], "bonne": "6"},
    {"q": "4. HTML sert à quoi ?", "options": ["Créer la structure d'une page web", "Faire des calculs", "Gérer la base de données"], "bonne": "Créer la structure d'une page web"},
    {"q": "5. Quelle est la capitale de la Tunisie ?", "options": ["Sfax", "Tunis", "Sousse"], "bonne": "Tunis"},
]

if "livres" not in st.session_state: st.session_state.livres = LIVRES_DE_BASE.copy()
if "etudiants_df" not in st.session_state: st.session_state.etudiants_df = None
if "resultats" not in st.session_state: st.session_state.resultats = []
if "connecte" not in st.session_state: st.session_state.connecte = False
if "tentatives" not in st.session_state: st.session_state.tentatives = 0
if "bloque_jusqua" not in st.session_state: st.session_state.bloque_jusqua = 0
if "etudiant_verifie" not in st.session_state: st.session_state.etudiant_verifie = False
if "etudiant_nom" not in st.session_state: st.session_state.etudiant_nom = ""
if "etudiant_id" not in st.session_state: st.session_state.etudiant_id = ""
if "ids_autorises" not in st.session_state: st.session_state.ids_autorises = ["MIT-2026-PENIEL", "MIT-001", "MIT-002"]

def verifier_id_unique(id_tape):
    id_tape = str(id_tape).strip().upper()
    if not id_tape:
        return False, ""
    if st.session_state.etudiants_df is not None:
        df = st.session_state.etudiants_df
        for col in df.columns:
            if str(col).lower() in ["id", "id unique", "code", "email", "matricule"]:
                valeurs = df[col].astype(str).str.strip().str.upper().tolist()
                if id_tape in valeurs:
                    ligne = df[df[col].astype(str).str.strip().str.upper() == id_tape]
                    nom_trouve = ""
                    for c in ["Nom", "Prénom", "Prenom", "Name"]:
                        if c in df.columns:
                            nom_trouve += str(ligne.iloc[0][c]) + " "
                    return True, nom_trouve.strip()
        return False, ""
    if id_tape in [x.upper() for x in st.session_state.ids_autorises]:
        return True, "Étudiant MIT"
    return False, ""

# ===== HEADER =====
st.markdown("<div style='text-align: center; font-size: 90px; margin-bottom: -20px;'>🎓</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #0B3D91; font-weight: bold; font-size: 18px;'>MIT TUNIS - MONPLAISIR</div>", unsafe_allow_html=True)
st.title(t["titre"])
st.subheader(t["sous"])
st.write(f"### {t['bienvenue']}")

# ===== VUE ADMIN EN HAUT - SEUL ADMIN VOIT CA =====
if st.session_state.connecte:
    st.markdown("<div class='admin-box'><h3>👑 MODE ADMIN - Vue Administrateur</h3><p>Tu vois tout. Les étudiants ne voient pas cette partie.</p></div>", unsafe_allow_html=True)
    nb_etudiants = len(st.session_state.etudiants_df) if st.session_state.etudiants_df is not None else 0
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("👨‍🎓 Étudiants inscrits", nb_etudiants)
    a2.metric("📚 Livres", len(st.session_state.livres))
    a3.metric("🔑 IDs créés", len(st.session_state.ids_autorises))
    a4.metric("📝 Tests passés", len(st.session_state.resultats))
    with st.expander("👁️ Voir le tableau Admin complet", expanded=False):
        st.write("**📋 Étudiants Excel :**")
        if st.session_state.etudiants_df is not None:
            st.dataframe(st.session_state.etudiants_df, use_container_width=True)
        else:
            st.info("Aucun Excel importé. Va dans l'onglet Admin pour importer.")
        st.write("**🔑 IDs autorisés :**")
        st.write(", ".join(st.session_state.ids_autorises))
        st.write("**📝 Résultats Tests :**")
        if len(st.session_state.resultats) > 0:
            st.dataframe(pd.DataFrame(st.session_state.resultats), use_container_width=True)
        else:
            st.info("Aucun test passé.")
    st.divider()
else:
    # Vue publique : on cache le nombre d'étudiants
    c1, c2, c3 = st.columns(3)
    c1.metric("📚 Livres", len(st.session_state.livres))
    c2.metric("📝 Tests passés", len(st.session_state.resultats))
    c3.metric("🎓 Formations", "3")

# ===== SIDEBAR ETUDIANT =====
st.sidebar.header("🔑 Accès Étudiant - ID Unique")
if st.session_state.connecte:
    st.sidebar.success("✅ Tu es connecté en Admin")
    if st.sidebar.button("🚪 Déconnexion Admin", key="deco_admin_sidebar"):
        st.session_state.connecte = False
        st.rerun()
elif not st.session_state.etudiant_verifie:
    st.sidebar.info("🔒 Pour voir la Bibliothèque, il faut ton ID Unique.\nSans ID, tu peux voir Formations, Événements et Test, mais pas la Bibliothèque.")
    id_tape = st.sidebar.text_input("Ton ID Unique (ex: MIT-001)", key="id_unique_input")
    if st.sidebar.button("🔓 Débloquer la Bibliothèque", key="btn_debloquer_biblio"):
        ok, nom_trouve = verifier_id_unique(id_tape)
        if ok:
            st.session_state.etudiant_verifie = True
            st.session_state.etudiant_id = id_tape.strip().upper()
            st.session_state.etudiant_nom = nom_trouve
            st.sidebar.success(f"✅ Bienvenue {nom_trouve} ! Bibliothèque débloquée.")
            st.rerun()
        else:
            st.sidebar.error("❌ ID Unique incorrect. Demande ton ID à l'Admin.")
else:
    st.sidebar.success(f"✅ Connecté : {st.session_state.etudiant_nom}\nID : {st.session_state.etudiant_id}")
    if st.sidebar.button("🚪 Déconnexion Étudiant", key="deco_etudiant_sidebar"):
        st.session_state.etudiant_verifie = False
        st.session_state.etudiant_nom = ""
        st.session_state.etudiant_id = ""
        st.rerun()

a_droit_biblio = st.session_state.connecte or st.session_state.etudiant_verifie

menu = st.tabs([t["formations"], t["biblio"], t["etudiants"], t["events"], t["test"], t["admin"]])

with menu[0]:
    col1, col2, col3 = st.columns(3)
    col1.info("**💻 Génie Logiciel**\n\nPython, C, Web, Mobile, IA")
    col2.info("**📊 Systèmes d'Information**\n\nBases de données, Réseaux, Cloud")
    col3.info("**💼 Management**\n\nBusiness, Marketing, Finance")

with menu[1]:
    st.header(t["biblio"])
    if not a_droit_biblio:
        st.warning("🔒 Bibliothèque réservée aux étudiants inscrits.")
        st.info("👉 Va à gauche dans **Accès Étudiant - ID Unique**, tape ton ID Unique, puis reviens ici.")
        st.info("Tu n'as pas d'ID ? Demande à l'Admin. Sans ID, tu peux quand même voir les Formations, Événements et Test.")
    else:
        if st.session_state.etudiant_verifie:
            st.success(f"✅ Bienvenue {st.session_state.etudiant_nom} - Bibliothèque débloquée")
        if st.session_state.connecte:
            st.success("✅ Vue Admin : tu vois toute la Bibliothèque")
        st.write(f"**{len(st.session_state.livres)} livres disponibles**")
        col_f1, col_f2 = st.columns(2)
        recherche = col_f1.text_input(t["recherche"], key="recherche_biblio")
        filiere_choisie = col_f2.selectbox("Filtrer par filière", ["Toutes", "Génie Logiciel", "Systèmes d'Information", "Management"], key="filtre_biblio")
        for livre in st.session_state.livres:
            if filiere_choisie != "Toutes" and livre["filiere"] != filiere_choisie: continue
            if recherche.lower() not in livre["titre"].lower() and recherche.lower() not in livre["auteur"].lower() and recherche != "": continue
            statut = "Disponible ✅" if livre["dispo"] else "Emprunté ❌"
            if livre["dispo"]: st.success(f"**{livre['titre']}** | {livre['auteur']} | {livre['filiere']} | {livre['annee']} | {statut}")
            else: st.error(f"**{livre['titre']}** | {livre['auteur']} | {livre['filiere']} | {livre['annee']} | {statut}")
            if "lire" in livre:
                with st.expander(f"📖 Lire chez soi - {livre['titre']}"):
                    st.write(livre["lire"])
                    st.info("💡 Astuce : Tu peux lire ça chez toi, sur ton téléphone, sans venir à la bibliothèque.")

with menu[2]:
    st.header(t["etudiants"])
    if not st.session_state.connecte:
        st.warning("🔒 Cette partie est réservée à l'Admin.")
        st.info("Les étudiants ne voient pas combien d'étudiants sont inscrits, ni la liste.")
        st.info("Si tu es étudiant, va dans Bibliothèque avec ton ID Unique.")
    else:
        if st.session_state.etudiants_df is not None:
            df = st.session_state.etudiants_df
            st.success(f"✅ {len(df)} étudiants chargés depuis Excel")
            search = st.text_input("🔍 Rechercher un étudiant par nom...", key="search_etudiant")
            if search: df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False, na=False)).any(axis=1)]
            st.dataframe(df, use_container_width=True)
            if "Note" in df.columns: st.bar_chart(df["Note"])
        else:
            st.warning("Aucun fichier Excel importé. Va dans Admin pour importer.")

with menu[3]:
    st.header(t["events"])
    st.warning("🎉 Soirée d'intégration - Vendredi 18h - Monplaisir")
    st.warning("⚽ Tournoi de foot MIT - Samedi 10h")
    st.warning("📝 Examens Blancs - Lundi prochain")

with menu[4]:
    st.header(t["test_titre"])
    st.info("📋 5 questions - Chaque bonne réponse = 4 points - Total = 20/20 - Pour réussir il faut 10/20")
    nom_test = st.text_input(t["nom_label"], placeholder="Ex: Peniel Mwilambwe", key="nom_test_input")
    reponses = []
    for item in QUESTIONS:
        rep = st.radio(item["q"], item["options"], key="test_" + item["q"])
        reponses.append(rep)
    if st.button(t["valider"], key="btn_valider_test"):
        if not nom_test: st.error("❌ Écris d'abord ton nom !")
        else:
            score = 0
            for i, item in enumerate(QUESTIONS):
                if reponses[i] == item["bonne"]: score += 4
            st.session_state.resultats.append({"Nom": nom_test, "Note /20": score, "Réussi": "OUI ✅" if score >= 10 else "NON ❌"})
            st.divider()
            st.write(f"### 🎓 Résultat pour {nom_test} : **{score} / 20**")
            st.progress(score / 20)
            if score >= 16:
                st.balloons(); st.success("🎉 EXCELLENT ! Félicitations, tu es un champion MIT !")
            elif score >= 10: st.success("✅ RÉUSSI ! Bravo, tu as validé le test.")
            else: st.error("❌ ÉCHOUÉ. Ne lâche pas, relis les livres de la bibliothèque et recommence !")
            st.write("**Correction :**")
            for i, item in enumerate(QUESTIONS):
                if reponses[i] == item["bonne"]: st.write(f"{item['q']} -> ✅ {item['bonne']}")
                else: st.write(f"{item['q']} -> ❌ Tu as mis {reponses[i]} | Bonne réponse : {item['bonne']}")

with menu[5]:
    st.header(t["admin_titre"])
    if time.time() < st.session_state.bloque_jusqua:
        st.error("🔒 Bloqué 30 secondes")
    elif not st.session_state.connecte:
        mdp = st.text_input(t["mdp_label"], type="password", key="mdp_admin_input")
        if st.button("Connexion Admin", key="btn_connexion_admin"):
            if verifier_mdp(mdp):
                st.session_state.connecte = True
                st.session_state.tentatives = 0
                st.rerun()
            else:
                st.session_state.tentatives += 1
                restant = 3 - st.session_state.tentatives
                if restant <= 0:
                    st.session_state.bloque_jusqua = time.time() + 30
                    st.session_state.tentatives = 0
                else:
                    st.error(f"❌ Mauvais mot de passe. Il reste {restant}")
    else:
        st.success(t["bienvenue_admin"])
        st.subheader("📊 Résultats des Tests")
        if len(st.session_state.resultats) > 0:
            st.dataframe(pd.DataFrame(st.session_state.resultats), use_container_width=True)
        else:
            st.info("Aucun test passé pour le moment.")
        st.subheader(t["excel_titre"])
        st.info(t["excel_info"])
        fichier = st.file_uploader("📂 Choisis ton fichier Excel (.xlsx)", type=["xlsx", "xls", "csv"], key="upload_excel_admin")
        if fichier is not None:
            try:
                df = pd.read_csv(fichier) if fichier.name.endswith(".csv") else pd.read_excel(fichier)
                st.session_state.etudiants_df = df
                st.success(f"✅ {len(df)} étudiants chargés !")
                st.dataframe(df)
                st.download_button("⬇️ Télécharger cet Excel", df.to_csv(index=False).encode(), "etudiants.csv", key="dl_excel_admin")
            except Exception as e:
                st.error(f"Erreur: {e}")
        st.subheader("🔑 Créer un ID Unique pour un étudiant")
        st.info("L'étudiant utilisera cet ID pour débloquer la Bibliothèque. Ex: MIT-003")
        nouvel_id = st.text_input("Nouvel ID Unique (ex: MIT-003)", key="nouvel_id_input")
        if st.button("➕ Ajouter cet ID", key="btn_ajouter_id"):
            if nouvel_id and nouvel_id.strip().upper() not in [x.upper() for x in st.session_state.ids_autorises]:
                st.session_state.ids_autorises.append(nouvel_id.strip().upper())
                st.success(f"✅ ID {nouvel_id.strip().upper()} créé ! Donne-le à l'étudiant.")
            elif nouvel_id:
                st.warning("Cet ID existe déjà.")
        st.write("**IDs autorisés :**")
        st.write(", ".join(st.session_state.ids_autorises))
        id_a_supprimer = st.selectbox("Supprimer un ID ?", ["Aucun"] + st.session_state.ids_autorises, key="supprimer_id_select")
        if st.button("🗑️ Supprimer cet ID", key="btn_supprimer_id"):
            if id_a_supprimer != "Aucun":
                st.session_state.ids_autorises.remove(id_a_supprimer)
                st.success(f"ID {id_a_supprimer} supprimé")
                st.rerun()
        st.subheader(t["ajouter_livre"])
        nt = st.text_input("Titre du livre", key="nouveau_titre_livre")
        na = st.text_input("Auteur", key="nouvel_auteur_livre")
        if st.button("Ajouter le livre", key="btn_ajouter_livre"):
            if nt and na:
                st.session_state.livres.append({"titre": nt, "auteur": na, "filiere": "Génie Logiciel", "annee": 2026, "dispo": True})
                st.success("Livre ajouté !")
                st.rerun()
        if st.button(t["deconnexion"], key="btn_deconnexion_admin"):
            st.session_state.connecte = False
            st.rerun()

