from flask import Flask, request, Response
import threading

app = Flask(__name__)

ultima_foto = None
# Criamos a "campainha" que vai avisar as rotas quando uma imagem nova chegar
nova_foto_condicao = threading.Condition()

@app.route('/upload', methods=['POST'])
def upload():
    global ultima_foto
    ultima_foto = request.data  
    
    # Assim que a foto chega do ESP32, nós "tocamos a campainha"
    with nova_foto_condicao:
        nova_foto_condicao.notify_all()
        
    return "Foto recebida", 200

@app.route('/foto')
def get_foto():
    global ultima_foto
    if ultima_foto:
        response = Response(ultima_foto, mimetype='image/jpeg')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return "Nenhuma foto ainda", 404

@app.route('/blynk_stream')
def blynk_stream():
    def generate():
        while True:
            with nova_foto_condicao:
                # O servidor "congela" AQUI e espera. 
                # Não há delay fixo. Ele acorda no exato instante em que a campainha toca.
                nova_foto_condicao.wait()
                
            if ultima_foto:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + ultima_foto + b'\r\n')
            
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    html = """
    <!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'></head>
    <body style='text-align:center; background-color:#1e1e1e; color:white; font-family:sans-serif;'>
    <h2>Conexao Global (Zero Delay Interno)</h2>
    
    <img id='cam' src='/foto' style='width:100%; max-width:640px; border: 2px solid #4CAF50; border-radius: 10px;' onload='refresh()' onerror='refresh()' />
    
    <script>
    function refresh() {
      // Pedimos a foto numa velocidade extrema (10ms). 
      // Se não houver foto nova, o navegador não sente o tranco.
      setTimeout(function() {
        document.getElementById('cam').src = '/foto?' + Math.random();
      }, 10); 
    }
    </script>
    </body></html>
    """
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
