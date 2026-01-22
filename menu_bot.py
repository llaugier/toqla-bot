import os
import requests
from playwright.sync_api import sync_playwright

def get_menu():
    with sync_playwright() as p:
        print("Lancement du navigateur...")
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1280, 'height': 1000}, locale="fr-FR")
        page = context.new_page()
        
        url = "https://app.toqla.fr/site/67/shop/585d9cc9-390b-431a-b90b-e15fa53c64c9"
        print(f"Connexion à {url}...")
        page.goto(url)

        try:
            # 1. SAISIE DE L'EMAIL
            print("Saisie de l'email...")
            page.wait_for_selector('input[name="username"]', timeout=15000)
            page.fill('input[name="username"]', os.environ['TOQLA_EMAIL'])
            
            # 2. VALIDATION (On utilise Enter au lieu de cliquer sur le bouton problématique)
            print("Validation de l'email avec la touche Entrée...")
            page.keyboard.press("Enter")
            
            # 3. SAISIE DU MOT DE PASSE
            print("Attente du champ mot de passe...")
            # On attend spécifiquement que le champ password apparaisse
            page.wait_for_selector('input[type="password"]', timeout=15000)
            page.fill('input[type="password"]', os.environ['TOQLA_PASSWORD'])
            
            # 4. VALIDATION FINALE
            print("Validation finale...")
            page.keyboard.press("Enter")

            # 5. ATTENTE DE LA REDIRECTION VERS LA BOUTIQUE
            print("Attente de la redirection vers la boutique...")
            # On attend que l'URL change pour confirmer la connexion
            page.wait_for_url("**/shop/**", timeout=30000)
            
            # Attente de sécurité pour le chargement des menus
            page.wait_for_timeout(7000)
            
            # 6. EXTRACTION DES PLATS
            print("Extraction des plats...")
            found_items = []
            # Sélecteurs plus larges pour capturer le texte des plats
            selectors = ["h3", "h4", ".article-name", ".product-name", "div.name"]
            
            for sel in selectors:
                elements = page.query_selector_all(sel)
                for el in elements:
                    t = el.inner_text().strip()
                    if len(t) > 3 and "\n" not in t:
                        found_items.append(t)

            browser.close()
            
            unique_items = list(dict.fromkeys(found_items))
            
            if not unique_items:
                return "⚠️ Connexion réussie, mais aucun plat n'a été trouvé. Le service est peut-être terminé."
                
            return "🍴 *Menu du jour Toqla* 🍴\n\n" + "\n".join([f"- {item}" for item in unique_items])

        except Exception as e:
            # En cas d'échec, on prend une photo pour voir où ça a bloqué
            page.screenshot(path="error_login.png")
            browser.close()
            raise e

def send_to_google_chat(text):
    webhook_url = 'https://chat.googleapis.com/v1/spaces/AAAAh2O9o4g/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=VN6fIX1Jq_3A3zuEIgu7Z4_2UX6MiodpX9-4oa3MdR4'
    if webhook_url:
        requests.post(webhook_url, json={"text": text})

if __name__ == "__main__":
    try:
        menu = get_menu()
        send_to_google_chat(menu)
    except Exception as e:
        error_msg = f"❌ Erreur lors de l'exécution : {str(e)}"
        print(error_msg)
        send_to_google_chat(error_msg)
