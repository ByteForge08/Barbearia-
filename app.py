from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave_segura_barbearia'

def init_db():
    conn = sqlite3.connect('barbearia.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS agendamentos 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, telefone TEXT, servico TEXT, barbeiro TEXT, data TEXT, hora TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, email TEXT UNIQUE, senha TEXT, tipo TEXT)''')
    
    try:
        cursor.execute("INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                       ('Barbeiro Admin', 'adminbarbeiro@gmail.com', 'barbeariaprata123!', 'barbeiro'))
        conn.commit()
    except:
        pass 
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')
    conn = sqlite3.connect('barbearia.db')
    user = conn.execute('SELECT * FROM usuarios WHERE email = ? AND senha = ?', (email, senha)).fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user[0]
        session['email'] = user[2]
        session['tipo'] = user[4]
        return redirect(url_for('admin'))
    
    flash('E-mail ou senha incorretos!', 'erro-login')
    return redirect(url_for('index'))

@app.route('/agendar', methods=['POST'])
def agendar():
    nome = request.form.get('nome')
    telefone = request.form.get('telefone')
    servico = request.form.get('servico')
    barbeiro = request.form.get('barbeiro')
    data = request.form.get('data')
    hora = request.form.get('hora')

    try:
        conn = sqlite3.connect('barbearia.db')
        conn.execute('INSERT INTO agendamentos (nome, telefone, servico, barbeiro, data, hora) VALUES (?,?,?,?,?,?)', 
                     (nome, telefone, servico, barbeiro, data, hora))
        conn.commit()
        conn.close()
        flash('Horário agendado com sucesso!', 'sucesso-agendamento')
    except Exception as e:
        flash('Erro ao agendar. Tente novamente.', 'erro-agendamento')

    return redirect(url_for('index'))

@app.route('/admin')
def admin():
    if session.get('email') != 'adminbarbeiro@gmail.com':
        flash('Acesso restrito apenas ao administrador!', 'erro-login')
        return redirect(url_for('index'))

    conn = sqlite3.connect('barbearia.db')
    agendamentos = conn.execute('SELECT * FROM agendamentos ORDER BY data DESC, hora DESC').fetchall()
    conn.close()
    return render_template('admin.html', agendamentos=agendamentos)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)