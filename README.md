# Análise de Inadimplência e Taxa Selic

Aplicação web desenvolvida em Python utilizando Flask para análise e manipulação de dados econômicos relacionados à inadimplência e à taxa Selic.

O sistema permite importar arquivos de dados, consultar tabelas, editar informações e realizar análises entre os indicadores.

## Funcionalidades

- Upload de arquivos de dados
- Consulta de tabelas de inadimplência e taxa Selic
- Edição de registros de inadimplência
- Edição de registros da taxa Selic
- Análise de correlação entre os indicadores
- Estrutura preparada para geração de gráficos

## Tecnologias utilizadas

- Python
- Flask
- SQLite
- HTML
- CSS

## Estrutura do projeto

```
Clarify
│
├── main.py
├── config.py
├── dados.db
│
├── static
│   └── style.css
│
├── templates
│   ├── index.html
│   ├── consultar.html
│   ├── editar_inadimplencia.html
│   └── editar_selic.html
│
├── inadimplencia.csv
└── taxa_selic.csv
```

## Objetivo

Este projeto foi desenvolvido com o objetivo de praticar desenvolvimento web com Python, manipulação de dados e análise de indicadores econômicos.
