import sqlite3, os
from datetime import datetime

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iflash.db')

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    return db

def init_db():
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT DEFAULT 'vendedor',
            ativo INTEGER DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT DEFAULT 'Cliente',
            cpf_cnpj TEXT,
            nome TEXT NOT NULL,
            nome_fantasia TEXT,
            rg TEXT,
            email TEXT,
            cep TEXT,
            endereco TEXT,
            numero TEXT,
            complemento TEXT,
            bairro TEXT,
            cidade TEXT,
            telefone TEXT,
            telefone2 TEXT,
            limite_credito REAL DEFAULT 0,
            observacoes TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_barras TEXT,
            descricao TEXT NOT NULL,
            marca TEXT,
            grupo TEXT,
            subgrupo TEXT,
            unidade TEXT DEFAULT 'UN',
            custo REAL DEFAULT 0,
            pct_lucro REAL DEFAULT 0,
            valor_venda REAL DEFAULT 0,
            estoque_atual REAL DEFAULT 0,
            estoque_minimo REAL DEFAULT 0,
            compativel TEXT,
            ativo INTEGER DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            ultima_venda DATETIME
        );
        CREATE TABLE IF NOT EXISTS dispositivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT, modelo TEXT,
            tipo TEXT DEFAULT 'Celular',
            armazenamento TEXT, cor TEXT, imei TEXT,
            estado TEXT DEFAULT 'Novo',
            custo REAL DEFAULT 0,
            valor_venda REAL DEFAULT 0,
            status TEXT DEFAULT 'Disponível',
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE,
            tipo TEXT DEFAULT 'OS',
            cliente_id INTEGER,
            data_emissao DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_finalizacao DATETIME,
            usuario TEXT,
            marca TEXT, modelo TEXT, imei TEXT,
            acessorios TEXT, sintomas TEXT,
            checklist TEXT,
            status TEXT DEFAULT 'Aguardando',
            valor_produto REAL DEFAULT 0,
            valor_servico REAL DEFAULT 0,
            total REAL DEFAULT 0,
            forma_pagamento TEXT,
            observacoes TEXT,
            assinatura_entrada TEXT,
            assinatura_saida TEXT,
            foto_entrada_1 TEXT, foto_entrada_2 TEXT, foto_entrada_3 TEXT,
            video_entrada TEXT,
            foto_saida_1 TEXT, foto_saida_2 TEXT, foto_saida_3 TEXT,
            video_saida TEXT,
            FOREIGN KEY (cliente_id) REFERENCES pessoas(id)
        );
        CREATE TABLE IF NOT EXISTS os_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            os_id INTEGER,
            produto_id INTEGER,
            descricao TEXT,
            valor_unit REAL DEFAULT 0,
            quantidade REAL DEFAULT 1,
            desconto REAL DEFAULT 0,
            valor_total REAL DEFAULT 0,
            funcionario TEXT,
            tipo TEXT DEFAULT 'produto',
            FOREIGN KEY (os_id) REFERENCES ordens_servico(id)
        );
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE,
            cliente_id INTEGER,
            data_emissao DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_finalizacao DATETIME,
            vendedor TEXT,
            status TEXT DEFAULT 'Aberta',
            valor_produto REAL DEFAULT 0,
            desconto REAL DEFAULT 0,
            total REAL DEFAULT 0,
            forma_pagamento TEXT,
            parcelas INTEGER DEFAULT 1,
            valor_parcela REAL DEFAULT 0,
            juros REAL DEFAULT 0,
            observacoes TEXT,
            FOREIGN KEY (cliente_id) REFERENCES pessoas(id)
        );
        CREATE TABLE IF NOT EXISTS venda_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER,
            produto_id INTEGER,
            descricao TEXT,
            estoque_atual REAL DEFAULT 0,
            valor_unit REAL DEFAULT 0,
            quantidade REAL DEFAULT 1,
            desconto_unit REAL DEFAULT 0,
            valor_total REAL DEFAULT 0,
            FOREIGN KEY (venda_id) REFERENCES vendas(id)
        );
        CREATE TABLE IF NOT EXISTS caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT DEFAULT 'entrada',
            descricao TEXT,
            valor REAL DEFAULT 0,
            forma_pagamento TEXT DEFAULT 'Dinheiro',
            referencia TEXT,
            usuario TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS abertura_caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE DEFAULT (DATE('now')),
            valor_inicial REAL DEFAULT 0,
            usuario TEXT,
            fechado INTEGER DEFAULT 0,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Usuários padrão
    if not db.execute("SELECT id FROM usuarios WHERE usuario='admin'").fetchone():
        db.executescript('''
            INSERT INTO usuarios (nome,usuario,senha,perfil) VALUES
                ('Administrador','admin','1234','admin'),
                ('Gerente','gerente','1234','gerente'),
                ('Vendedor','vendedor','1234','vendedor'),
                ('Caixa','caixa','1234','caixa'),
                ('Técnico','tecnico','1234','tecnico');
        ''')
        db.commit()

    # Dados de exemplo
    if not db.execute("SELECT id FROM pessoas LIMIT 1").fetchone():
        db.executescript('''
            INSERT INTO pessoas (tipo,cpf_cnpj,nome,telefone,cidade) VALUES
                ('Cliente','123.456.789-00','João Silva','(16) 99999-1234','Ribeirão Preto'),
                ('Cliente','987.654.321-00','Maria Souza','(16) 98888-5678','Ribeirão Preto'),
                ('Cliente','456.789.123-00','Carlos Lima','(16) 97777-9012','Ribeirão Preto'),
                ('Fornecedor','12.345.678/0001-90','TechParts Distribuidora','(11) 3333-4444','São Paulo'),
                ('Técnico','','Rafael Técnico','(16) 96666-7890','Ribeirão Preto');
            INSERT INTO produtos (codigo_barras,descricao,marca,grupo,custo,pct_lucro,valor_venda,estoque_atual,estoque_minimo,compativel) VALUES
                ('7891234560001','Bateria iPhone 14','Apple','Peças',45,166,120,8,3,'iPhone 14'),
                ('7891234560002','Tela iPhone 13 Original','Apple','Peças',180,94,350,3,2,'iPhone 13'),
                ('7891234560003','Cabo Lightning 1m','Apple','Acessórios',8,212,25,22,10,'iPhone'),
                ('7891234560004','Capinha iPhone 14 Silicone','Diversos','Acessórios',12,275,45,15,5,'iPhone 14'),
                ('7891234560005','Película Vidro iPhone 15','Diversos','Acessórios',5,300,20,30,10,'iPhone 15');
            INSERT INTO dispositivos (marca,modelo,tipo,armazenamento,cor,imei,estado,custo,valor_venda,status) VALUES
                ('Apple','iPhone 15','Celular','128GB','Preto','351234567890123','Novo',3800,5299,'Disponível'),
                ('Samsung','Galaxy S24','Celular','256GB','Cinza','352345678901234','Usado',2500,3800,'Disponível');
            INSERT INTO caixa (tipo,descricao,valor,forma_pagamento,referencia) VALUES
                ('entrada','OS0001 — Serviço concluído',380,'Pix','os'),
                ('entrada','Venda #0001 — Capinha + Película',65,'Dinheiro','venda'),
                ('saida','Compra peças TechParts',320,'Transferência','compra');
        ''')
        db.commit()
    db.close()
    print('  Banco de dados OK!')


