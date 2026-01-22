import os
import requests
from playwright.sync_api import sync_playwright

def get_menu():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # On définit une langue française pour éviter les bugs de détection
        context = browser.new_context(locale="fr-FR")
        page = context.new_page()
        
        url = "https://app.toqla.fr/site/67/shop/585d9cc9-390b-431a-b90b-e15fa53c64c9"
        
        print("Navigation vers la page de connexion...")
        page.goto(url)
        
        # 1. REMPLIR L'EMAIL
        # On attend que le champ email apparaisse (vu sur votre capture)
        page.wait_for_selector('input[type="email"], input[name="username"]')
        page.fill('input[type="email"], input[name="username"]', os.environ['TOQLA_EMAIL'])
        
        # 2. CLIQUER SUR CONTINUER
        page.click('button:has-text("Continue"), button:has-text("Continuer")')
        print("Email validé, attente du champ mot de passe...")

        # 3. REMPLIR LE MOT DE PASSE
        # On attend que le champ password apparaisse
        page.wait_for_selector('input[type="password"]')
        page.fill('input[type="password"]', os.environ['TOQLA_PASSWORD'])
        
        # 4. CLIQUER SUR CONNEXION
        # Le bouton peut s'appeler "Log In", "Connexion" ou avoir une icône
        page.keyboard.press("Enter") 
        print("Tentative de connexion en cours...")

        # 5. ACCÉDER AU SHOP
        # On attend d'être redirigé vers la boutique
        page.wait_for_url("**/shop/**", timeout=30000)
        print("Connexion réussie ! Récupération du menu...")
        
        # Petite attente pour le chargement des plats
        page.wait_for_timeout(5000)
        
        # 6. EXTRACTION DU MENU
        found_items = []
        # On cible les titres de produits (souvent h3 ou classes avec "name")
        selectors = ["h3", "h4", ".article-name", ".product-name"]
        
        for sel in selectors:
            elements = page.query_selector_all(sel)
            for el in elements:
                t = el.inner_text().strip()
                if len(t) > 3:
                    found_items.append(t)

        browser.close()
        unique_items = list(dict.fromkeys(found_items))
        
        if not unique_items:
            return "⚠️ Connecté, mais aucun plat trouvé sur la page boutique."
            
        return "🍴 *Menu du jour* 🍴\n\n" + "\n".join([f"- {item}" for item in unique_items])

def send_to_google_chat(text):
    webhook_url = 'https://chat.googleapis.com/v1/spaces/AAAAh2O9o4g/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=VN6fIX1Jq_3A3zuEIgu7Z4_2UX6MiodpX9-4oa3MdR4'
    if webhook_url:
        requests.post(webhook_url, json={"text": text})

if __name__ == "__main__":
    try:
        menu = get_menu()
        send_to_google_chat(menu)
    except Exception as e:
        error_msg = f"❌ Erreur lors de la connexion : {str(e)}"
        print(error_msg)
        send_to_google_chat(error_msg)
