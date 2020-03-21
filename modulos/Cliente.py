class Cliente:
    def __init__(self, conn):
        self.conn = conn

    """Este metodo se encarga de crear un nuevo cliente en la BD
        
        Arguments:
            id_cliente {Integer} -- la cedula o nit de la entidad o persona
            id_tipo_doc {char(50)} -- el tipo de documento (cedula, cedula extranjera, nit , etc)
            nombre {char(50)} -- el nombre de la persona o entidad
            apellido {char(50)} -- el apellido de la persona o entidad
            correo {char(100)} -- el correo de la persona o entidad 
            direcciones {array[direccion]} -- la lista de direcciones de la persona o entidad
            telefonos {array[direccion]} -- la lista de telefonos de la persona o entidad
        
        Returns:
            JSON -- retorna un JSON indicando el resultado de la operacion
        """

    def crear_clientes(self, id_cliente, id_tipo_doc, nombre, apellido, correo, direcciones, telefonos):
        try:
            if self.existe_cliente(id_cliente):
                return {"message": "El cliente ya está registrado", "status": "0"}
            with self.conn.cursor() as cursor:
                consulta = "INSERT INTO cliente (id_cliente, id_tipo_doc, nombre, apellido, correo, activo) VALUES(%s,%s,%s,%s,%s,true)"
                cursor.execute(
                    consulta, (id_cliente, id_tipo_doc, nombre, apellido, correo))
                self.conn.commit()
                cursor.close()
                self.insert_direccion(id_cliente, direcciones)
                self.insert_telefono(id_cliente, telefonos)
                return {"message": "Registro Realizado", "status": 200}
        except Exception as e:
            return {"message": "Error "+str(e), "status": 500}
    

    """Este metodo se encarga de editar un cliente en la BD
        
        Arguments:
            id_cliente {Integer} -- la cedula o nit de la entidad o persona
            id_client_aux {Integer} -- la cedula o nit de la entidad o persona
            id_tipo_doc {char(50)} -- el tipo de documento (cedula, cedula extranjera, nit , etc)
            nombre {char(50)} -- el nombre de la persona o entidad
            apellido {char(50)} -- el apellido de la persona o entidad
            correo {char(100)} -- el correo de la persona o entidad 
            activo {boolean} -- true o false
            direcciones {array[direccion]} -- la lista de direcciones de la persona o entidad
            telefonos {array[direccion]} -- la lista de telefonos de la persona o entidad
        
        Returns:
            JSON -- retorna un JSON indicando el resultado de la operacion
        """

    def editar_clientes(self, id_cliente, id_tipo_doc, nombre, apellido, correo, activo, id_client_aux, direcciones, telefonos):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE cliente  SET id_cliente = %s, id_tipo_doc = %s, nombre = %s , apellido = %s, correo = %s, activo = %s WHERE id_cliente = %s"
                cursor.execute(consulta, (id_cliente, id_tipo_doc, nombre, apellido, correo, activo, id_client_aux))
                self.conn.commit()
                cursor.close()
                self.delete_telefono(id_cliente)
                self.delete_direccion(id_cliente)
                self.insert_direccion(id_cliente, direcciones)
                self.insert_telefono(id_cliente, telefonos)
                return {"message": "Registro Realizado", "status": 200}
        except Exception as e:
            return {"message": "Error "+str(e), "status": 500}
    

    """Este metodo se encarga de verificar que un cliente exista en la base de datos
        
        Arguments:
            id_cliente {Integer} -- el numero de documento del cliente o entidad
        
        Returns:
            boolean -- true o false de acuerdo si el cliente esta o no
        """
    def existe_cliente(self, id_cliente):

        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT COUNT(*) as cantidad FROM cliente WHERE id_cliente = %s"
                cursor.execute(consulta, (id_cliente,))
                rows = cursor.fetchall()
                esta = False
                for row in rows:
                    if row[0] > 0:
                        esta = True
                cursor.close()
                return esta
        except Exception as e:
            print(str(e))
            return False

    """Este metodo se encarga de desactivar unos o varios telefono asociada a un cliente
        
        Arguments:
            id_cliente {Integer} -- el numero de documento del cliente o entidad
            telefonos {array[telefono]} -- una lista de telefonos a desactivar
        Returns:
            boolean -- true o false de acuerdo si el cliente esta o no
    """
    def delete_telefono(self, id_cliente):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE telefono SET activo = false WHERE id_cliente = %s"
                cursor.execute(consulta, (id_cliente,))
                self.conn.commit()
                cursor.close()
                return True
        except Exception as e:
            print(str(e))
            return False
    
    """Este metodo se encarga de desactivar una o varias direcciones asociada a un cliente
        
        Arguments:
            id_cliente {Integer} -- el numero de documento del cliente o entidad
            direcciones {array[direccion]} -- una lista de direcciones a desactivar
        Returns:
            boolean -- true o false de acuerdo si el cliente esta o no
    """
    def delete_direccion(self, id_cliente):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE direccion SET activo = false WHERE id_cliente = %s"
                cursor.execute(consulta, (id_cliente,))
                self.conn.commit()
                cursor.close()
                return True
        except Exception as e:
            print(str(e))
            return False
    
    """Este metodo se encarga de insertar unos o varios telefono asociada a un cliente
        
        Arguments:
            id_cliente {Integer} -- el numero de documento del cliente o entidad
            telefono {array[telefono]} -- una lista de telefonos a insertar
        Returns:
            boolean -- true o false de acuerdo si el cliente esta o no
    """
    def insert_telefono(self, id_cliente, telefonos):

        try:
            with self.conn.cursor() as cursor:
                for telefono in telefonos:
                    consulta = "INSERT INTO telefono (id_cliente, id_pais, id_ciudad, telefono, activo) VALUES(%s,%s,%s,%s,true)"
                    cursor.execute(
                        consulta, (id_cliente, telefono["id_pais"], telefono["id_ciudad"], telefono["telefono"]))
                    self.conn.commit()
                cursor.close()
                return True
        except Exception as e:
            print(str(e))
            return False

    """Este metodo se encarga de insertar una o varias direcciones asociada a un cliente
        
        Arguments:
            id_cliente {Integer} -- el numero de documento del cliente o entidad
            direcciones {array[direccion]} -- una lista de direcciones a insertar
        Returns:
            boolean -- true o false de acuerdo si el cliente esta o no
    """

    def insert_direccion(self, id_cliente, direcciones):

        try:
            with self.conn.cursor() as cursor:
                for direccion in direcciones:
                    consulta = "INSERT INTO direccion (id_cliente, id_pais, id_ciudad, direccion, activo) VALUES(%s,%s,%s,%s,true)"
                    cursor.execute(
                        consulta, (id_cliente, direccion["id_pais"], direccion["id_ciudad"], direccion["direccion"]))
                    self.conn.commit()
                cursor.close()
                return True
        except Exception as e:
            print(str(e))
            return False
    """Este metodo se encarga de buscar a los clientes de acuerdo al nombre
        
        Arguments:
            nombre {Integer} -- el nombre de la persona
            apellido {Integer} -- el apellido de la persona
        Returns:
            JSON -- una lista de clientes que estan activosy coinciden con el nombre y el apellido
    """
    def buscar_cliente(self, nombre, apellido):
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT * FROM cliente WHERE nombre like UPPER(%s) AND apellido like UPPER(%s) AND activo = true"
                name_pattern = '%{}%'.format(nombre)
                apellido_pattern = '%{}%'.format(apellido)
                cursor.execute(consulta, (name_pattern,apellido_pattern))
                rows = cursor.fetchall()
                clientes = []
                for row in rows:
                    clientes.append({"id_cliente": row[0], "id_tipo_doc": row[1], "nombre": row[2], "apellido": row[3], "correo": row[4], "activo": row[5]})
                cursor.close()
                return clientes
        except Exception as e:
            print(str(e))
            return []

    """Este metodo se encarga de buscar a los clientes de acuerdo al nombre
        
        Arguments:
            nombre {Integer} -- el nombre de la persona
            apellido {Integer} -- el apellido de la persona
        Returns:
            JSON -- una lista de clientes que coinciden con el nombre y el apellido
    """
    def buscar_cliente_edit(self, nombre, apellido):
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT * FROM cliente WHERE nombre like UPPER(%s) AND apellido like UPPER(%s)"
                name_pattern = '%{}%'.format(nombre)
                apellido_pattern = '%{}%'.format(apellido)
                cursor.execute(consulta, (name_pattern,apellido_pattern))
                rows = cursor.fetchall()
                clientes = []
                for row in rows:
                    clientes.append({"id_cliente": row[0], "id_tipo_doc": row[1], "nombre": row[2], "apellido": row[3], "correo": row[4], "activo": row[5]})
                cursor.close()
                return clientes
        except Exception as e:
            print(str(e))
            return []