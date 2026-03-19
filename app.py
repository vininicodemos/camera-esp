from flask import Flask, request, Response

app = Flask(__name__)

ultima_foto = None

@app.route('/upload', methods=['POST'])
def upload():
    global ultima_foto
    ultima_foto = request.data  
    return "Foto recebida", 200

@app.route('/foto')
def get_foto():
    global ultima_foto
    if ultima_foto:
        response = Response(ultima_foto, mimetype='image/jpeg')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    return "Nenhuma foto ainda", 404

@app.route('/')
def index():
    html = """
    <!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'></head>
    <body style='text-align:center; background-color:#1e1e1e; color:white; font-family:sans-serif;'>
    <h2>Visao do Robo</h2>
    
    <img id='cam' src='/foto' style='width:100%; max-width:640px; border: 2px solid #4CAF50; border-radius: 10px;' />
    
    <script>
    const cam = document.getElementById('cam');
    
    // A MÁGICA ANTI-TRAVAMENTO: O navegador puxa as fotos como uma corrente.
    // Uma foto só é pedida QUANDO a anterior terminar de ser pintada na tela.
    cam.onload = function() {
        cam.src = '/foto?' + new Date().getTime();
    };
    
    // Se der algum erro (ex: Render demorar a responder), ele tenta de novo em meio segundo
    cam.onerror = function() {
        setTimeout(function() {
            cam.src = '/foto?' + new Date().getTime();
        }, 500);
    };
    </script>
    </body></html>
    """
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
