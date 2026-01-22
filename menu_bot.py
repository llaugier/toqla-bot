import os
import requests
from playwright.sync_api import sync_playwright

def get_menu():
    with sync_playwright() as p:
        print("Lancement du navigateur...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        
        url = "https://app.toqla.fr/site/67/shop/585d9cc9-390b-431a-b90b-e15fa53c64c9"
        
        print(f"Chargement de la page : {url}")
        page.goto(url, wait_until="networkidle")
        
        # On attend un peu que les éléments dynamiques (React/Vue) s'affichent
        print("Attente du chargement des plats...")
        page.wait_for_timeout(8000) 

        # Tentative d'extraction : on cherche les textes qui ressemblent à des plats
        # On cible les titres (h3, h4) et les classes souvent utilisées par Toqla
        menu_items = []
        
        # On cherche tous les éléments qui pourraient contenir un nom de produit
        selectors = ["h3", "h4", ".article-name", ".product-name", "span.name"]
        
        for selector in selectors:
            elements = page.query_selector_all(selector)
            for el in elements:
                text = el.inner_text().strip()
                if text and len(text) > 3: # On évite les textes trop courts
                    menu_items.append(text)
        
        browser.close()
        
        # Nettoyage des doublons et formatage
        unique_items = list(dict.fromkeys(menu_items))
        
        if not unique_items:
            return "⚠️ Aucun plat n'a pu être détecté automatiquement sur la page."
            
        return "🍴 *Menu du jour Toqla* 🍴\n\n" + "\n".join([f"- {item}" for item in unique_items])

def send_to_google_chat(text):
    webhook_url = os.environ.get('https://chat.googleapis.com/v1/spaces/AAAAh2O9o4g/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=VN6fIX1Jq_3A3zuEIgu7Z4_2UX6MiodpX9-4oa3MdR4')
    if not webhook_url:
        print("Erreur : La variable GOOGLE_CHAT_WEBHOOK est vide.")
        return

    payload = {"text": text}
    response = requests.post(webhook_url, json=payload)
    print(f"Statut de l'envoi : {response.status_code}")

if __name__ == "__main__":
    try:
        content = get_menu()
        print("Menu récupéré, envoi en cours...")
        send_to_google_chat(content)
    except Exception as e:
        print(f"Une erreur est survenue : {e}")
