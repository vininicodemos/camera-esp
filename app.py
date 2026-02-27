from flask import Flask, request, Response
import time

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
        # A MÁGICA AQUI: Obriga os roteadores e operadoras a não fazerem cache (atraso)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return "Nenhuma foto ainda", 404

@app.route('/blynk_stream')
def blynk_stream():
    def generate():
        while True:
            if ultima_foto:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + ultima_foto + b'\r\n')
            time.sleep(0.03) 
            
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    html = """
    <!DOCTYPE html><html><head><meta name='viewport' content='width=device-width, initial-scale=1.0'></head>
    <body style='text-align:center; background-color:#1e1e1e; color:white; font-family:sans-serif;'>
    <h2>Conexao Global</h2>
    
    <img id='cam' src='/foto' style='width:100%; max-width:640px; border: 2px solid #4CAF50; border-radius: 10px;' onload='refresh()' onerror='refresh()' />
    
    <script>
    function refresh() {
      setTimeout(function() {
        document.getElementById('cam').src = '/foto?' + Math.random();
      }, 30); 
    }
    </script>
    </body></html>
    """
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
