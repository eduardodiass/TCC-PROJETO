from flask import render_template,flash, url_for,request,redirect
from assispy import app,database,bcrypt
from assispy.forms import FormLogin,FormCriarConta,FormEditarPerfil,FormCriarCartao
from assispy.models import Estudante,Tarefa,Cartao,Revisao
from flask_login import login_user,logout_user, current_user, login_required
import secrets
import os
from PIL import Image
import openai

openai.api_key = 'CHAVE_SECRETA_DA_API_CHATGPT'
conversa= []
@app.route('/')
@login_required
def principal():
    return render_template('tarefa.html')

@app.route('/login', methods= ['GET','POST'])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()

    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        estudante=Estudante.query.filter_by(email=form_login.email.data).first()
        if estudante and bcrypt.check_password_hash(estudante.senha,form_login.senha.data):
            login_user(estudante, remember=form_login.lembrar_dados.data)
            flash('Login feito com sucesso', 'alert-success')
            parametro_next= request.args.get('next')
            if parametro_next:
                return redirect(parametro_next)
            else:
                return redirect(url_for('principal'))
        else:
            flash('Senha ou email incorretos', 'alert-danger')

    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senha_criptografada= bcrypt.generate_password_hash(form_criarconta.senha.data)
        estudante = Estudante(username=form_criarconta.username.data,email=form_criarconta.email.data,senha=senha_criptografada)
        database.session.add(estudante)
        database.session.commit()
        flash('Cadastro realizado com sucesso','alert-success')
        return redirect(url_for('principal'))

    return render_template('login.html', form_login=form_login,form_criarconta=form_criarconta)

@app.route("/sair")
def sair():
    logout_user()
    flash('Logout realizado com sucesso', 'alert-success')
    return redirect(url_for('principal'))

@app.route("/perfil")
@login_required
def perfil():
    foto_perfil = url_for('static',filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil.html',foto_perfil=foto_perfil)

def salvar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo



@app.route("/perfil/editar",methods=['GET','POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.username=form.username.data
        current_user.email = form.email.data
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        if form.validate_on_submit() and 'botao_submit_editarperfil' in request.form:
            senha_criptografada = bcrypt.generate_password_hash(form.senha.data)
            current_user.senha = senha_criptografada
        database.session.commit()
        flash('Dados atualizados com sucesso','alert-success')
        return redirect(url_for('perfil'))
    elif request.method== 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username
        form.senha.data = current_user.senha

    foto_perfil = url_for('static',filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('editarperfil.html',foto_perfil=foto_perfil,form=form)


@app.route("/listas-tarefas/criar",)
@login_required
def criar_lista_tarefas ():
    return render_template("criar_lista_tarefas.html")


@app.route("/assistente", methods=['GET','POST'])
@login_required
def assistente():

    if request.method == 'GET':
        return render_template('assistente.html')
    if request.form['pergunta']:
        pergunta = 'Eu: ' + request.form['pergunta']

        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=pergunta,
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6
        )

        resposta = 'IA: ' + response.choices[0].text.strip()

        conversa.append(pergunta)
        conversa.append(resposta)

        return render_template('assistente.html', conversa=conversa)
    else:
        return render_template('assistente.html')


@app.route("/tarefa", methods=['GET','POST'])
@login_required
def tarefa():
    tarefa_lista = Tarefa.query.all()
    return render_template("tarefa.html", tarefa_lista=tarefa_lista)
@app.route("/add", methods=["POST"])
@login_required
def add():
    nome = request.form.get("nome")
    prioridade = request.form.get("prioridade")
    nova_tarefa = Tarefa(nome=nome,prioridade=prioridade,concluida=False,autor=current_user)
    database.session.add(nova_tarefa)
    database.session.commit()
    return redirect(url_for("tarefa"))


@app.route("/update/<int:tarefa_id>")
@login_required
def update(tarefa_id):
    tarefa = Tarefa.query.filter_by(id=tarefa_id).first()
    tarefa.concluida = not tarefa.concluida
    database.session.commit()
    return redirect(url_for("tarefa"))


@app.route("/delete/<int:tarefa_id>")
@login_required
def delete(tarefa_id):
    tarefa = Tarefa.query.filter_by(id=tarefa_id).first()
    database.session.delete(tarefa)
    database.session.commit()
    return redirect(url_for("tarefa"))




@app.route('/cartao/criar', methods= ['GET','POST'])
@login_required
def cartao_add():
    form_criarcartao = FormCriarCartao()
    if form_criarcartao.validate_on_submit() and 'botao_submit_criarcartao' in request.form:
       #estudante=Estudante.query.filter_by(email=form_criarcartao.frente.data).first()
        frente = form_criarcartao.frente.data
        verso = form_criarcartao.verso.data
        cartao = Cartao(frente=frente,verso=verso,autor=current_user)
        database.session.add(cartao)
        database.session.commit()
        flash('Cartão cadastrado com sucesso', 'alert-success')

    return render_template('cartoes.html', form_criarcartao=form_criarcartao)

@app.route("/lista", methods=['GET','POST'])
@login_required
def cartao_lista():
    cartao_lista = Cartao.query.all()
    return render_template("listar_cartoes.html", cartao_lista=cartao_lista)


@app.route('/editar/<int:cartao_id>', methods= ['GET','POST'])
@login_required
def editar_cartao(cartao_id):
    form_criarcartao = FormCriarCartao()
    if form_criarcartao.validate_on_submit() and 'botao_submit_criarcartao' in request.form:
        cartao = Cartao.query.filter_by(id=cartao_id).first()
        cartao.frente = form_criarcartao.frente.data
        cartao.verso = form_criarcartao.verso.data
        cartao_editado = Cartao(frente=cartao.frente,verso=cartao.verso,autor=current_user)
        database.session.add(cartao_editado)
        database.session.commit()
        flash('Cartão editado com sucesso', 'alert-success')

    return render_template('cartoes.html', form_criarcartao=form_criarcartao)


@app.route("/delete/<int:cartao_id>")
@login_required
def delete_cartao(cartao_id):
    cartao = Cartao.query.filter_by(id=cartao_id).first()
    database.session.delete(cartao)
    database.session.commit()
    return redirect(url_for("cartao_lista"))

# @app.route("revisao")
# @login_required
#   id=database.Column(database.Integer, primary_key=True)
#     id_estudante = database.Column(database.Integer, database.ForeignKey('estudante.id'), nullable=False)
#     id_cartao = database.Column(database.Integer, database.ForeignKey('cartao.id'), nullable=False)
#     nao_lembrou = database.Column(database.Boolean,default=True)
#     acertou = database.Column(database.Boolean,default=False)
#     data_revisao = database.Column(database.DateTime)
#     qtde_dia_proxima_revisao = database.Column(database.Integer)
#     data_proxima_revisao = database.Column(database.DateTime)

@app.route("/revisao")
@login_required
def revisao():
  return  render_template('revisao.html')

@app.route("/revisar")
@login_required
def revisar():
  return  render_template('revisar.html')