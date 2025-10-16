import requests
from bs4 import BeautifulSoup

def get_html(url):
    headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/141.0.0.0 Safari/537.36')
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            print(f"⚠️ Error {response.status_code} al acceder a {url}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"⚠️ Error de conexión: {e}")
        return None

def parse_product_data(html):
    soup = BeautifulSoup(html, 'html.parser')

    # Seleccionar todos los resultados
    items = soup.select("ol.ui-search-layout li.ui-search-layout__item")
    if not items:
        return []

    productos = []
    for item in items:
        # Precio
        price = item.select_one("div.poly-price__current")
        current_price = price.select_one("span.andes-money-amount__fraction") if price else None
        current_price = current_price.text.strip() if current_price else "Sin precio"
        price = price.text.strip() if price else "Sin precio"


        current_price = int(current_price.replace(',', '')) if current_price != "Sin precio" else current_price

        # Marca
        brand_tag = item.select_one("span.poly-component__brand")
        brand = brand_tag.text.strip() if brand_tag else "Sin marca"

        # Título y enlace
        link_tag = item.select_one("a.poly-component__title")
        if link_tag:
            title = link_tag.text.strip()
            link = link_tag['href']
        else:
            title = "Sin título"
            link = "Sin enlace"

        productos.append({
            "marca": brand,
            "titulo": title,
            "link": link,
            "precio": current_price
        })

    return productos

def get_item_info(item_name):
    item_name = item_name.lower().replace(' ', '-')
    stores = ['amora-beauty-market', 'the-fragrance']

    results = {}

    for store in stores:
        url = f'https://listado.mercadolibre.com.mx/tienda/{store}/{item_name}?sb=storefront_url#D[A:{item_name}]'
        print(f"🔍 Buscando en {store}...")

        html = get_html(url)
        if not html:
            results[store] = []
            continue

        results[store] = parse_product_data(html)

    return results

def show_results(item_name, results):
    print("\n==========================")
    print(f"🧴 Resultados para: {item_name.capitalize()}")
    print("==========================")

    for store, productos in results.items():
        print(f"🏬 {store}")
        if not productos:
            print("   ⚠️ No se encontraron productos.\n")
            continue

        for i, p in enumerate(productos, 1):
            print(f"   {i}. 🏷️ Marca: {p['marca']}")
            print(f"      💬 Producto: {p['titulo']}")
            print(f"      🔗 Link: {p['link']}")
            print(f"      💲 Precio: {p['precio']}\n")

def evaluate_price(item, resultados):
    precios = []
    for tienda, productos in resultados.items():
        for producto in productos:
            if producto['precio'] != "Sin precio":
                precios.append((producto['precio'], tienda, producto['link']))

    if not precios:
        print("⚠️ No se encontraron precios para evaluar.")
        return

    print(f"🏆 Mejor precio para '{item}':")
    print("===================================")
    print("   Productos con precio menor a $2000:")
    for i, precios in enumerate(precios, 1):
        
        if precios[0] < 700:
            print(f"   {i}. 💲 Precio: {precios[0]} - Tienda: {precios[1]} - Link: {precios[2]}")

    if not precios:
        print("⚠️ No se encontraron precios para evaluar.")
        return

if __name__ == "__main__":
    item = "Eros"
    resultados = get_item_info(item)
    show_results(item, resultados)

    evaluate_price(item, resultados)
