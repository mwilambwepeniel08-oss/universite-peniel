import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import hashlib
import hmac
import json
import os
import time
import uuid
import requests
from datetime import datetime

# ✅ CORRIGÉ : UN SEUL set_page_config, et c'est la 1ère commande Streamlit
st.set_page_config(
    page_title="MIT Tunis - Monplaisir",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- MODE iPHONE / APPLE ---
# ✅ CORRIGÉ : on ne cache plus le "header", sinon la flèche qui ouvre la barre
#    latérale disparaît sur téléphone et les étudiants ne peuvent plus entrer leur ID.
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="MIT Tunis">

<style>
    .stButton > button {
        width: 100%;
        height: 50px;
        border-radius: 15px;
        font-size: 17px;
        font-weight: bold;
    }
    .stTextInput > div > div > input {
        font-size: 16px !important;
        border-radius: 12px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ======================================================
# CONFIGURATION
# ======================================================
SHEET_ID = "1jUbSyUFGGX4WeCw5Pwj8hDHkmCmkuy9H-PL22gTJhxY"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycby0xCfO-0ozSBNqLs0qkLk9sIrqBwujteOmOUHd6pgxn4RdUq3TYWj7IRBgQhYGuDDlZw/exec"

# Fichiers PARTAGÉS entre tous les visiteurs
FICHIER_EN_LIGNE = "en_ligne.json"
FICHIER_IDS = "ids_autorises.json"
FICHIER_LIVRES = "livres_ajoutes.json"
FICHIER_RESULTATS = "resultats.json"
FICHIER_ETUDIANTS = "etudiants_importes.csv"

DELAI_EN_LIGNE = 300  # secondes d'inactivité avant de disparaître de "en ligne"
IDS_PAR_DEFAUT = ["MIT-2026-PENIEL", "MIT-001", "MIT-002"]
COLONNES_ID = ["id", "id unique", "code", "email", "matricule"]

# ======================================================
# 🔐 MOT DE PASSE ADMIN  →  À REMPLIR PAR TOI, À LA MAIN
# ======================================================
# Option A (recommandée) : dans les "Secrets" de Streamlit, ajoute la ligne
#     ADMIN_HASH = "le_hash_sha256_de_ton_mot_de_passe"
# Option B (plus simple) : écris ton mot de passe entre les guillemets ci-dessous.
#     (Attention : si tu publies ce fichier sur GitHub public, tout le monde le verra.)
MOT_DE_PASSE_ADMIN = ""  # <-- METS TON MOT DE PASSE ICI (ou laisse vide si tu utilises les Secrets)

ADMIN_HASH = ""
try:
    ADMIN_HASH = st.secrets["ADMIN_HASH"]
except Exception:
    if MOT_DE_PASSE_ADMIN:
        ADMIN_HASH = hashlib.sha256(MOT_DE_PASSE_ADMIN.encode()).hexdigest()


def verifier_mdp(mdp):
    # ✅ CORRIGÉ : si aucun mot de passe n'est configuré, personne ne peut entrer
    if not ADMIN_HASH:
        return False
    h = hashlib.sha256(mdp.encode()).hexdigest()
    return hmac.compare_digest(h, str(ADMIN_HASH))


# ======================================================
# OUTILS : fichiers partagés
# ======================================================
@st.cache_resource
def get_verrou():
    # ✅ CORRIGÉ : un seul verrou partagé (un verrou créé dans le script serait recréé à chaque rechargement)
    import threading
    return threading.Lock()


def lire_json(chemin, defaut):
    if os.path.exists(chemin):
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return defaut
    return defaut


def ecrire_json(chemin, data):
    # ✅ CORRIGÉ : écriture "atomique" : on écrit dans un fichier temporaire puis on remplace,
    #    pour qu'un autre visiteur ne lise jamais un fichier à moitié écrit (JSON cassé).
    tmp = f"{chemin}.{uuid.uuid4().hex}.tmp"
    with get_verrou():
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, chemin)


# ======================================================
# GOOGLE SHEETS (lecture, mise en cache 60 secondes)
# ======================================================
@st.cache_data(ttl=60)
def lire_sheet(nom_feuille):
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={nom_feuille}"
    try:
        return pd.read_csv(url)
    except Exception:
        return pd.DataFrame()


# ======================================================
# DONNÉES DE BASE
# ======================================================
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


# ======================================================
# DONNÉES PARTAGÉES (étudiants, IDs, livres, résultats)
# ======================================================
def charger_etudiants():
    """Excel importé par l'admin, sinon la feuille Google 'Etudiants', sinon None."""
    if os.path.exists(FICHIER_ETUDIANTS):
        try:
            return pd.read_csv(FICHIER_ETUDIANTS)
        except Exception:
            pass
    df = lire_sheet("Etudiants")
    if not df.empty:
        return df
    return None


def charger_ids():
    return lire_json(FICHIER_IDS, list(IDS_PAR_DEFAUT))


def sauver_ids(ids):
    ecrire_json(FICHIER_IDS, ids)


def charger_livres():
    return LIVRES_DE_BASE + lire_json(FICHIER_LIVRES, [])


def charger_resultats():
    return lire_json(FICHIER_RESULTATS, [])


def enregistrer_resultat(nom, score):
    reussi = score >= 10
    resultats = charger_resultats()
    resultats.append({
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Nom": nom,
        "Note /20": score,
        "Réussi": "OUI ✅" if reussi else "NON ❌",
    })
    ecrire_json(FICHIER_RESULTATS, resultats)
    # Copie vers Google Sheets (si ça échoue, ce n'est pas grave)
    try:
        requests.post(WEB_APP_URL, json={
            "feuille": "Resultats",
            "nom": nom,
            "note": score,
            "reussi": "OUI" if reussi else "NON",
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }, timeout=5)
    except Exception:
        pass


# ======================================================
# ÉTUDIANTS EN LIGNE
# ======================================================
def liste_en_ligne():
    data = lire_json(FICHIER_EN_LIGNE, {})
    maintenant = time.time()
    return {k: v for k, v in data.items() if maintenant - v.get("ts", 0) < DELAI_EN_LIGNE}


def marquer_en_ligne(id_e, nom):
    if "mon_token" not in st.session_state:
        st.session_state.mon_token = str(uuid.uuid4())
    en_ligne = liste_en_ligne()
    en_ligne[id_e] = {
        "nom": nom,
        "heure": datetime.now().strftime("%H:%M:%S"),
        "ts": time.time(),
        "token": st.session_state.mon_token,
    }
    ecrire_json(FICHIER_EN_LIGNE, en_ligne)


def retirer_en_ligne(id_e):
    en_ligne = lire_json(FICHIER_EN_LIGNE, {})
    if id_e in en_ligne:
        del en_ligne[id_e]
        ecrire_json(FICHIER_EN_LIGNE, en_ligne)


# ======================================================
# ✅ CORRIGÉ : blocage anti-devinette PARTAGÉ (avant, il était dans session_state,
#    donc un simple rechargement de la page remettait le compteur à zéro)
# ======================================================
@st.cache_resource
def etat_blocage():
    return {"essais": 0, "jusqua": 0.0}


# ======================================================
# VIBRATIONS
# ======================================================
def son_erreur():
    components.html("""
        <script>
        try {
            if (window.parent.navigator.vibrate) {
                window.parent.navigator.vibrate([500, 200, 500, 200, 500]);
            } else if (navigator.vibrate) {
                navigator.vibrate([500, 200, 500, 200, 500]);
            }
        } catch(e) {}
        </script>
    """, height=0)


def son_succes():
    components.html("""
        <script>
        try {
            if (window.parent.navigator.vibrate) {
                window.parent.navigator.vibrate([100]);
            } else if (navigator.vibrate) {
                navigator.vibrate([100]);
            }
        } catch(e) {}
        </script>
    """, height=0)


# Le son demandé avant un st.rerun() est joué ici, après le rechargement
son_demande = st.session_state.pop("son_a_jouer", None)
if son_demande == "succes":
    son_succes()
elif son_demande == "erreur":
    son_erreur()

# ======================================================
# STYLE + LANGUES
# ======================================================
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

# ======================================================
# ÉTAT DE LA SESSION (seulement ce qui est PERSONNEL au visiteur)
# ======================================================
if "connecte" not in st.session_state: st.session_state.connecte = False
if "etudiant_verifie" not in st.session_state: st.session_state.etudiant_verifie = False
if "etudiant_nom" not in st.session_state: st.session_state.etudiant_nom = ""
if "etudiant_id" not in st.session_state: st.session_state.etudiant_id = ""


def verifier_id_unique(id_tape):
    id_tape = str(id_tape).strip().upper()
    if not id_tape:
        return False, ""

    # 1) On cherche dans l'Excel / la feuille Google
    df = charger_etudiants()
    if df is not None:
        for col in df.columns:
            if str(col).strip().lower() in COLONNES_ID:
                masque = df[col].astype(str).str.strip().str.upper() == id_tape
                if masque.any():
                    ligne = df[masque].iloc[0]
                    morceaux = []
                    for c in ["Nom", "Prénom", "Prenom", "Name"]:
                        if c in df.columns and pd.notna(ligne[c]):
                            morceaux.append(str(ligne[c]))
                    return True, " ".join(morceaux).strip() or "Étudiant MIT"

    # 2) On cherche AUSSI dans les IDs créés par l'admin
    if id_tape in [str(x).upper() for x in charger_ids()]:
        return True, "Étudiant MIT"

    return False, ""


# Données partagées chargées une fois par affichage
livres = charger_livres()
resultats = charger_resultats()

# ===== HEADER =====
st.markdown("<div style='text-align: center; font-size: 90px; margin-bottom: -20px;'>🎓</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; color: #0B3D91; font-weight: bold; font-size: 18px;'>MIT TUNIS - MONPLAISIR</div>", unsafe_allow_html=True)
st.title(t["titre"])
st.subheader(t["sous"])
st.write(f"### {t['bienvenue']}")

# ===== VUE ADMIN EN HAUT - SEUL ADMIN VOIT ÇA =====
if st.session_state.connecte:
    st.markdown("<div class='admin-box'><h3>👑 MODE ADMIN - Vue Administrateur</h3><p>Tu vois tout. Les étudiants ne voient pas cette partie.</p></div>", unsafe_allow_html=True)
    st.subheader("🟢 Étudiants en ligne")
    en_ligne = liste_en_ligne()
    if en_ligne:
        st.write(f"**{len(en_ligne)} étudiant(s) en ligne**")
        for id_e, infos in en_ligne.items():
            st.write(f"🟢 {infos['nom']} - ID: {id_e} - Dernière activité à {infos['heure']}")
    else:
        st.info("Aucun étudiant en ligne pour le moment.")

    df_admin = charger_etudiants()
    nb_etudiants = len(df_admin) if df_admin is not None else 0
    ids_actuels = charger_ids()
    a1, a2, a3, a4 = st.columns(4)
    a1.metric("👨‍🎓 Étudiants inscrits", nb_etudiants)
    a2.metric("📚 Livres", len(livres))
    a3.metric("🔑 IDs créés", len(ids_actuels))
    a4.metric("📝 Tests passés", len(resultats))
    with st.expander("👁️ Voir le tableau Admin complet", expanded=False):
        st.write("**📋 Étudiants Excel :**")
        if df_admin is not None:
            st.dataframe(df_admin)
        else:
            st.info("Aucun Excel importé. Va dans l'onglet Admin pour importer.")
        st.write("**🔑 IDs autorisés :**")
        st.write(", ".join(str(x) for x in ids_actuels))
        st.write("**📝 Résultats Tests :**")
        if len(resultats) > 0:
            st.dataframe(pd.DataFrame(resultats))
        else:
            st.info("Aucun test passé.")
    st.divider()
else:
    # Vue publique : on cache le nombre d'étudiants
    c1, c2, c3 = st.columns(3)
    c1.metric("📚 Livres", len(livres))
    c2.metric("📝 Tests passés", len(resultats))
    c3.metric("🎓 Formations", "3")

# ===== SIDEBAR ÉTUDIANT =====
st.sidebar.header("🔑 Accès Étudiant - ID Unique")
if st.session_state.connecte:
    st.sidebar.success("✅ Tu es connecté en Admin")
    if st.sidebar.button("🚪 Déconnexion Admin", key="deco_admin_sidebar"):
        st.session_state.connecte = False
        st.rerun()
elif not st.session_state.etudiant_verifie:
    st.sidebar.info("🔒 Pour voir la Bibliothèque, il faut ton ID Unique.\nSans ID, tu peux voir Formations, Événements et Test, mais pas la Bibliothèque.")
    id_tape = st.sidebar.text_input("Ton ID Unique", key="id_unique_input")
    if st.sidebar.button("🔓 Débloquer la Bibliothèque", key="btn_debloquer_biblio"):
        ok, nom_trouve = verifier_id_unique(id_tape)
        if ok:
            st.session_state.etudiant_verifie = True
            st.session_state.etudiant_id = id_tape.strip().upper()
            st.session_state.etudiant_nom = nom_trouve
            st.session_state.son_a_jouer = "succes"
            st.rerun()
        else:
            son_erreur()
            st.sidebar.error("❌ ID Unique incorrect. Demande ton ID à l'Admin.")
else:
    st.sidebar.success(f"✅ Connecté : {st.session_state.etudiant_nom}\nID : {st.session_state.etudiant_id}")
    if st.sidebar.button("🚪 Déconnexion Étudiant", key="deco_etudiant_sidebar"):
        retirer_en_ligne(st.session_state.etudiant_id)
        st.session_state.etudiant_verifie = False
        st.session_state.etudiant_nom = ""
        st.session_state.etudiant_id = ""
        st.rerun()

# On signale que l'étudiant est en ligne
if st.session_state.etudiant_verifie:
    marquer_en_ligne(st.session_state.etudiant_id, st.session_state.etudiant_nom)

a_droit_biblio = st.session_state.connecte or st.session_state.etudiant_verifie

menu = st.tabs([t["formations"], t["biblio"], t["etudiants"], t["events"], t["test"], t["admin"]])

# ===== ONGLET 0 : FORMATIONS =====
with menu[0]:
    col1, col2, col3 = st.columns(3)
    col1.info("**💻 Génie Logiciel**\n\nPython, C, Web, Mobile, IA")
    col2.info("**📊 Systèmes d'Information**\n\nBases de données, Réseaux, Cloud")
    col3.info("**💼 Management**\n\nBusiness, Marketing, Finance")

# ===== ONGLET 1 : BIBLIOTHÈQUE =====
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
        st.write(f"**{len(livres)} livres disponibles**")
        col_f1, col_f2 = st.columns(2)
        recherche = col_f1.text_input(t["recherche"], key="recherche_biblio")
        filiere_choisie = col_f2.selectbox("Filtrer par filière", ["Toutes", "Génie Logiciel", "Systèmes d'Information", "Management"], key="filtre_biblio")
        for livre in livres:
            if filiere_choisie != "Toutes" and livre["filiere"] != filiere_choisie:
                continue
            mot = recherche.lower()
            if mot and mot not in livre["titre"].lower() and mot not in livre["auteur"].lower():
                continue
            statut = "Disponible ✅" if livre["dispo"] else "Emprunté ❌"
            texte = f"**{livre['titre']}** | {livre['auteur']} | {livre['filiere']} | {livre['annee']} | {statut}"
            if livre["dispo"]:
                st.success(texte)
            else:
                st.error(texte)
            if "lire" in livre:
                with st.expander(f"📖 Lire chez soi - {livre['titre']}"):
                    st.text(livre["lire"])  # ✅ st.text : le code HTML/Python s'affiche tel quel
                    st.info("💡 Astuce : Tu peux lire ça chez toi, sur ton téléphone, sans venir à la bibliothèque.")

# ===== ONGLET 2 : ÉTUDIANTS (ADMIN SEULEMENT) =====
with menu[2]:
    st.header(t["etudiants"])
    if not st.session_state.connecte:
        st.warning("🔒 Cette partie est réservée à l'Admin.")
        st.info("Les étudiants ne voient pas combien d'étudiants sont inscrits, ni la liste.")
        st.info("Si tu es étudiant, va dans Bibliothèque avec ton ID Unique.")
    else:
        df = charger_etudiants()
        if df is not None:
            st.success(f"✅ {len(df)} étudiants chargés")
            search = st.text_input("🔍 Rechercher un étudiant par nom...", key="search_etudiant")
            if search:
                masque = df.astype(str).apply(
                    lambda col: col.str.contains(search, case=False, na=False, regex=False)
                ).any(axis=1)
                df = df[masque]
            st.dataframe(df)
            if "Note" in df.columns:
                notes = pd.to_numeric(df["Note"], errors="coerce").dropna()
                if len(notes) > 0:
                    st.bar_chart(notes)
        else:
            st.warning("Aucun fichier Excel importé. Va dans Admin pour importer.")

# ===== ONGLET 3 : ÉVÉNEMENTS =====
with menu[3]:
    st.header(t["events"])
    st.warning("🎉 Soirée d'intégration - Vendredi 18h - Monplaisir")
    st.warning("⚽ Tournoi de foot MIT - Samedi 10h")
    st.warning("📝 Examens Blancs - Lundi prochain")

# ===== ONGLET 4 : TEST =====
with menu[4]:
    st.header(t["test_titre"])
    st.info("📋 5 questions - Chaque bonne réponse = 4 points - Total = 20/20 - Pour réussir il faut 10/20")
    nom_test = st.text_input(t["nom_label"], placeholder="Ex: Peniel Mwilambwe", key="nom_test_input")
    reponses = []
    for item in QUESTIONS:
        rep = st.radio(item["q"], item["options"], index=None, key="test_" + item["q"])
        reponses.append(rep)
    if st.button(t["valider"], key="btn_valider_test"):
        if not nom_test.strip():
            st.error("❌ Écris d'abord ton nom !")
        elif None in reponses:
            st.error("❌ Réponds à toutes les questions avant de valider !")
        else:
            score = 0
            for i, item in enumerate(QUESTIONS):
                if reponses[i] == item["bonne"]:
                    score += 4
            enregistrer_resultat(nom_test.strip(), score)
            st.divider()
            st.write(f"### 🎓 Résultat pour {nom_test} : **{score} / 20**")
            st.progress(score / 20)
            if score >= 16:
                st.balloons()
                st.success("🎉 EXCELLENT ! Félicitations, tu es un champion MIT !")
            elif score >= 10:
                st.success("✅ RÉUSSI ! Bravo, tu as validé le test.")
            else:
                st.error("❌ ÉCHOUÉ. Ne lâche pas, relis les livres de la bibliothèque et recommence !")
            st.write("**Correction :**")
            for i, item in enumerate(QUESTIONS):
                if reponses[i] == item["bonne"]:
                    st.write(f"{item['q']} -> ✅ {item['bonne']}")
                else:
                    st.write(f"{item['q']} -> ❌ Tu as mis {reponses[i]} | Bonne réponse : {item['bonne']}")

# ===== ONGLET 5 : ADMIN =====
with menu[5]:
    st.header(t["admin_titre"])
    blocage = etat_blocage()
    if time.time() < blocage["jusqua"]:
        reste = int(blocage["jusqua"] - time.time()) + 1
        st.error(f"🔒 Connexion Admin bloquée encore {reste} secondes. Recharge la page après ce délai.")
    elif not st.session_state.connecte:
        if not ADMIN_HASH:
            st.warning("⚠️ Aucun mot de passe Admin configuré. Remplis MOT_DE_PASSE_ADMIN dans le code (ou ADMIN_HASH dans les Secrets).")
        mdp = st.text_input(t["mdp_label"], type="password", key="mdp_admin_input")
        if st.button("Connexion Admin", key="btn_connexion_admin"):
            if verifier_mdp(mdp):
                blocage["essais"] = 0
                st.session_state.connecte = True
                st.session_state.son_a_jouer = "succes"
                st.rerun()
            else:
                blocage["essais"] += 1
                restant = 3 - blocage["essais"]
                son_erreur()
                if restant <= 0:
                    blocage["jusqua"] = time.time() + 30
                    blocage["essais"] = 0
                    st.error("🔒 Trop d'essais. Bloqué 30 secondes.")
                else:
                    st.error(f"❌ Mauvais mot de passe. Il reste {restant}")
    else:
        st.success(t["bienvenue_admin"])

        # --- Résultats des tests ---
        st.subheader("📊 Résultats des Tests")
        if len(resultats) > 0:
            st.dataframe(pd.DataFrame(resultats))
        else:
            st.info("Aucun test passé pour le moment.")

        # --- Import Excel ---
        st.subheader(t["excel_titre"])
        st.info(t["excel_info"])
        fichier = st.file_uploader("📂 Choisis ton fichier Excel (.xlsx) ou CSV", type=["xlsx", "xls", "csv"], key="upload_excel_admin")
        if fichier is not None:
            try:
                df_import = pd.read_csv(fichier) if fichier.name.endswith(".csv") else pd.read_excel(fichier)
                st.write(f"Aperçu : {len(df_import)} lignes")
                st.dataframe(df_import)
                # ✅ CORRIGÉ : on enregistre seulement quand l'admin clique (avant : réécrit à chaque rechargement)
                if st.button("💾 Enregistrer cette liste pour tout le monde", key="btn_enregistrer_import"):
                    df_import.to_csv(FICHIER_ETUDIANTS, index=False)
                    st.success(f"✅ {len(df_import)} étudiants enregistrés !")
                st.download_button("⬇️ Télécharger la liste (CSV)", df_import.to_csv(index=False).encode("utf-8"),
                                   "etudiants.csv", mime="text/csv", key="dl_excel_admin")
            except Exception as e:
                st.error(f"Erreur: {e}")
        if os.path.exists(FICHIER_ETUDIANTS):
            if st.button("🗑️ Supprimer l'import (revenir à Google Sheets)", key="btn_suppr_import"):
                os.remove(FICHIER_ETUDIANTS)
                st.rerun()

        # --- IDs uniques ---
        st.subheader("🔑 Créer un ID Unique pour un étudiant")
        st.info("L'étudiant utilisera cet ID pour débloquer la Bibliothèque. Ex: MIT-003")
        ids = charger_ids()
        nouvel_id = st.text_input("Nouvel ID Unique (ex: MIT-003)", key="nouvel_id_input")
        if st.button("➕ Ajouter cet ID", key="btn_ajouter_id"):
            if nouvel_id and nouvel_id.strip().upper() not in [str(x).upper() for x in ids]:
                ids.append(nouvel_id.strip().upper())
                sauver_ids(ids)
                st.success(f"✅ ID {nouvel_id.strip().upper()} créé ! Donne-le à l'étudiant.")
            elif nouvel_id:
                st.warning("Cet ID existe déjà.")
        st.write("**IDs autorisés :**")
        st.write(", ".join(str(x) for x in ids))
        id_a_supprimer = st.selectbox("Supprimer un ID ?", ["Aucun"] + ids, key="supprimer_id_select")
        if st.button("🗑️ Supprimer cet ID", key="btn_supprimer_id"):
            if id_a_supprimer != "Aucun":
                ids.remove(id_a_supprimer)
                sauver_ids(ids)
                st.rerun()

        # --- Ajouter un livre ---
        st.subheader(t["ajouter_livre"])
        nt = st.text_input("Titre du livre", key="nouveau_titre_livre")
        na = st.text_input("Auteur", key="nouvel_auteur_livre")
        nf = st.selectbox("Filière", ["Génie Logiciel", "Systèmes d'Information", "Management"], key="nouvelle_filiere_livre")
        if st.button("Ajouter le livre", key="btn_ajouter_livre"):
            if nt and na:
                ajoutes = lire_json(FICHIER_LIVRES, [])
                ajoutes.append({"titre": nt, "auteur": na, "filiere": nf, "annee": 2026, "dispo": True})
                ecrire_json(FICHIER_LIVRES, ajoutes)
                st.rerun()
            else:
                st.warning("Remplis le titre et l'auteur.")

        if st.button(t["deconnexion"], key="btn_deconnexion_admin"):
            st.session_state.connecte = False
            st.rerun()
