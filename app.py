import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'chave_segura_barbearia_prata'

def get_db_connection():

    if os.environ.get('VERCEL'):
        db_path = '/tmp/barbearia.db'
    else:
        db_path = 'barbearia.db'
    
    conn = sqlite3.connect(db_path)
    
    conn.row_factory = sqlite3.Row 
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            servico TEXT NOT NULL,
            barbeiro TEXT NOT NULL,
            data TEXT NOT NULL,
            hora TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    ''')
    
    # Email: adminbarbeiro@prata.com | Senha: barbeariaprata123!
    try:
        cursor.execute('''
            INSERT INTO usuarios (nome, email, senha, tipo) 
            VALUES (?, ?, ?, ?)
        ''', ('Yuri Prata', 'adminbarbeiro@prata.com', 'barbeariaprata123!', 'barbeiro'))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
        
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/agendar', methods=['POST'])
def agendar():
    nome = request.form.get('nome')
    telefone = request.form.get('telefone')
    servico = request.form.get('servico')
    barbeiro = request.form.get('barbeiro')
    data = request.form.get('data')
    hora = request.form.get('hora')

    if not all([nome, telefone, servico, barbeiro, data, hora]):
        flash('Por favor, preencha todos os campos!', 'erro-agendamento')
        return redirect(url_for('index'))

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO agendamentos (nome, telefone, servico, barbeiro, data, hora)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nome, telefone, servico, barbeiro, data, hora))
    conn.commit()
    conn.close()
    
    flash('Horário agendado com sucesso!', 'sucesso-agendamento')
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email, senha)).fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user['id']
        session['email'] = user['email']
        session['nome'] = user['nome']
        session['tipo'] = user['tipo']
        return redirect(url_for('admin'))
    
    flash('E-mail ou senha incorretos!', 'erro-login')
    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    
    if session.get('email') != 'adminbarbeiro@prata.com':
        flash('Acesso restrito apenas ao Yuri!', 'erro-login')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    agendamentos = conn.execute('SELECT * FROM agendamentos ORDER BY data DESC, hora DESC').fetchall()
    conn.close()
    
    return render_template('admin.html', agendamentos=agendamentos)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

app.debug = True

if __name__ == '__main__':
    app.run()