import sqlite3, os
from datetime import datetime

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iflash.db')

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys = ON')
    return db

def init_db():
    db = get_db()
    db.executescript('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            perfil TEXT DEFAULT 'vendedor',
            ativo INTEGER DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS pessoas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT DEFAULT 'Cliente',
            cpf_cnpj TEXT,
            nome TEXT NOT NULL,
            nome_fantasia TEXT,
            rg TEXT,
            email TEXT,
            cep TEXT,
            endereco TEXT,
            numero TEXT,
            complemento TEXT,
            bairro TEXT,
            cidade TEXT,
            telefone TEXT,
            telefone2 TEXT,
            limite_credito REAL DEFAULT 0,
            observacoes TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_barras TEXT,
            descricao TEXT NOT NULL,
            marca TEXT,
            grupo TEXT,
            subgrupo TEXT,
            unidade TEXT DEFAULT 'UN',
            custo REAL DEFAULT 0,
            pct_lucro REAL DEFAULT 0,
            valor_venda REAL DEFAULT 0,
            estoque_atual REAL DEFAULT 0,
            estoque_minimo REAL DEFAULT 0,
            compativel TEXT,
            ativo INTEGER DEFAULT 1,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
            ultima_venda DATETIME
        );
        CREATE TABLE IF NOT EXISTS dispositivos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT, modelo TEXT,
            tipo TEXT DEFAULT 'Celular',
            armazenamento TEXT, cor TEXT, imei TEXT,
            estado TEXT DEFAULT 'Novo',
            custo REAL DEFAULT 0,
            valor_venda REAL DEFAULT 0,
            status TEXT DEFAULT 'Disponível',
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE,
            tipo TEXT DEFAULT 'OS',
            cliente_id INTEGER,
            data_emissao DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_finalizacao DATETIME,
            usuario TEXT,
            marca TEXT, modelo TEXT, imei TEXT,
            acessorios TEXT, sintomas TEXT,
            checklist TEXT,
            status TEXT DEFAULT 'Aguardando',
            valor_produto REAL DEFAULT 0,
            valor_servico REAL DEFAULT 0,
            total REAL DEFAULT 0,
            forma_pagamento TEXT,
            observacoes TEXT,
            assinatura_entrada TEXT,
            assinatura_saida TEXT,
            foto_entrada_1 TEXT, foto_entrada_2 TEXT, foto_entrada_3 TEXT,
            video_entrada TEXT,
            foto_saida_1 TEXT, foto_saida_2 TEXT, foto_saida_3 TEXT,
            video_saida TEXT,
            FOREIGN KEY (cliente_id) REFERENCES pessoas(id)
        );
        CREATE TABLE IF NOT EXISTS os_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            os_id INTEGER,
            produto_id INTEGER,
            descricao TEXT,
            valor_unit REAL DEFAULT 0,
            quantidade REAL DEFAULT 1,
            desconto REAL DEFAULT 0,
            valor_total REAL DEFAULT 0,
            funcionario TEXT,
            tipo TEXT DEFAULT 'produto',
            FOREIGN KEY (os_id) REFERENCES ordens_servico(id)
        );
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT UNIQUE,
            cliente_id INTEGER,
            data_emissao DATETIME DEFAULT CURRENT_TIMESTAMP,
            data_finalizacao DATETIME,
            vendedor TEXT,
            status TEXT DEFAULT 'Aberta',
            valor_produto REAL DEFAULT 0,
            desconto REAL DEFAULT 0,
            total REAL DEFAULT 0,
            forma_pagamento TEXT,
            parcelas INTEGER DEFAULT 1,
            valor_parcela REAL DEFAULT 0,
            juros REAL DEFAULT 0,
            observacoes TEXT,
            FOREIGN KEY (cliente_id) REFERENCES pessoas(id)
        );
        CREATE TABLE IF NOT EXISTS venda_itens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER,
            produto_id INTEGER,
            descricao TEXT,
            estoque_atual REAL DEFAULT 0,
            valor_unit REAL DEFAULT 0,
            quantidade REAL DEFAULT 1,
            desconto_unit REAL DEFAULT 0,
            valor_total REAL DEFAULT 0,
            FOREIGN KEY (venda_id) REFERENCES vendas(id)
        );
        CREATE TABLE IF NOT EXISTS caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT DEFAULT 'entrada',
            descricao TEXT,
            valor REAL DEFAULT 0,
            forma_pagamento TEXT DEFAULT 'Dinheiro',
            referencia TEXT,
            usuario TEXT,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS abertura_caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data DATE DEFAULT (DATE('now')),
            valor_inicial REAL DEFAULT 0,
            usuario TEXT,
            fechado INTEGER DEFAULT 0,
            criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Usuários padrão
    if not db.execute("SELECT id FROM usuarios WHERE usuario='admin'").fetchone():
        db.executescript('''
            INSERT INTO usuarios (nome,usuario,senha,perfil) VALUES
                ('Administrador','admin','1234','admin'),
                ('Gerente','gerente','1234','gerente'),
                ('Vendedor','vendedor','1234','vendedor'),
                ('Caixa','caixa','1234','caixa'),
                ('Técnico','tecnico','1234','tecnico');
        ''')
        db.commit()

    # Dados de exemplo
    if not db.execute("SELECT id FROM pessoas LIMIT 1").fetchone():
        db.executescript('''
            INSERT INTO pessoas (tipo,cpf_cnpj,nome,telefone,cidade) VALUES
                ('Cliente','123.456.789-00','João Silva','(16) 99999-1234','Ribeirão Preto'),
                ('Cliente','987.654.321-00','Maria Souza','(16) 98888-5678','Ribeirão Preto'),
                ('Cliente','456.789.123-00','Carlos Lima','(16) 97777-9012','Ribeirão Preto'),
                ('Fornecedor','12.345.678/0001-90','TechParts Distribuidora','(11) 3333-4444','São Paulo'),
                ('Técnico','','Rafael Técnico','(16) 96666-7890','Ribeirão Preto');
            INSERT INTO produtos (codigo_barras,descricao,marca,grupo,custo,pct_lucro,valor_venda,estoque_atual,estoque_minimo,compativel) VALUES
                ('7891234560001','Bateria iPhone 14','Apple','Peças',45,166,120,8,3,'iPhone 14'),
                ('7891234560002','Tela iPhone 13 Original','Apple','Peças',180,94,350,3,2,'iPhone 13'),
                ('7891234560003','Cabo Lightning 1m','Apple','Acessórios',8,212,25,22,10,'iPhone'),
                ('7891234560004','Capinha iPhone 14 Silicone','Diversos','Acessórios',12,275,45,15,5,'iPhone 14'),
                ('7891234560005','Película Vidro iPhone 15','Diversos','Acessórios',5,300,20,30,10,'iPhone 15');
            INSERT INTO dispositivos (marca,modelo,tipo,armazenamento,cor,imei,estado,custo,valor_venda,status) VALUES
                ('Apple','iPhone 15','Celular','128GB','Preto','351234567890123','Novo',3800,5299,'Disponível'),
                ('Samsung','Galaxy S24','Celular','256GB','Cinza','352345678901234','Usado',2500,3800,'Disponível');
            INSERT INTO caixa (tipo,descricao,valor,forma_pagamento,referencia) VALUES
                ('entrada','OS0001 — Serviço concluído',380,'Pix','os'),
                ('entrada','Venda #0001 — Capinha + Película',65,'Dinheiro','venda'),
                ('saida','Compra peças TechParts',320,'Transferência','compra');
        ''')
        db.commit()
    db.close()
    print('  Banco de dados OK!')


