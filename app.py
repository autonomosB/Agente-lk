from flask import Flask, render_template, request, jsonify
import openai
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime
import time

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Configura tu clave de API de OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_latest_industry_news(industry):
    try:
        # Diferentes RSS feeds según la industria
        rss_feeds = {
            "tecnologia": "https://feeds.feedburner.com/TechCrunch/",
            "finanzas": "https://www.investing.com/rss/news.rss",
            "marketing": "https://www.marketingdive.com/feeds/news/",
            "recursos_humanos": "https://www.hrmorning.com/feed/",
            "general": "https://news.google.com/news/rss"
        }
        
        feed_url = rss_feeds.get(industry)
        if feed_url:
            news = feedparser.parse(feed_url)
            return [entry.title for entry in news.entries[:3]]
        return []
    except Exception:
        return []

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_post = ""
    error_message = ""
    is_loading = False
    
    if request.method == 'POST':
        is_loading = True
        topic = request.form.get('topic', '').strip()
        industry = request.form.get('industry', 'general')
        tone = request.form.get('tone', 'profesional')
        
        if not topic:
            error_message = "Por favor, ingresa un tema para el post."
        else:
            # Simular un pequeño retraso para mostrar el spinner
            time.sleep(1)
            generated_post = generate_post(topic, tone, industry)
        
        is_loading = False
    
    return render_template('index.html', 
                         generated_post=generated_post, 
                         error_message=error_message,
                         is_loading=is_loading)

def generate_post(topic, tone="profesional", industry="general"):
    # Diccionario de emojis por industria
    industry_emojis = {
        "tecnologia": "💻 🚀 🔧",
        "marketing": "📱 📊 🎯",
        "recursos_humanos": "👥 🤝 📈",
        "finanzas": "💰 📊 💹",
        "general": "✨ 📝 💡"
    }
    
    # Seleccionar emojis según la industria
    emojis = industry_emojis.get(industry, industry_emojis["general"])
    
    # Obtener noticias recientes de la industria
    latest_news = get_latest_industry_news(industry)
    news_context = "\n".join(latest_news) if latest_news else ""
    
    prompt = f"""Crea un post profesional para LinkedIn sobre '{topic}' para la industria de {industry} 
    con un tono {tone}, siguiendo esta estructura:

    1. Título llamativo (máximo 100 caracteres) {emojis[0]}
    2. Introducción que enganche (2-3 líneas) {emojis[1]}
    3. Cuerpo del mensaje estructurado:
       - Un dato estadístico impactante
       - Una experiencia personal o caso de éxito
       - Una lección aprendida o insight clave
       - Tips o consejos prácticos
    4. Llamada a la acción clara y específica
    5. 3-5 hashtags relevantes y estratégicos

    Contexto actual de la industria:
    {news_context}

    Requisitos adicionales:
    - Incluye preguntas retóricas para generar engagement
    - Usa viñetas o números para mejor legibilidad
    - Mantén párrafos cortos (máximo 3 líneas)
    - Incluye métricas o datos específicos del {industry}
    - Usa emojis estratégicamente: {emojis}"""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": f"""Eres un experto en marketing digital y creación de contenido 
                para LinkedIn especializado en {industry}. Tu objetivo es crear posts profesionales que:
                1. Generen alto engagement
                2. Aporten valor real
                3. Demuestren autoridad en el tema
                4. Incentiven la conversación
                5. Sean fácilmente escaneables"""},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
            presence_penalty=0.6,
            frequency_penalty=0.6
        )
        
        # Procesar y formatear la respuesta
        content = response['choices'][0]['message']['content']
        return content.replace('\n', '<br>')  # Convertir saltos de línea para HTML
        
    except Exception as e:
        return f"Error al generar el contenido: {str(e)}"

@app.route('/preview', methods=['POST'])
def preview_post():
    topic = request.form.get('topic', '')
    tone = request.form.get('tone', 'profesional')
    industry = request.form.get('industry', 'general')
    preview = generate_post(topic, tone, industry)
    return jsonify({'preview': preview})

if __name__ == '__main__':
    app.run(debug=True)