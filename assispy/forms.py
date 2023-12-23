from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField,BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError
from assispy.models import Estudante
from flask_login import current_user


class FormCriarConta(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(8, 20)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email(self,email):
        estudante = Estudante.query.filter_by(email=email.data).first()
        if estudante:
            raise ValidationError('E-mail já cadastrado')


class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(8, 20)])
    lembrar_dados = BooleanField('Lembrar dados de acesso')
    botao_submit_login = SubmitField('Fazer Login')

class FormEditarPerfil(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    foto_perfil = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png','jpeg'])])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(8, 20)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_editarperfil = SubmitField('Atualizar')

    def validate_email(self, email):
        if current_user.email != email.data:
            estudante = Estudante.query.filter_by(email=email.data).first()
            if estudante:
                raise ValidationError('Já existe um usuário com esse e-mail')


class FormCriarCartao(FlaskForm):
    frente = StringField('Frente', validators=[DataRequired()])
    verso = StringField('Verso', validators=[DataRequired()])
    botao_submit_criarcartao = SubmitField('Criar Cartao')