from flask import Flask, render_template, request, jsonify, send_from_directory
import sqlite3, os, socket, json, uuid
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'iflash2026'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB para vídeos

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
VIDEO_FOLDER  = os.path.join(UPLOAD_FOLDER, 'videos')
FOTO_FOLDER   = os.path.join(UPLOAD_FOLDER, 'os')
os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(FOTO_FOLDER, exist_ok=True)

JUROS_MES = 0.02
PARCELAS_SEM_JUROS = 6

# ── ROTAS ESTÁTICAS ───────────────────────────────
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/icon-192.png')
def icon192():
    return send_from_directory('.', 'icon-192.png')

@app.route('/icon-512.png')
def icon512():
    return send_from_directory('.', 'icon-512.png')

@app.route('/apple-touch-icon.png')
def apple_icon():
    return send_from_directory('.', 'apple-touch-icon.png')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('.', 'manifest.json')

# ── LOGIN ─────────────────────────────────────────
@app.route('/api/login', methods=['POST'])
def login():
    d = request.json
    db = get_db()
    u = db.execute('SELECT * FROM usuarios WHERE usuario=? AND senha=? AND ativo=1',
                   (d['usuario'], d['senha'])).fetchone()
    db.close()
    if u:
        return jsonify({'ok':True,'nome':u['nome'],'perfil':u['perfil'],'id':u['id']})
    return jsonify({'ok':False,'msg':'Usuário ou senha incorretos'}), 401

