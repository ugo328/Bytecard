import flask
from flask import Flask, redirect, render_template, request, flash

import forms
import use_cases
from database import db

app = Flask(__name__)

# Configura banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123456@localhost:3306/byte_card'
app.config['SQLALCHEMY_ECHO'] = True
db.init_app(app)

# Configure a chave secreta do Flask
app.secret_key = 'btg'

# Simulando uma estrutura de dados de usuários
usuarios = {
    'ugorventura': {'senha': 'ugodahora'},
    'olemar': {'senha': 'filho'}
}

@app.route('/')
def index():
    return redirect('/cartoes/lista')

def login():
    if request.method == 'POST':
        nickname = request.form['nickname']
        senha = request.form['senha']

        if nickname in usuarios and usuarios[nickname]['senha'] == senha:
            session['logged_in'] = True
            flash('Login bem-sucedido!')
            return redirect(url_for('index'))
        else:
            flash('Credenciais inválidas. Tente novamente.')

    return render_template('login.html')


# Rota para a página de logout
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logout bem-sucedido!')
    return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/cartoes/cadastrar', methods=['POST'])
def cadastra_cartao():
    form = forms.CadastraCartaoForm(request.form)
    if form.validate():
        use_cases.cadastra_cartao(form.cliente.data, form.limite.data)
        flash('Cartão cadastrado com sucesso.', 'info')
        return redirect('/cartoes/lista')
    return formulario_cartao(form)


@app.route('/cartoes/<id>/cancelar')
def cancela_cartao(id):
    use_cases.cancela_cartao(id)
    return redirect('/cartoes/lista')


@app.route('/cartoes/<id>/ativar')
def ativa_cartao(id):
    cartao_id = int(id)
    use_cases.ativa_cartao(cartao_id)

    return redirect('/cartoes/lista')


@app.route('/cartoes/<id>/limite')
def formulario_limite(id, form=None):
    cartao = use_cases.pesquisa_cartao_por_id(id)
    return render_template('cartao/limite.html', cartao=cartao, form=form)


@app.route('/cartoes/alterar-limite', methods=['POST'])
def altera_limite():
    form = forms.AlteraLimiteForm(request.form)
    if form.validate():
        use_cases.define_limite(form.id.data, form.limite.data)
        flash('Limite alterado com sucesso.', 'info')

        return redirect('/cartoes/lista')

    return formulario_limite(form.id.data, form=form)


@app.route('/compras/formulario')
def formulario_compra(form=None):
    cartoes = use_cases.lista_cartoes()

    return render_template('compra/formulario.html', cartoes=cartoes, form=form)


@app.route('/compras/cadastrar', methods=['POST'])
def cadastra_compra():
    form = forms.CadastraCompraForm(request.form)
    if form.validate():
        use_cases.cadastra_compra(
            form.cartao.data,
            form.valor.data,
            form.categoria.data,
            form.estabelecimento.data
        )

        flash('Compra cadastrada com sucesso.', 'info')
        return redirect('/compras/cadastrar')

    return formulario_compra(form)


if __name__ == '__main__':
    app.run(debug=True)