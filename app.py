import gradio as gr
from bs4 import BeautifulSoup
import requests

css = """
#col-container {
    margin: 0 auto;
    max-width: 290px;
}
"""

def fetch_languages():
    language_symbols = {}
    try:
        response = requests.get("https://www.wikipedia.org/")
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        for option in soup.find_all('option'):
            language = option.text.strip()
            symbol = option['lang']
            language_symbols[language] = symbol

        return language_symbols, list(language_symbols.keys())
    except requests.exceptions.RequestException as e:
        return {}, [f"Error fetching language data: {e}"]

def fetch_data(selected_topic, selected_language, language_symbols):
    symbol = language_symbols.get(selected_language)
    try:
        url = f"https://{symbol}.wikipedia.org/wiki/{selected_topic}"
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        main_content = soup.find('div', {'id': 'mw-content-text'})
        filtered_content = ""

        if main_content:
            for element in main_content.descendants:
                if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    filtered_content += "\n" + element.get_text(strip=True).upper() + "\n"
                elif element.name == 'p':
                    filtered_content += element.get_text(strip=True) + "\n"

        return filtered_content
    except requests.exceptions.RequestException as e:
        return f"Error fetching Wikipedia content: {e}"

def fetch_image(query):
    try:
        search_url = f"https://www.google.com/search?q={query}&tbm=isch"
        response = requests.get(search_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        for img in soup.find_all('img'):
            image_url = img.get('src')
            if image_url and image_url.startswith("http"):
                img_data = requests.get(image_url).content
                img_path = f"{query}.jpg"
                with open(img_path, 'wb') as handler:
                    handler.write(img_data)
                return img_path

    except requests.exceptions.RequestException as e:
        return f"Error fetching image URLs: {e}"

language_symbols, languages = fetch_languages()

def gradio_interface(selected_language, selected_topic):
    wikipedia_content = fetch_data(selected_topic, selected_language, language_symbols)
    image_path = fetch_image(selected_topic)
    return wikipedia_content, image_path

with gr.Blocks(css=css, theme="bethecloud/storj_theme",) as demo:
    gr.Markdown("# WIKI SCRAP 🌐")
    language_input = gr.Dropdown(choices=languages, label="📍Select Language")
    topic_input = gr.Textbox(label="📍Enter Topic")
    scrape_button = gr.Button("Run🚀")
    wikipedia_output = gr.Textbox(label="Wikipedia Content", lines=15)
    image_output = gr.Image(label="Related Image", type="filepath")

    scrape_button.click(fn=gradio_interface, inputs=[language_input, topic_input], outputs=[wikipedia_output, image_output])

demo.launch()