# ── USUÁRIOS ──────────────────────────────────────
@app.route('/api/usuarios', methods=['GET'])
def get_usuarios():
    db = get_db()
    rows = db.execute('SELECT id,nome,usuario,perfil,ativo FROM usuarios ORDER BY nome').fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/usuarios', methods=['POST'])
def add_usuario():
    d = request.json
    db = get_db()
    try:
        db.execute('INSERT INTO usuarios (nome,usuario,senha,perfil) VALUES (?,?,?,?)',
                   (d['nome'],d['usuario'],d['senha'],d.get('perfil','vendedor')))
        db.commit()
        return jsonify({'ok':True})
    except Exception as e:
        return jsonify({'ok':False,'msg':'Usuário já existe'}), 400
    finally:
        db.close()

@app.route('/api/usuarios/<int:id>', methods=['DELETE'])
def del_usuario(id):
    db = get_db()
    db.execute('UPDATE usuarios SET ativo=0 WHERE id=?',(id,))
    db.commit(); db.close()
    return jsonify({'ok':True})

# ── PESSOAS ───────────────────────────────────────
@app.route('/api/pessoas', methods=['GET'])
def get_pessoas():
    tipo  = request.args.get('tipo','')
    busca = request.args.get('busca','')
    db = get_db()
    q, p = 'SELECT * FROM pessoas WHERE 1=1', []
    if tipo:  q += ' AND tipo=?';  p.append(tipo)
    if busca:
        q += ' AND (nome LIKE ? OR cpf_cnpj LIKE ? OR telefone LIKE ?)'
        p += [f'%{busca}%']*3
    rows = db.execute(q+' ORDER BY nome', p).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/pessoas/<int:id>', methods=['GET'])
def get_pessoa(id):
    db = get_db()
    r = db.execute('SELECT * FROM pessoas WHERE id=?',(id,)).fetchone()
    db.close()
    return jsonify(dict(r) if r else {})

