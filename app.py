from flask import Flask, request, Response

app = Flask(__name__)

# Variável global que vai guardar a última foto recebida do robô na memória RAM da nuvem
ultima_foto = None

# Rota 1: Onde o ESP32-CAM vai arremessar a foto (Método POST)
@app.route('/upload', methods=['POST'])
def upload():
    global ultima_foto
    ultima_foto = request.data  # Salva os bytes crus do JPEG
    return "Foto recebida", 200

# Rota 2: Onde o site pega a foto crua
@app.route('/foto')
def get_foto():
    global ultima_foto
    if ultima_foto:
        return Response(ultima_foto, mimetype='image/jpeg')
    return "Nenhuma foto ainda", 404

# Rota 3: A página principal que você vai acessar do seu celular (O painel TRACC)
@app.route('/')
def index():
    html = """
    <!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'></head>
    <body style='text-align:center; background-color:#1e1e1e; color:white; font-family:sans-serif;'>
    <h2>TRACC - Conexao Global</h2>
    
    <img id='cam' src='/foto' style='width:100%; max-width:640px; border: 2px solid #4CAF50; border-radius: 10px;' onload='refresh()' onerror='refresh()' />
    
    <script>
    function refresh() {
      setTimeout(function() {
        document.getElementById('cam').src = '/foto?' + Math.random();
      }, 50); // Puxa a nova foto da nuvem a cada 50 milissegundos
    }
    </script>
    </body></html>
    """
    return html

if __name__ == '__main__':
    # Roda o servidor na porta 5000
    app.run(host='0.0.0.0', port=5000)
