import os
import requests
from playwright.sync_api import sync_playwright

def get_menu():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # On simule un grand écran pour tout voir
        page = browser.new_page(viewport={'width': 1280, 'height': 1600})
        
        url = "https://app.toqla.fr/site/67/shop/585d9cc9-390b-431a-b90b-e15fa53c64c9"
        print(f"Navigation vers {url}...")
        page.goto(url, wait_until="networkidle")
        
        # On attend que le contenu dynamique apparaisse
        page.wait_for_timeout(10000) 
        
        # --- DEBUG : Capture d'écran ---
        page.screenshot(path="debug_screen.png")
        print("Capture d'écran effectuée.")

        # --- RECHERCHE LARGE ---
        # On cherche tout ce qui ressemble à un titre ou un nom de produit
        # Toqla utilise souvent des classes comme 'article-title' ou des div spécifiques
        found_items = []
        
        # On essaie de trouver les éléments qui ont une structure de prix à côté
        # ou qui sont dans les listes de produits
        selectors = [
            ".article-name", ".product-name", "h3", "h4", 
            "div[class*='name']", "span[class*='title']"
        ]
        
        for sel in selectors:
            elements = page.query_selector_all(sel)
            for el in elements:
                t = el.inner_text().strip()
                if len(t) > 5 and "\n" not in t: # Filtre pour éviter les blocs de texte inutiles
                    found_items.append(t)

        browser.close()
        
        # Nettoyage
        unique_items = list(dict.fromkeys(found_items))
        
        if not unique_items:
            return "⚠️ Robot connecté, mais aucun texte de plat trouvé. Vérifiez la capture d'écran dans GitHub."
            
        return "🍴 *Menu du jour* 🍴\n\n" + "\n".join([f"- {item}" for item in unique_items[:20]])

def send_to_google_chat(text):
    webhook_url = 'https://chat.googleapis.com/v1/spaces/AAAAh2O9o4g/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=VN6fIX1Jq_3A3zuEIgu7Z4_2UX6MiodpX9-4oa3MdR4'
    if webhook_url:
        requests.post(webhook_url, json={"text": text})

if __name__ == "__main__":
    menu = get_menu()
    send_to_google_chat(menu)