@app.route('/api/pessoas', methods=['POST'])
def add_pessoa():
    d = request.json
    db = get_db()
    db.execute('''INSERT INTO pessoas (tipo,cpf_cnpj,nome,nome_fantasia,rg,email,
                  cep,endereco,numero,complemento,bairro,cidade,telefone,telefone2,
                  limite_credito,observacoes)
                  VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
               (d.get('tipo','Cliente'),d.get('cpf_cnpj',''),d['nome'],
                d.get('nome_fantasia',''),d.get('rg',''),d.get('email',''),
                d.get('cep',''),d.get('endereco',''),d.get('numero',''),
                d.get('complemento',''),d.get('bairro',''),d.get('cidade',''),
                d.get('telefone',''),d.get('telefone2',''),
                d.get('limite_credito',0),d.get('observacoes','')))
    db.commit(); db.close()
    return jsonify({'ok':True})

@app.route('/api/pessoas/<int:id>', methods=['PUT'])
def update_pessoa(id):
    d = request.json
    db = get_db()
    db.execute('''UPDATE pessoas SET tipo=?,cpf_cnpj=?,nome=?,nome_fantasia=?,rg=?,email=?,
                  cep=?,endereco=?,numero=?,complemento=?,bairro=?,cidade=?,
                  telefone=?,telefone2=?,limite_credito=?,observacoes=? WHERE id=?''',
               (d.get('tipo','Cliente'),d.get('cpf_cnpj',''),d['nome'],
                d.get('nome_fantasia',''),d.get('rg',''),d.get('email',''),
                d.get('cep',''),d.get('endereco',''),d.get('numero',''),
                d.get('complemento',''),d.get('bairro',''),d.get('cidade',''),
                d.get('telefone',''),d.get('telefone2',''),
                d.get('limite_credito',0),d.get('observacoes',''),id))
    db.commit(); db.close()
    return jsonify({'ok':True})

@app.route('/api/pessoas/<int:id>', methods=['DELETE'])
def del_pessoa(id):
    db = get_db()
    db.execute('DELETE FROM pessoas WHERE id=?',(id,))
    db.commit(); db.close()
    return jsonify({'ok':True})

@app.route('/api/pessoas/<int:id>/historico')
def historico_pessoa(id):
    db = get_db()
    os_list = db.execute('SELECT * FROM ordens_servico WHERE cliente_id=? ORDER BY id DESC',(id,)).fetchall()
    vendas  = db.execute('SELECT * FROM vendas WHERE cliente_id=? ORDER BY id DESC',(id,)).fetchall()
    tot = sum(r['total'] for r in os_list) + sum(r['total'] for r in vendas)
    db.close()
    return jsonify({'ordens':[dict(r) for r in os_list],'vendas':[dict(r) for r in vendas],'total_gasto':round(tot,2)})

# ── PRODUTOS ──────────────────────────────────────
@app.route('/api/produtos', methods=['GET'])
def get_produtos():
    busca = request.args.get('busca','')
    db = get_db()
    q, p = 'SELECT * FROM produtos WHERE ativo=1', []
    if busca:
        q += ' AND (descricao LIKE ? OR codigo_barras LIKE ? OR marca LIKE ?)'
        p += [f'%{busca}%']*3
    rows = db.execute(q+' ORDER BY descricao', p).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/produtos', methods=['POST'])
def add_produto():
    d = request.json
    db = get_db()
    db.execute('''INSERT INTO produtos (codigo_barras,descricao,marca,grupo,subgrupo,unidade,
                  custo,pct_lucro,valor_venda,estoque_atual,estoque_minimo,compativel)
                  VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
               (d.get('codigo_barras',''),d['descricao'],d.get('marca',''),
                d.get('grupo',''),d.get('subgrupo',''),d.get('unidade','UN'),
                d.get('custo',0),d.get('pct_lucro',0),d.get('valor_venda',0),
                d.get('estoque_atual',0),d.get('estoque_minimo',0),d.get('compativel','')))
    db.commit(); db.close()
    return jsonify({'ok':True})

@app.route('/api/produtos/<int:id>', methods=['PUT'])
def update_produto(id):
    d = request.json
    db = get_db()
    db.execute('''UPDATE produtos SET codigo_barras=?,descricao=?,marca=?,grupo=?,
                  subgrupo=?,unidade=?,custo=?,pct_lucro=?,valor_venda=?,
                  estoque_atual=?,estoque_minimo=?,compativel=? WHERE id=?''',
               (d.get('codigo_barras',''),d['descricao'],d.get('marca',''),
                d.get('grupo',''),d.get('subgrupo',''),d.get('unidade','UN'),
                d.get('custo',0),d.get('pct_lucro',0),d.get('valor_venda',0),
                d.get('estoque_atual',0),d.get('estoque_minimo',0),d.get('compativel',''),id))
    db.commit(); db.close()
    return jsonify({'ok':True})

@app.route('/api/produtos/<int:id>', methods=['DELETE'])
def del_produto(id):
    db = get_db()
    db.execute('UPDATE produtos SET ativo=0 WHERE id=?',(id,))
    db.commit(); db.close()
    return jsonify({'ok':True})

# ── DISPOSITIVOS ──────────────────────────────────
@app.route('/api/dispositivos', methods=['GET'])
def get_dispositivos():
    busca = request.args.get('busca','')
    db = get_db()
    q, p = 'SELECT * FROM dispositivos WHERE 1=1', []
    if busca:
        q += ' AND (marca LIKE ? OR modelo LIKE ? OR imei LIKE ?)'
        p += [f'%{busca}%']*3
    rows = db.execute(q+' ORDER BY marca,modelo', p).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/dispositivos', methods=['POST'])
def add_dispositivo():
    d = request.json
    db = get_db()
    db.execute('''INSERT INTO dispositivos (marca,modelo,tipo,armazenamento,cor,imei,
                  estado,custo,valor_venda,status) VALUES (?,?,?,?,?,?,?,?,?,?)''',
               (d['marca'],d['modelo'],d.get('tipo','Celular'),d.get('armazenamento',''),
                d.get('cor',''),d.get('imei',''),d.get('estado','Novo'),
                d.get('custo',0),d.get('valor_venda',0),'Disponível'))
    db.commit(); db.close()
    return jsonify({'ok':True})

@app.route('/api/dispositivos/<int:id>', methods=['DELETE'])
def del_dispositivo(id):
    db = get_db()
    db.execute('DELETE FROM dispositivos WHERE id=?',(id,))
    db.commit(); db.close()
    return jsonify({'ok':True})

# ── UPLOAD FOTO / VÍDEO ───────────────────────────
@app.route('/api/upload/foto', methods=['POST'])
def upload_foto():
    if 'file' not in request.files:
        return jsonify({'ok':False,'msg':'Nenhum arquivo'}), 400
    f = request.files['file']
    ext = os.path.splitext(f.filename)[1].lower() or '.jpg'
    nome = f'{uuid.uuid4().hex}{ext}'
    f.save(os.path.join(FOTO_FOLDER, nome))
    return jsonify({'ok':True,'url':f'/static/uploads/os/{nome}','nome':nome})

