import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Configuration avec TES paramètres
VINTED_URL = "https://www.vinted.fr/catalog?search_text=ralph%20lauren&time=1746424860"
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")

def get_vinted_listings():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9"
    }
    
    try:
        response = requests.get(VINTED_URL, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        listings = []
        for item in soup.select('div.feed-grid__item'):
            try:
                title = item.select_one('h2.item-card__title').get_text(strip=True)
                price = item.select_one('div.item-card__price').get_text(strip=True)
                link = "https://www.vinted.fr" + item.select_one('a.item-card__link')['href']
                image = item.select_one('img.item-card__image')['src'] if item.select_one('img.item-card__image') else None
                
                listings.append({
                    'title': title,
                    'price': price,
                    'url': link,
                    'image': image,
                    'time': datetime.now().strftime("%H:%M %d/%m")
                })
            except Exception as e:
                print(f"Erreur sur un article: {e}")
                continue
                
        return listings[:8]  # Limite à 8 résultats
        
    except Exception as e:
        print(f"Erreur de connexion à Vinted: {e}")
        return []

def send_to_discord(item):
    embed = {
        "title": f"👕 {item['title']}",
        "description": f"**Prix:** {item['price']}",
        "url": item['url'],
        "color": 3447003,  # Bleu
        "thumbnail": {"url": item['image']} if item['image'] else None,
        "footer": {"text": f"🕒 {item['time']}"}
    }
    
    payload = {
        "username": "Vinted Scout - Ralph Lauren",
        "avatar_url": "https://i.imgur.com/JY5jHHT.png",
        "embeds": [embed]
    }
    
    try:
        requests.post(DISCORD_WEBHOOK, json=payload)
    except Exception as e:
        print(f"Erreur d'envoi à Discord: {e}")

if __name__ == "__main__":
    print("🔍 Scan des nouvelles annonces Ralph Lauren...")
    new_items = get_vinted_listings()
    
    if new_items:
        print(f"✅ {len(new_items)} nouvelles annonces trouvées!")
        for item in new_items:
            send_to_discord(item)
    else:
        print("❌ Aucune nouvelle annonce trouvée")
