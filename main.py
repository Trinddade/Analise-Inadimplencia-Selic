from flask import Flask, request, jsonify, render_template_string
import pandas as pd
import sqlite3
import os
import config
import plotly.graph_objs as go
import dash
from dash import Dash, html, dcc
import numpy as np

app = Flask(__name__)
DB_PATH = config.DB_PATH

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS inadimplencia(
                        mes TEXT PRIMARY KEY,
                        inadimplencia REAL
                       )
''')
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS selic(
                        mes TEXT PRIMARY KEY,
                        selic_diaria REAL
                        ) 
''')
        conn.commit()

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="pt-br">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Painel Econômico</title>

<link href="https://cdn.jsdelivr.net/npm/remixicon@4.2.0/fonts/remixicon.css" rel="stylesheet"/>

<style>
:root {
    --bg: #f5f5f7;
    --card: rgba(255,255,255,0.75);
    --text: #1d1d1f;
    --subtext: #6e6e73;
    --primary: #0071e3;
    --border: #d2d2d7;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}

body {
    background: linear-gradient(180deg, #f5f5f7, #e9e9ee);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
    color: var(--text);
}

.container {
    width: 100%;
    max-width: 750px;
    padding: 50px;
    border-radius: 28px;
    background: var(--card);
    backdrop-filter: blur(20px);
    box-shadow: 0 25px 60px rgba(0,0,0,0.08);
}

h1 {
    text-align: center;
    font-size: 26px;
    font-weight: 600;
    margin-bottom: 45px;
}

/* ===== GRID PERSONALIZADO ===== */
.icon-menu {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-bottom: 50px;
}

/* Faz Correlação ficar abaixo de Gráficos */
.icon-card.correlacao {
    grid-column: 2;
    grid-row: 2;
}

.icon-card {
    background: white;
    padding: 28px 20px;
    border-radius: 22px;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(.25,.8,.25,1);
    box-shadow: 0 10px 25px rgba(0,0,0,0.06);
    position: relative;
    overflow: hidden;
}

.icon-card i {
    font-size: 32px;
    color: var(--primary);
    transition: 0.3s;
}

.icon-card span {
    display: block;
    margin-top: 12px;
    font-size: 14px;
    color: var(--subtext);
}

/* Animação estilo Linux */
.icon-card:hover {
    transform: translateY(-12px) scale(1.07);
    box-shadow: 0 30px 50px rgba(0,0,0,0.18);
}

.icon-card:hover i {
    transform: scale(1.15) rotate(-5deg);
}

/* Ripple */
.icon-card::after {
    content: "";
    position: absolute;
    width: 0;
    height: 0;
    background: rgba(0,113,227,0.15);
    border-radius: 50%;
    transform: scale(0);
    opacity: 0;
}

.icon-card.active::after {
    animation: ripple 0.6s ease-out;
}

@keyframes ripple {
    0% {
        width: 0;
        height: 0;
        opacity: 0.6;
        transform: scale(0);
    }
    100% {
        width: 350px;
        height: 350px;
        opacity: 0;
        transform: scale(1);
    }
}

/* ===== UPLOAD ===== */
.upload-group {
    margin-bottom: 25px;
}

.upload-label {
    font-size: 14px;
    color: var(--subtext);
    margin-bottom: 8px;
    display: block;
}

.file-input {
    display: none;
}

.file-box {
    display: flex;
    align-items: center;
    padding: 16px 18px;
    border-radius: 18px;
    border: 1px solid var(--border);
    background: white;
    cursor: pointer;
    transition: 0.25s;
}

.file-box:hover {
    border-color: var(--primary);
    box-shadow: 0 15px 30px rgba(0,113,227,0.15);
    transform: translateY(-3px);
}

.file-box i {
    font-size: 20px;
    color: var(--primary);
    margin-right: 12px;
}

.file-name {
    font-size: 14px;
    color: var(--subtext);
}

button {
    width: 100%;
    padding: 15px;
    border-radius: 20px;
    border: none;
    background: var(--primary);
    color: white;
    font-size: 15px;
    font-weight: 500;
    cursor: pointer;
    transition: 0.3s;
    margin-top: 15px;
}

button:hover {
    transform: scale(1.05);
    box-shadow: 0 20px 35px rgba(0,113,227,0.3);
}
</style>
</head>

<body>

<div class="container">

<h1>Painel Econômico</h1>

<div class="icon-menu">
   

    <a href='/consultar'> Consultar</a>

    <a href='/editar_selic'> Editar Selic</a>
                                  
    <a href='/graficos'>graficos</a>

    <a href='/editar_inadimplencia'>Editar Dados</a>


    <div class="icon-card correlacao" onclick="navigate(this, '/correlacao')">
        <i class="ri-node-tree"></i>
        <span>Correlação</span>
    </div>
</div>

<form action="/upload" method="POST" enctype="multipart/form-data">


        <label class="upload-label">Arquivo de Inadimplência</label>
        <input type="file" name="campo_inadimplencia">
        

        <label class="upload-label">Arquivo de Taxa Selic</label>
        <input type="file" name="campo_selic">
    


    <button type="submit">Fazer Upload</button>

</form>

</div>

</body>
</html>
''')


@app.route('/upload', methods=['POST', 'GET'])
def upload():
    inad_file = request.files.get('campo_inadimplencia')
    selic_file = request.files.get('campo_selic')

    if not inad_file or not selic_file:
        return jsonify({"Erro":"Ambos os dados devem ser enviados"})
    
    inad_df = pd.read_csv(
        inad_file,
        sep = ";",
        names = ['data','inadimplencia'],
        header = 0
    )

    selic_df = pd.read_csv(
        selic_file,
        sep = ";",
        names = ['data', 'selic_diaria'],
        header = 0
    )

    inad_df['data'] = pd.to_datetime(inad_df['data'], format='%d/%m/%Y')
    selic_df['data'] = pd.to_datetime(selic_df['data'], format='%d/%m/%Y')

    inad_df['mes'] = inad_df['data'].dt.to_period('M').astype(str)
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str)

    inad_mensal = inad_df[['mes', 'inadimplencia']].drop_duplicates()
    selic_mensal = selic_df.groupby('mes')['selic_diaria'].mean().reset_index()

    with sqlite3.connect(DB_PATH) as conn:
        inad_mensal.to_sql('inadimplencia', conn, if_exists = 'replace', index = False) 
        selic_mensal.to_sql('selic', conn, if_exists = 'replace', index = False)

    return jsonify({'Mensagem':'Dados armazenados com sucesso.'})

@app.route('/consultar', methods=['POST','GET'])
def consultar():
    # Reservando a Vaga
    if request.method == "POST":
        tabela = request.form.get('campo_tabela')

        if tabela not in ['inadimplencia','selic']:
            return jsonify({'Erro','Tabela Inválida'})
        
        with sqlite3.connect(DB_PATH) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {tabela}", conn)
        return df.to_html(index=False)

    return render_template_string('''
    <h1> Consultar de Tabela </h1>
    <form method="POST" action="/consultar">
        <label> Escolha a Tabela</label>
        <select name="campo_tabela">
            <option value="inadimplencia"> Inadimplencia </option>
            <option value="selic"> Taxa Selic </option>
        </select>
        <input type="submit" value=" consultar ">                                      
    </form>
    <br>
    <a href="/"> Voltar </a>
''')

@app.route('/editar_inadimplencia', methods=['POST','GET'])
def editar_inadimplencia():

    if request.method == "POST":
        mes = request.form.get('campo_mes')
        novo_valor = request.form.get('campo_valor')

        try:
            novo_valor = float(novo_valor)
        except:
            return jsonify({'Erro':'Valor invalido'})
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE inadimplencia SET inadimplencia = ? WHERE mes = ?", (novo_valor, mes))
            conn.commit()
        return jsonify({'Mensagem':f'Valor atualizado com sucesso para {mes}'}) 

    return render_template_string('''
    <h1> Editar Inadimplencia</h1>
    <form method="POST" action="/editar_inadimplencia">
        <label for="campo_mes"> Mes (AAAA-MM) </label>
        <input type="text" name="campo_mes">
        </input><br>
        <label for="campo_valor"> Novo Valor de Inadimplencia </label>
        <input type="text" name="campo_valor">
        </input><br>
        <input type="submit" value=" Atualizar Dados "
        <br>
        <a href="/"> Voltar </a>           
    </form>
''')

@app.route('/editar_selic', methods=['POST','GET'])
def editar_selic():
   
   if request.method == 'POST':
       mes = request.form.get('campo_mes')
       novo_valor = request.form.get('campo_selic')

       try:
            novo_valor = float(novo_valor)
       except:
            return jsonify({'Erro':'Valor invalido'})
       
       with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE selic SET selic_diaria = ? WHERE mes = ?", (novo_valor, mes))
            conn.commit()
       return jsonify({'Mensagem':f'Valor atualizado com sucesso para {mes}'})
    

   return render_template_string('''
    <h1> Editar Selic</h1>
    <form method="POST" action="/editar_selic">
        <label for="campo_mes"> Mes (AAAA-MM) </label>
        <input type="text" name="campo_mes">
        </input><br>
        <label for="campo_selic"> Novo Valor de selic</label>
        <input type="text" name="campo_selic">
        </input><br>
        <input type="submit" value=" Atualizar Dados "
        <br>
        <a href="/"> Voltar </a>           
    </form>
''')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)