@app.route('/api/upload/video', methods=['POST'])
def upload_video():
    if 'file' not in request.files:
        return jsonify({'ok':False,'msg':'Nenhum arquivo'}), 400
    f = request.files['file']
    ext = os.path.splitext(f.filename)[1].lower() or '.mp4'
    nome = f'{uuid.uuid4().hex}{ext}'
    f.save(os.path.join(VIDEO_FOLDER, nome))
    return jsonify({'ok':True,'url':f'/static/uploads/videos/{nome}','nome':nome})

# ── ORDENS DE SERVIÇO ─────────────────────────────
@app.route('/api/os', methods=['GET'])
def get_os():
    status = request.args.get('status','')
    busca  = request.args.get('busca','')
    db = get_db()
    q = '''SELECT os.*, p.nome as cliente_nome, p.telefone as cliente_tel,
           p.cpf_cnpj as cliente_cpf
           FROM ordens_servico os LEFT JOIN pessoas p ON os.cliente_id=p.id WHERE 1=1'''
    params = []
    if status: q += ' AND os.status=?'; params.append(status)
    if busca:
        q += ' AND (p.nome LIKE ? OR os.numero LIKE ? OR os.modelo LIKE ?)'
        params += [f'%{busca}%']*3
    rows = db.execute(q+' ORDER BY os.id DESC', params).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/os/<int:id>', methods=['GET'])
def get_os_one(id):
    db = get_db()
    r = db.execute('''SELECT os.*, p.nome as cliente_nome, p.telefone as cliente_tel,
                      p.cpf_cnpj as cliente_cpf
                      FROM ordens_servico os LEFT JOIN pessoas p ON os.cliente_id=p.id
                      WHERE os.id=?''',(id,)).fetchone()
    itens = db.execute('SELECT * FROM os_itens WHERE os_id=?',(id,)).fetchall()
    db.close()
    if not r: return jsonify({})
    d = dict(r)
    d['itens'] = [dict(i) for i in itens]
    return jsonify(d)

