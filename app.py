from flask import Flask, request, Response
import threading

app = Flask(__name__)

ultima_foto = None
nova_foto_condicao = threading.Condition()

@app.route('/upload', methods=['POST'])
def upload():
    global ultima_foto
    ultima_foto = request.data  
    
    with nova_foto_condicao:
        nova_foto_condicao.notify_all()
        
    return "Foto recebida", 200

@app.route('/foto')
def get_foto():
    global ultima_foto
    if ultima_foto:
        response = Response(ultima_foto, mimetype='image/jpeg')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return response
    return "Nenhuma foto ainda", 404

# ROTA DE VÍDEO FLUIDO (Totalmente independente)
@app.route('/stream')
def video_stream():
    def generate():
        while True:
            with nova_foto_condicao:
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
    <h2>TRACC - Visao do Robo</h2>
    
    <img id='cam' src='/stream' style='width:100%; max-width:640px; border: 2px solid #4CAF50; border-radius: 10px;' />
    
    </body></html>
    """
    return html

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
