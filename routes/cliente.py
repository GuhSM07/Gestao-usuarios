from flask import Blueprint, render_template, request, abort
from database.models.cliente import Cliente

cliente_route = Blueprint('cliente', __name__)


def get_cliente_or_404(cliente_id):
    cliente = Cliente.get_or_none(Cliente.id == cliente_id)
    if cliente is None:
        abort(404)
    return cliente
 

@cliente_route.route('/')
def listar_cliente():

    clientes = Cliente.select()
    return render_template('listar_cliente.html', clientes=clientes)
    # '''Listar os clientes'''


@cliente_route.route('/', methods=['POST'])
def inserir_cliente():

    data = request.get_json(silent=True) or request.form

    novo_usuario = Cliente.create(
        nome=data['nome'],
        email=data['email']
    )

    return render_template('item_cliente.html', cliente=novo_usuario)


@cliente_route.route('/new')
def form_cliente():
    # '''Formularo para cadastrar um cliente'''
    return render_template('form_cliente.html')
    

@cliente_route.route('/<int:cliente_id>')
def detalhes_cliente(cliente_id):
    cliente = Cliente.get_by_id(cliente_id)
    return render_template('detalhe_cliente.html', cliente=cliente)


@cliente_route.route('/<int:cliente_id>/edit')
def editar_cliente(cliente_id):
    cliente = Cliente.get_by_id(cliente_id)
    return render_template('form_cliente.html', cliente=cliente)


@cliente_route.route('/<int:cliente_id>/update', methods=['PUT'])
def atualizar_cliente(cliente_id):
    cliente_editado = Cliente.get_by_id(cliente_id)
    data = request.get_json(silent=True) or request.form

    cliente_editado.nome = data['nome']
    cliente_editado.email = data['email']
    cliente_editado.save()

    return render_template('item_cliente.html', cliente=cliente_editado)


@cliente_route.route('/<int:cliente_id>/deletar', methods=['DELETE'])
def deletar_cliente(cliente_id):
    cliente = Cliente.get_by_id(cliente_id)
    cliente.delete_instance()
    return {'deleted': 'ok'}