@app.route('/api/os', methods=['POST'])
def add_os():
    d = request.json
    db = get_db()
    n = db.execute('SELECT COUNT(*) as c FROM ordens_servico').fetchone()['c']
    numero = f'OS{str(n+1).zfill(4)}'
    val_prod = sum(i.get('valor_total',0) for i in d.get('itens',[]))
    val_serv = sum(i.get('valor_total',0) for i in d.get('servicos',[]))
    total = val_prod + val_serv
    db.execute('''INSERT INTO ordens_servico
                  (numero,tipo,cliente_id,usuario,marca,modelo,imei,acessorios,sintomas,
                   checklist,status,valor_produto,valor_servico,total,observacoes,
                   assinatura_entrada,foto_entrada_1,foto_entrada_2,foto_entrada_3,video_entrada)
                  VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
               (numero,d.get('tipo','OS'),d['cliente_id'],d.get('usuario',''),
                d.get('marca',''),d.get('modelo',''),d.get('imei',''),
                d.get('acessorios',''),d.get('sintomas',''),d.get('checklist',''),
                'Aguardando',val_prod,val_serv,total,d.get('observacoes',''),
                d.get('assinatura_entrada',''),
                d.get('foto_entrada_1',''),d.get('foto_entrada_2',''),d.get('foto_entrada_3',''),
                d.get('video_entrada','')))
    os_id = db.execute('SELECT last_insert_rowid() as id').fetchone()['id']
    for item in d.get('itens',[]):
        db.execute('''INSERT INTO os_itens (os_id,produto_id,descricao,valor_unit,quantidade,
                      desconto,valor_total,tipo) VALUES (?,?,?,?,?,?,?,?)''',
                   (os_id,item.get('produto_id'),item.get('descricao',''),
                    item.get('valor_unit',0),item.get('quantidade',1),
                    item.get('desconto',0),item.get('valor_total',0),'produto'))
    for svc in d.get('servicos',[]):
        db.execute('''INSERT INTO os_itens (os_id,descricao,valor_unit,quantidade,
                      valor_total,funcionario,tipo) VALUES (?,?,?,?,?,?,?)''',
                   (os_id,svc.get('descricao',''),svc.get('valor_unit',0),1,
                    svc.get('valor_total',0),svc.get('funcionario',''),'servico'))
    db.commit(); db.close()
    return jsonify({'ok':True,'numero':numero,'id':os_id})

@app.route('/api/os/<int:id>', methods=['PUT'])
def update_os(id):
    d = request.json
    db = get_db()
    campos, vals = [], []
    for f in ['status','forma_pagamento','observacoes','assinatura_saida',
              'foto_saida_1','foto_saida_2','foto_saida_3','video_saida',
              'valor_produto','valor_servico','total']:
        if f in d: campos.append(f+'=?'); vals.append(d[f])
    if d.get('status') in ('Concluído','Entregue'):
        campos.append('data_finalizacao=?')
        vals.append(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    if campos:
        vals.append(id)
        db.execute(f'UPDATE ordens_servico SET {",".join(campos)} WHERE id=?', vals)
        if d.get('status')=='Entregue' and d.get('total',0)>0:
            os_r = db.execute('SELECT numero,total FROM ordens_servico WHERE id=?',(id,)).fetchone()
            if os_r:
                db.execute('INSERT INTO caixa (tipo,descricao,valor,forma_pagamento,referencia) VALUES (?,?,?,?,?)',
                           ('entrada',f"OS {os_r['numero']} — Serviço",os_r['total'],
                            d.get('forma_pagamento','Dinheiro'),'os'))
        db.commit()
    db.close()
    return jsonify({'ok':True})

# ── VENDAS ────────────────────────────────────────
@app.route('/api/vendas', methods=['GET'])
def get_vendas():
    busca = request.args.get('busca','')
    db = get_db()
    q = '''SELECT v.*, p.nome as cliente_nome FROM vendas v
           LEFT JOIN pessoas p ON v.cliente_id=p.id WHERE 1=1'''
    params = []
    if busca:
        q += ' AND (p.nome LIKE ? OR v.numero LIKE ?)'
        params += [f'%{busca}%']*2
    rows = db.execute(q+' ORDER BY v.id DESC', params).fetchall()
    db.close()
    return jsonify([dict(r) for r in rows])

@app.route('/api/vendas/<int:id>', methods=['GET'])
def get_venda_one(id):
    db = get_db()
    r = db.execute('''SELECT v.*, p.nome as cliente_nome FROM vendas v
                      LEFT JOIN pessoas p ON v.cliente_id=p.id WHERE v.id=?''',(id,)).fetchone()
    itens = db.execute('SELECT * FROM venda_itens WHERE venda_id=?',(id,)).fetchall()
    db.close()
    if not r: return jsonify({})
    d = dict(r); d['itens'] = [dict(i) for i in itens]
    return jsonify(d)

@app.route('/api/vendas', methods=['POST'])
def add_venda():
    d = request.json
    db = get_db()
    n = db.execute('SELECT COUNT(*) as c FROM vendas').fetchone()['c']
    numero = f'VD{str(n+1).zfill(4)}'
    parcelas = int(d.get('parcelas',1))
    val_bruto = float(d.get('valor_produto',0))
    desconto  = float(d.get('desconto',0))
    base = val_bruto - desconto
    juros = 0.0
    if parcelas > PARCELAS_SEM_JUROS:
        juros = round(base * ((1+JUROS_MES)**parcelas - 1), 2)
    total = round(base + juros, 2)
    val_parcela = round(total/parcelas, 2) if parcelas > 0 else total
    db.execute('''INSERT INTO vendas (numero,cliente_id,vendedor,status,valor_produto,
                  desconto,total,forma_pagamento,parcelas,valor_parcela,juros,observacoes)
                  VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
               (numero,d['cliente_id'],d.get('vendedor',''),
                'Gravado',val_bruto,desconto,total,
                d.get('forma_pagamento','Dinheiro'),parcelas,val_parcela,juros,
                d.get('observacoes','')))
    vid = db.execute('SELECT last_insert_rowid() as id').fetchone()['id']
    for item in d.get('itens',[]):
        db.execute('''INSERT INTO venda_itens (venda_id,produto_id,descricao,estoque_atual,
                      valor_unit,quantidade,desconto_unit,valor_total) VALUES (?,?,?,?,?,?,?,?)''',
                   (vid,item.get('produto_id'),item.get('descricao',''),
                    item.get('estoque_atual',0),item.get('valor_unit',0),
                    item.get('quantidade',1),item.get('desconto_unit',0),item.get('valor_total',0)))
        if item.get('produto_id'):
            db.execute('UPDATE produtos SET estoque_atual=estoque_atual-?, ultima_venda=? WHERE id=?',
                       (item['quantidade'],datetime.now().strftime('%Y-%m-%d'),item['produto_id']))
    db.execute('INSERT INTO caixa (tipo,descricao,valor,forma_pagamento,referencia) VALUES (?,?,?,?,?)',
               ('entrada',f"Venda {numero}",total,d.get('forma_pagamento','Dinheiro'),'venda'))
    db.commit(); db.close()
    return jsonify({'ok':True,'numero':numero,'total':total,'valor_parcela':val_parcela,'juros':juros})

# ── CALCULAR PARCELAS ─────────────────────────────
@app.route('/api/calcular', methods=['POST'])
def calcular():
    d = request.json
    valor = float(d.get('valor',0))
    parcelas = int(d.get('parcelas',1))
    if parcelas <= PARCELAS_SEM_JUROS:
        juros, total = 0.0, valor
    else:
        juros = round(valor*((1+JUROS_MES)**parcelas-1), 2)
        total = round(valor+juros, 2)
    return jsonify({'juros':juros,'total':total,'valor_parcela':round(total/parcelas,2),
                    'sem_juros':parcelas<=PARCELAS_SEM_JUROS})

