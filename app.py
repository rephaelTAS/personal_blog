from flask import Flask, render_template, request, redirect, url_for, session
import os
import json
from datetime import datetime

# Configurações básicas do Flask
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Alterar para uma chave aleatória segura
ARTICLES_DIR = 'articles/'  # Diretório onde os artigos serão salvos

# Helper: Carregar artigos do diretório
def load_articles():
    articles = []
    for filename in os.listdir(ARTICLES_DIR):
        if filename.endswith('.json'):
            try:
                with open(os.path.join(ARTICLES_DIR, filename), 'r') as f:
                    articles.append(json.load(f))
            except json.JSONDecodeError:
                print(f"Erro ao decodificar JSON no arquivo: {filename}")
            except Exception as e:
                print(f"Erro ao ler o arquivo {filename}: {e}")
    return sorted(articles, key=lambda x: x['date'], reverse=True)

# Helper: Verificar credenciais de autenticação
def check_auth(username, password):
    return username == 'admin' and password == 'password'  # Alterar conforme necessário

# Rotas Públicas
@app.route('/')
def home():
    """Página inicial com a lista de artigos."""
    articles = load_articles()
    return render_template('home.html', articles=articles)

@app.route('/article/<filename>')
def article(filename):
    """Exibir um artigo específico."""
    try:
        with open(os.path.join(ARTICLES_DIR, filename), 'r') as f:
            article = json.load(f)
        return render_template('article.html', article=article)
    except FileNotFoundError:
        return "Artigo não encontrado", 404

# Rotas de Administração
@app.route('/admin/dashboard', methods=['GET'])
def dashboard():
    """Painel de administração com a lista de artigos."""
    if 'username' not in session:
        return redirect(url_for('login'))
    articles = load_articles()
    return render_template('dashboard.html', articles=articles)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_article():
    """Adicionar um novo artigo."""
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        date = request.form['date']
        filename = f"{title.replace(' ', '_').lower()}.json"
        article = {"title": title, "content": content, "date": date}
        with open(os.path.join(ARTICLES_DIR, filename), 'w') as f:
            json.dump(article, f)
        return redirect(url_for('dashboard'))
    return render_template('add_article.html')

@app.route('/admin/edit/<filename>', methods=['GET', 'POST'])
def edit_article(filename):
    """Editar um artigo existente."""
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        with open(os.path.join(ARTICLES_DIR, filename), 'r') as f:
            article = json.load(f)
    except FileNotFoundError:
        return "Artigo não encontrado", 404

    if request.method == 'POST':
        article['title'] = request.form['title']
        article['content'] = request.form['content']
        article['date'] = request.form['date']
        with open(os.path.join(ARTICLES_DIR, filename), 'w') as f:
            json.dump(article, f)
        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', article=article)

@app.route('/admin/delete/<filename>', methods=['POST'])
def delete_article(filename):
    """Excluir um artigo."""
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        os.remove(os.path.join(ARTICLES_DIR, filename))
    except FileNotFoundError:
        return "Artigo não encontrado", 404
    return redirect(url_for('dashboard'))

# Rotas de Autenticação
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_auth(username, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Fazer logout e encerrar a sessão."""
    session.pop('username', None)
    return redirect(url_for('home'))

# Execução da aplicação
if __name__ == '__main__':
    os.makedirs(ARTICLES_DIR, exist_ok=True)  # Criar o diretório se não existir
    app.run(debug=True)
