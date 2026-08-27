from flask import Flask
from configuration import configure_all
 
# inicializaçao
app = Flask(__name__)

configure_all(app)

# EXECUÇÃO
app.run(debug=True)



#Coisas da Aula 1 e 2
    
# ROTAS
# @app.route('/') 
# def Pagina_inicial():
#     titulo = "Gestao de Usuarios"
#     usuarios= [
#         {"nome": "Guilherme", "membro_ativo": True},
#         {"nome": "Joao", "membro_ativo": False},
#         {"nome": "Maria", "membro_ativo": False},
#     ]
#     return render_template ('index.html', titulo = titulo, usuarios=usuarios)

# @app.route('/sobre')
# def pagina_sobre(): 
#     return """
#         <b>Programador Guh</b>: vamos faze a base do 
#         <a href="https://rhymarea.netlify.app/batalhas"> RhymÁrea</a>
#         """