# ── CAIXA ─────────────────────────────────────────
@app.route('/api/caixa', methods=['GET'])
def get_caixa():
    data = request.args.get('data','')
    db = get_db()
    q, p = "SELECT * FROM caixa WHERE 1=1", []
    if data: q += " AND DATE(criado_em)=?"; p.append(data)
    else:    q += " AND DATE(criado_em)=DATE('now')"
    rows = db.execute(q+' ORDER BY criado_em DESC', p).fetchall()
    entradas = sum(r['valor'] for r in rows if r['tipo']=='entrada')
    saidas   = sum(r['valor'] for r in rows if r['tipo']=='saida')
    formas = {}
    for r in rows:
        if r['tipo']=='entrada':
            f = r['forma_pagamento']
            formas[f] = round(formas.get(f,0)+r['valor'],2)
    db.close()
    return jsonify({'movimentos':[dict(r) for r in rows],
                    'entradas':round(entradas,2),'saidas':round(saidas,2),
                    'saldo':round(entradas-saidas,2),'por_forma':formas})

@app.route('/api/caixa', methods=['POST'])
def add_caixa():
    d = request.json
    db = get_db()
    db.execute('INSERT INTO caixa (tipo,descricao,valor,forma_pagamento,referencia) VALUES (?,?,?,?,?)',
               (d['tipo'],d.get('descricao',''),d.get('valor',0),
                d.get('forma_pagamento','Dinheiro'),d.get('referencia','')))
    db.commit(); db.close()
    return jsonify({'ok':True})

@app.route('/api/caixa/abertura', methods=['POST'])
def abrir_caixa():
    d = request.json
    db = get_db()
    hoje = datetime.now().strftime('%Y-%m-%d')
    if db.execute('SELECT id FROM abertura_caixa WHERE data=? AND fechado=0',(hoje,)).fetchone():
        db.close(); return jsonify({'ok':False,'msg':'Caixa já aberto hoje'})
    db.execute('INSERT INTO abertura_caixa (valor_inicial,usuario,data) VALUES (?,?,?)',
               (d.get('valor_inicial',0),d.get('usuario',''),hoje))
    if d.get('valor_inicial',0)>0:
        db.execute('INSERT INTO caixa (tipo,descricao,valor,forma_pagamento,referencia) VALUES (?,?,?,?,?)',
                   ('entrada','Abertura de caixa',d['valor_inicial'],'Dinheiro','abertura'))
    db.commit(); db.close()
    return jsonify({'ok':True})

# ── DASHBOARD ─────────────────────────────────────
@app.route('/api/dashboard')
def dashboard():
    db = get_db()
    os_ab  = db.execute("SELECT COUNT(*) as c FROM ordens_servico WHERE status NOT IN ('Entregue')").fetchone()['c']
    clientes = db.execute("SELECT COUNT(*) as c FROM pessoas WHERE tipo='Cliente'").fetchone()['c']
    est_baixo = db.execute('SELECT COUNT(*) as c FROM produtos WHERE estoque_atual<=estoque_minimo AND ativo=1').fetchone()['c']
    vd_hoje = db.execute("SELECT COALESCE(SUM(total),0) as t FROM vendas WHERE DATE(data_emissao)=DATE('now')").fetchone()['t']
    entradas = db.execute("SELECT COALESCE(SUM(valor),0) as t FROM caixa WHERE tipo='entrada' AND DATE(criado_em)=DATE('now')").fetchone()['t']
    saidas   = db.execute("SELECT COALESCE(SUM(valor),0) as t FROM caixa WHERE tipo='saida' AND DATE(criado_em)=DATE('now')").fetchone()['t']
    os_rec = db.execute('''SELECT os.*,p.nome as cliente_nome FROM ordens_servico os
                           LEFT JOIN pessoas p ON os.cliente_id=p.id
                           ORDER BY os.id DESC LIMIT 8''').fetchall()
    db.close()
    return jsonify({'os_abertas':os_ab,'clientes':clientes,'estoque_baixo':est_baixo,
                    'vendas_hoje':round(float(vd_hoje),2),
                    'entradas':round(float(entradas),2),'saidas':round(float(saidas),2),
                    'saldo':round(float(entradas-saidas),2),
                    'os_recentes':[dict(r) for r in os_rec]})

# ── IP ────────────────────────────────────────────
@app.route('/api/ip')
def get_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80))
        ip=s.getsockname()[0]; s.close()
    except: ip='127.0.0.1'
    return jsonify({'ip':ip,'url':f'http://{ip}:5000'})

if __name__ == '__main__':
    init_db()
    print('\n'+'='*50)
    print('  i-flash Sistema v3')
    print('='*50)
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(('8.8.8.8',80))
        ip=s.getsockname()[0]; s.close()
    except: ip='127.0.0.1'
    print(f'  PC:      http://localhost:5000')
    print(f'  Celular: http://{ip}:5000')
    print('='*50+'\n')
    app.run(host='0.0.0.0',port=5000,debug=False)

# ── INICIALIZAÇÃO RAILWAY ─────────────────────────
# Roda init_db ao iniciar pelo gunicorn também
init_db()
