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
    <div class="icon-card" onclick="navigate(this, '/consultar')">
        <i class="ri-database-2-line"></i>
        <span>Inadimplência</span>
    </div>

    <div class="icon-card" onclick="navigate(this, '/graficos')">
        <i class="ri-bar-chart-box-line"></i>
        <span>Gráficos</span>
    </div>

    <div class="icon-card">
        <i class="ri-edit-2-line"></i>
        <span>Editar Dados</span>
    </div>

    <div class="icon-card correlacao" onclick="navigate(this, '/correlacao')">
        <i class="ri-node-tree"></i>
        <span>Correlação</span>
    </div>
</div>

<form>

    <div class="upload-group">
        <label class="upload-label">Arquivo de Inadimplência</label>
        <input type="file" id="inad" class="file-input">
        <label for="inad" class="file-box">
            <i class="ri-upload-cloud-2-line"></i>
            <span class="file-name" id="name-inad">Selecionar arquivo...</span>
        </label>
    </div>

    <div class="upload-group">
        <label class="upload-label">Arquivo de Taxa Selic</label>
        <input type="file" id="selic" class="file-input">
        <label for="selic" class="file-box">
            <i class="ri-upload-cloud-2-line"></i>
            <span class="file-name" id="name-selic">Selecionar arquivo...</span>
        </label>
    </div>

    <button type="submit">Fazer Upload</button>

</form>

</div>

<script>
function navigate(element, url) {
    element.classList.add("active");
    setTimeout(() => {
        window.location.href = url;
    }, 300);
}

document.getElementById("inad").addEventListener("change", function(){
    document.getElementById("name-inad").textContent =
        this.files.length ? this.files[0].name : "Selecionar arquivo...";
});

document.getElementById("selic").addEventListener("change", function(){
    document.getElementById("name-selic").textContent =
        this.files.length ? this.files[0].name : "Selecionar arquivo...";
});
</script>

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
        name = ['data','inadimplencia'],
        header = 0
    )

    selic_df = pd.read_csv(
        selic_file,
        sep = ";",
        name = ['data', 'selic_diaria'],
        header = 0
    )

    inad_df['data'] = pd.to_datetime(inad_df['data'], format='%d/%m/%Y')
    selic_df['data'] = pd.to_datetime(selic_df['data'], format='%d/%m/%Y')

    inad_df['mes'] = inad_df['data'].dt.to_period('M').astype(str)
    selic_df['mes'] = selic_df['data'].dt.to_period('M').astype(str)

    inad_mensal = inad_df[['mes', 'inadimplencia']].drop_duplicates()
    selic_mensal = selic_df.grouby('mes')['selic_diaria'].mean().reset_index()

    with sqlite3.connect(DB_PATH) as conn:
        inad_mensal.to_sql('inadimplencia', conn, if_exists = 'replace', index = 'False') 
        selic_mensal.to_sql('inadimplencia', conn, if_exists = 'replace', index = 'False')

    return jsonify({'Mensagem':'Dados armazenados com sucesso.'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)