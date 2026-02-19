from flask import Flask

app = Flask(__name__)

@app.route('/')
def pagina_inicial():
    return "<marquee>Olá Mundo</marquee>"

@app.route('/Contato')
def pagina_sobre():
    return "<marquee>Sou a pagina de Contato</marquee>"

if __name__ == '__main__':
    app.run(debug=True)