from assispy import database,app,login_manager
from flask_login import UserMixin

@login_manager.user_loader
def carregar_estudante(id_estudante):
    return Estudante.query.get(int(id_estudante))

class Estudante(database.Model,UserMixin):

    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    foto_perfil=database.Column(database.String, default='default.jpg')
    listatarefas = database.relationship('Tarefa',backref='autor',lazy=True)
    listacartoes = database.relationship('Cartao', backref='autor', lazy=True)
    listarevisoes = database.relationship('Revisao', backref='autor', lazy=True)

# class Pomodoro(database.Model):
#     id = database.Column(database.Integer, primary_key=True)
#     tempo_pomodoro = database.Column(database.Integer,nullable=False)
#     pausa_curta = database.Column(database.Integer,nullable=False)
#     pausa_longa = database.Column(database.Integer,nullable=False)
#     repeticao = database.Column(database.Integer,nullable=False)
#     ativo=database.Column(database.Boolean,default=0)
#     resetado =database.Column(database.Boolean,default=0)
#     id_estudante = database.Column(database.Integer, database.ForeignKey('estudante.id'), nullable=False)
class Tarefa(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    nome = database.Column(database.String, nullable=False)
    concluida = database.Column(database.Boolean,nullable=False)
    prioridade = database.Column(database.String,nullable=False)
    id_estudante = database.Column(database.Integer, database.ForeignKey('estudante.id'), nullable=False)
    id_pomodoro = database.Column(database.Integer, database.ForeignKey('tarefa.id'))



class Cartao(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    frente = database.Column(database.String,nullable=False)
    verso = database.Column(database.String,nullable=False)
    id_estudante = database.Column(database.Integer, database.ForeignKey('estudante.id'), nullable=False)
    listarevisoes = database.relationship('Revisao', backref='cartao', lazy=True)



class Revisao (database.Model):
    id=database.Column(database.Integer, primary_key=True)
    id_estudante = database.Column(database.Integer, database.ForeignKey('estudante.id'), nullable=False)
    id_cartao = database.Column(database.Integer, database.ForeignKey('cartao.id'), nullable=False)
    nao_lembrou = database.Column(database.Boolean,default=True)
    acertou = database.Column(database.Boolean,default=False)
    data_revisao = database.Column(database.DateTime)
    qtde_dia_proxima_revisao = database.Column(database.Integer)
    data_proxima_revisao = database.Column(database.DateTime)






#Para resetar e ou criar banco de dados
# with app.app_context():
#     database.drop_all()
#     database.create_all()









