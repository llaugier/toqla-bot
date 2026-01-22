import os
import requests
from playwright.sync_api import sync_playwright

def get_menu():
    with sync_playwright() as p:
        print("Lancement du navigateur...")
        browser = p.chromium.launch(headless=True)
        # On définit un user-agent réaliste pour éviter d'être bloqué
        context = browser.new_context(
            viewport={'width': 1280, 'height': 1000},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        shop_url = "https://app.toqla.fr/site/67/shop/585d9cc9-390b-431a-b90b-e15fa53c64c9"
        print(f"Connexion initiale à : {shop_url}")
        page.goto(shop_url)

        try:
            # 1. ÉTAPE EMAIL
            print("Vérification de l'étape Email...")
            page.wait_for_selector('input[name="username"]', timeout=15000)
            page.fill('input[name="username"]', os.environ['TOQLA_EMAIL'])
            page.keyboard.press("Enter")
            
            # 2. ÉTAPE MOT DE PASSE
            print("Attente du champ mot de passe...")
            # On utilise un sélecteur plus large pour éviter les erreurs
            page.wait_for_selector('input[name="password"], input[type="password"]', timeout=20000)
            page.fill('input[name="password"], input[type="password"]', os.environ['TOQLA_PASSWORD'])
            page.keyboard.press("Enter")

            # 3. GESTION DE LA REDIRECTION
            print("Attente de la connexion au domaine Toqla...")
            # On attend simplement d'arriver sur n'importe quelle page de Toqla
            page.wait_for_url("https://app.toqla.fr/**", timeout=30000)
            
            # Si on a atterri sur /home, on force le retour vers le shop
            if "/home" in page.url:
                print("Redirection vers /home détectée. Navigation forcée vers le shop...")
                page.goto(shop_url)
                page.wait_for_timeout(5000) # Attente du chargement
            
            # 4. EXTRACTION DU MENU
            print("Extraction des plats...")
            page.wait_for_selector("h3, .article-name", timeout=15000)
            
            found_items = []
            # On cherche les titres de plats
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
                return "⚠️ Connecté, mais aucun plat trouvé. Vérifiez si le service n'est pas terminé."
                
            return "🍴 *Menu du jour Toqla* 🍴\n\n" + "\n".join([f"- {item}" for item in unique_items])

        except Exception as e:
            # On prend une capture d'écran de l'erreur pour le debug
            page.screenshot(path="error_login.png")
            print(f"Erreur détectée sur l'URL : {page.url}")
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
        # On n'envoie pas l'erreur sur le chat à chaque fois pour éviter le spam si vous testez
        # send_to_google_chat(error_msg)
