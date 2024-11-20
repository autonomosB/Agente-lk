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
    if request.method == 'POST':
        topic = request.form.get('topic')
        if topic:
            generated_post = generate_post(topic)
    return render_template('index.html', generated_post=generated_post)

def generate_post(topic):
    # Generar el contenido del post utilizando la API de OpenAI
    prompt = f"Genera un post para LinkedIn sobre el tema '{topic}'. Incluye un título atractivo, un cuerpo informativo y hashtags relevantes."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # O el modelo que prefieras
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True)