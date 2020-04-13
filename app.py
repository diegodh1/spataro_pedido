from flask import Flask,jsonify,request
from flask_cors import CORS
import conection
import modulos.Cliente as cliente
import modulos.Usuario as usuario
import modulos.Referencia as referencia
import modulos.Pedido as pedido
from werkzeug.utils import secure_filename

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

"""funcion encargada de recibir una peticion post en la ruta /search_cliente

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/search_cliente',methods=['POST'])
def search_cliente():
    content=request.get_json()
    id_cliente=content['id_cliente']
    nuevo_cliente = cliente.Cliente(conection.conn)
    return nuevo_cliente.search_cliente(id_cliente)

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

"""funcion encargada de recibir una peticion post en la ruta /buscar_cliente

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/buscar_cliente',methods=['POST'])
def buscar_cliente():
    content=request.get_json()
    nombre=content['nombre']
    apellido=content['apellido']
    nuevo_cliente = cliente.Cliente(conection.conn)
    return jsonify(nuevo_cliente.buscar_cliente(nombre, apellido))

"""funcion encargada de recibir una peticion post en la ruta /get_documentos

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/get_documentos',methods=['POST'])
def get_documentos():
    nuevo_cliente = cliente.Cliente(conection.conn)
    return jsonify(nuevo_cliente.get_documentos())

"""funcion encargada de recibir una peticion post en la ruta /get_paises

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/get_paises',methods=['POST'])
def get_paises():
    content=request.get_json()
    id_pais=content['id_pais']
    nuevo_cliente = cliente.Cliente(conection.conn)
    return jsonify(nuevo_cliente.get_paises(id_pais))

"""funcion encargada de recibir una peticion post en la ruta /get_ciudades

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/get_ciudades',methods=['POST'])
def get_ciudades():
    content=request.get_json()
    id_ciudad=content['id_ciudad']
    nuevo_cliente = cliente.Cliente(conection.conn)
    return jsonify(nuevo_cliente.get_ciudades(id_ciudad))

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
    foto = content['foto']
    menus = content['menus']
    nuevo_usuario = usuario.Usuario(conection.conn)
    return nuevo_usuario.crear_usuario(id_usuario, id_tipo_doc, nombre, apellido, correo, passwrd,foto, menus)

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
    foto = content['foto']
    menus = content['menus']
    nuevo_usuario = usuario.Usuario(conection.conn)
    return nuevo_usuario.editar_usuario(id_usuario, id_tipo_doc, nombre, apellido, correo, activo, id_usuario_aux, foto, menus)

"""funcion encargada de recibir una peticion post en la ruta /search_usuario

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/search_usuario',methods=['POST'])
def search_usuario():
    content=request.get_json()
    id_usuario=content['id_usuario']
    nuevo_usuario = usuario.Usuario(conection.conn)
    return nuevo_usuario.search_usuario(id_usuario)

"""funcion encargada de recibir una peticion post en la ruta /get_menus

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/get_menus',methods=['POST'])
def get_menus():
    nuevo_usuario = usuario.Usuario(conection.conn)
    return jsonify(nuevo_usuario.get_menus())


"""funcion encargada de recibir una peticion post en la ruta /iniciar_sesion

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/iniciar_sesion',methods=['POST'])
def iniciar_sesion():
    content=request.get_json()
    id_usuario=content['id_usuario']
    passwrd=content['passwrd']
    nuevo_usuario = usuario.Usuario(conection.conn)
    return nuevo_usuario.iniciar_sesion(id_usuario,passwrd)

"""funcion encargada de recibir una peticion post en la ruta /reset_password

Returns:
    un Json indicando el resultado de la operacion
"""

@app.route('/reset_password',methods=['POST'])
def reset_password():
    content=request.get_json()
    id_usuario=content['id_usuario']
    passwrd=content['passwrd']
    nuevo_usuario = usuario.Usuario(conection.conn)
    return nuevo_usuario.reset_password(id_usuario,passwrd)

"""funcion encargada de recibir una peticion post en la ruta /guardar_referencia

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/guardar_referencia',methods=['POST'])
def guardar_referencia():
    content=request.get_json()
    f = content['file']
    tipo = content['tipo']
    ref = referencia.Referencia(conection.conn)
    return ref.guardar_referencia(f,tipo)


"""funcion encargada de recibir una peticion post en la ruta /buscar_referencia

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/buscar_referencia',methods=['POST'])
def buscar_referencia():
    content=request.get_json()
    id_referencia=content['id_referencia']
    ref = referencia.Referencia(conection.conn)
    return ref.buscar_referencia(id_referencia)

