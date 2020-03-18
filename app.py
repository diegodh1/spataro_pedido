from flask import Flask,jsonify,request
from flask_cors import CORS
import conection
import modulos.Cliente as cliente
import modulos.Usuario as usuario

app=Flask(__name__)
CORS(app)


"""funcion encargada de recibir una peticion post en la ruta /crear_cliente

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/crear_cliente',methods=['POST'])
def crear_cliente():
    content=request.get_json()
    id_cliente=content['id_cliente']
    id_tipo_doc=content['id_tipo_doc']
    nombre=content['nombre']
    apellido=content['apellido']
    correo=content['correo']
    direcciones = content['direcciones']
    telefonos = content['telefonos']
    nuevo_cliente = cliente.Cliente(conection.conn)
    return nuevo_cliente.crear_clientes(id_cliente, id_tipo_doc, nombre, apellido, correo, direcciones, telefonos)

"""funcion encargada de recibir una peticion post en la ruta /editar_cliente

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/editar_cliente',methods=['POST'])
def editar_cliente():
    content=request.get_json()
    id_cliente=content['id_cliente']
    id_client_aux=content['id_client_aux']
    id_tipo_doc=content['id_tipo_doc']
    nombre=content['nombre']
    apellido=content['apellido']
    correo=content['correo']
    direcciones = content['direcciones']
    telefonos = content['telefonos']
    activo = content['activo']
    nuevo_cliente = cliente.Cliente(conection.conn)
    return nuevo_cliente.editar_clientes(id_cliente, id_tipo_doc, nombre, apellido, correo, activo, id_client_aux, direcciones, telefonos)

@app.route('/buscar_cliente',methods=['POST'])
def buscar_cliente():
    content=request.get_json()
    nombre=content['nombre']
    apellido=content['apellido']
    nuevo_cliente = cliente.Cliente(conection.conn)
    return jsonify(nuevo_cliente.buscar_cliente(nombre, apellido))

@app.route('/buscar_cliente_edit',methods=['POST'])
def buscar_cliente_edit():
    content=request.get_json()
    nombre=content['nombre']
    apellido=content['apellido']
    nuevo_cliente = cliente.Cliente(conection.conn)
    return jsonify(nuevo_cliente.buscar_cliente_edit(nombre, apellido))

#funciones relacionadas con el usuario

"""funcion encargada de recibir una peticion post en la ruta /crear_usuario

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/crear_usuario',methods=['POST'])
def crear_usuario():
    content=request.get_json()
    id_usuario=content['id_usuario']
    id_tipo_doc=content['id_tipo_doc']
    nombre=content['nombre']
    apellido=content['apellido']
    correo=content['correo']
    passwrd = content['passwrd']
    menus = content['menus']
    nuevo_usuario = usuario.Usuario(conection.conn)
    return nuevo_usuario.crear_usuarios(id_usuario, id_tipo_doc, nombre, apellido, correo, passwrd, menus)

"""funcion encargada de recibir una peticion post en la ruta /editar_usuario

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/editar_usuario',methods=['POST'])
def editar_usuario():
    content=request.get_json()
    id_usuario=content['id_usuario']
    id_usuario_aux=content['id_usuario']
    id_tipo_doc=content['id_tipo_doc']
    nombre=content['nombre']
    apellido=content['apellido']
    correo=content['correo']
    activo=content['activo']
    passwrd = content['passwrd']
    menus = content['menus']
    nuevo_usuario = usuario.Usuario(conection.conn)
    return nuevo_usuario.editar_usuario(id_usuario, id_tipo_doc, nombre, apellido, correo, passwrd, activo, id_usuario_aux, menus)

#inicializamos el servidor el cual escucha en el puerto 4000 y se reinicia cada vez q hayan cambios
if __name__=='__main__':
    app.run(host="0.0.0.0",port=4000,debug=True)