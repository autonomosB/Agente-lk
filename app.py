from flask import Flask, render_template, request
import openai
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Configura tu clave de API de OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/', methods=['GET', 'POST'])
def index():
    generated_post = ""
    error_message = ""
    if request.method == 'POST':
        topic = request.form.get('topic', '').strip()
        tone = request.form.get('tone', 'profesional')  # Nuevo campo para el tono
        industry = request.form.get('industry', 'general')  # Nuevo campo para la industria
        
        if not topic:
            error_message = "Por favor, ingresa un tema para el post."
        else:
            generated_post = generate_post(topic, tone, industry)
    return render_template('index.html', generated_post=generated_post, error_message=error_message)

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

# Agregar nueva ruta para previsualización
@app.route('/preview', methods=['POST'])
def preview_post():
    topic = request.form.get('topic', '')
    tone = request.form.get('tone', 'profesional')
    industry = request.form.get('industry', 'general')
    preview = generate_post(topic, tone, industry)
    return jsonify({'preview': preview})

if __name__ == '__main__':
    app.run(debug=True)