"""funcion encargada de recibir una peticion post en la ruta /dar_tallas_referencias

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/dar_tallas_referencias',methods=['POST'])
def dar_tallas_referencias():
    content=request.get_json()
    id_ref_color=content['id_ref_color']
    ref = referencia.Referencia(conection.conn)
    return ref.dar_tallas_referencias(id_ref_color)

"""funcion encargada de recibir una peticion post en la ruta /crear_pedido

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/crear_pedido',methods=['POST'])
def crear_pedido():
    content=request.get_json()
    id_cliente=content['id_cliente']
    id_usuario=content['id_usuario']
    fecha=content['fecha']
    firma=content['firma']
    observacion=content['observacion']
    direccion = content['direccion']
    ped = pedido.Pedido(conection.conn)
    return ped.crear_pedido(id_cliente,id_usuario,fecha,firma,observacion, direccion)

"""funcion encargada de recibir una peticion post en la ruta /search_pedido

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/search_pedido',methods=['POST'])
def search_pedido():
    content=request.get_json()
    id_pedido=content['id_pedido']
    ped = pedido.Pedido(conection.conn)
    return ped.search_pedido(id_pedido)

"""funcion encargada de recibir una peticion post en la ruta /editar_pedido

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/editar_pedido',methods=['POST'])
def editar_pedido():
    content=request.get_json()
    id_pedido=content['id_pedido']
    id_cliente=content['id_cliente']
    fecha=content['fecha']
    firma=content['firma']
    observacion=content['observacion']
    activo=content['activo']
    direccion = content['direccion']
    ped = pedido.Pedido(conection.conn)
    return ped.editar_pedido(id_pedido,id_cliente,fecha,firma,observacion,activo,direccion)

"""funcion encargada de recibir una peticion post en la ruta /search_ref

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/search_ref',methods=['POST'])
def search_ref():
    content=request.get_json()
    id_referencia=content['id_referencia']
    ped = pedido.Pedido(conection.conn)
    return ped.buscar_referencia(id_referencia)

"""funcion encargada de recibir una peticion post en la ruta /search_ref_color

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/search_ref_color',methods=['POST'])
def search_ref_color():
    content=request.get_json()
    id_referencia=content['id_referencia']
    ped = pedido.Pedido(conection.conn)
    return ped.buscar_referencia_color(id_referencia)

"""funcion encargada de recibir una peticion post en la ruta /search_ref_color_talla

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/search_ref_color_talla',methods=['POST'])
def search_ref_color_talla():
    content=request.get_json()
    id_ref_color=content['id_ref_color']
    ped = pedido.Pedido(conection.conn)
    return ped.buscar_referencia_color_talla(id_ref_color)

"""funcion encargada de recibir una peticion post en la ruta /agregar_item_pedido

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/agregar_item_pedido',methods=['POST'])
def agregar_item_pedido():
    content=request.get_json()
    id_pedido=content['id_pedido']
    id_consecutivo=content['id_consecutivo']
    unidades=content['unidades']
    precio=content['precio']
    ped = pedido.Pedido(conection.conn)
    return ped.agregar_item_pedido(id_pedido,id_consecutivo,unidades,precio)

"""funcion encargada de recibir una peticion post en la ruta /eliminar_ref_unidades

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/eliminar_ref_unidades',methods=['POST'])
def eliminar_ref_unidades():
    content=request.get_json()
    id_pedido=content['id_pedido']
    consecutivo=content['consecutivo']
    ped = pedido.Pedido(conection.conn)
    return ped.eliminar_ref_unidades(id_pedido,consecutivo)

"""funcion encargada de recibir una peticion post en la ruta /dar_items_guardados

Returns:
    un Json indicando el resultado de la operacion
"""
@app.route('/dar_items_guardados',methods=['POST'])
def dar_items_guardados():
    content=request.get_json()
    id_pedido=content['id_pedido']
    ped = pedido.Pedido(conection.conn)
    return ped.dar_items_guardados(id_pedido)



#inicializamos el servidor el cual escucha en el puerto 4000 y se reinicia cada vez q hayan cambios
if __name__=='__main__':
    app.run(host="0.0.0.0",port=4000,debug=True)