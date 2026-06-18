import sqlite3, os
from datetime import datetime

DATABASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'iflash.db')

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
