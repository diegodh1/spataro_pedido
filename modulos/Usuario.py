class Usuario:
    def __init__(self, conn):
        self.conn = conn

    """Este metodo se encarga de crear un nuevo usuario en la BD
        
        Arguments:
            id_usuario {Integer} -- la cedula o nit de la entidad o persona
            id_tipo_doc {char(50)} -- el tipo de documento (cedula, cedula extranjera, nit , etc)
            nombre {char(50)} -- el nombre de la persona o entidad
            apellido {char(50)} -- el apellido de la persona o entidad
            correo {char(100)} -- el correo de la persona o entidad
            passwrd {char(50)} -- la contrasenha del usuario
            menus {array[menu]} -- la lista de permisos o menus que puede ver el usuario
        
        Returns:
            JSON -- retorna un JSON indicando el resultado de la operacion
        """

    def crear_usuarios(self, id_usuario, id_tipo_doc, nombre, apellido, correo, passwrd, menus):
        try:
            if self.existe_usuario(id_usuario):
                return {"message": "El usuario ya está registrado", "status": "0"}
            with self.conn.cursor() as cursor:
                consulta = "INSERT INTO usuario (id_usuario, id_tipo_doc, nombre, apellido, correo, passwrd, activo) VALUES(%s,%s,%s,%s,%s,%s,true)"
                cursor.execute(
                    consulta, (id_usuario, id_tipo_doc, nombre, apellido, correo, passwrd))
                self.conn.commit()
                cursor.close()
                self.insert_menu(id_usuario,menus)
                return {"message": "Registro Realizado", "status": "1"}
        except Exception as e:
            return {"message": "Error"+str(e), "status": "2"}
    

    """Este metodo se encarga de editar un usuario en la BD
        
        Arguments:
            id_usuario {Integer} -- la cedula o nit de la entidad o persona
            id_usuario_aux {Integer} -- la cedula o nit de la entidad o persona
            id_tipo_doc {char(50)} -- el tipo de documento (cedula, cedula extranjera, nit , etc)
            nombre {char(50)} -- el nombre de la persona o entidad
            apellido {char(50)} -- el apellido de la persona o entidad
            correo {char(100)} -- el correo de la persona o entidad 
            activo {boolean} -- true o false
            passwrd {char(50)} -- la contrasenha del usuario
            menus {array[direccion]} -- la lista de permisos o menus que puede ver el usuario
        
        Returns:
            JSON -- retorna un JSON indicando el resultado de la operacion
        """

    def editar_usuario(self, id_usuario, id_tipo_doc, nombre, apellido, correo, passwrd, activo, id_usuario_aux, menus):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE usuario  SET id_usuario = %s, id_tipo_doc = %s, nombre = %s , apellido = %s, correo = %s, passwrd = %s, activo = %s WHERE id_usuario = %s"
                cursor.execute(consulta, (id_usuario, id_tipo_doc, nombre, apellido, correo, passwrd, activo, id_usuario_aux))
                self.conn.commit()
                cursor.close()
                self.delete_menu(id_usuario)
                self.insert_menu(id_usuario, menus)
                return {"message": "Registro Realizado", "status": "1"}
        except Exception as e:
            return {"message": "Error"+str(e), "status": "2"}
    

    """Este metodo se encarga de verificar que un usuario exista en la base de datos
        
        Arguments:
            id_usuario {Integer} -- el numero de documento del cliente o entidad
        
        Returns:
            boolean -- true o false de acuerdo si el cliente esta o no
        """
    def existe_usuario(self, id_usuario):

        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT COUNT(*) as cantidad FROM usuario WHERE id_usuario = %s"
                cursor.execute(consulta, (id_usuario,))
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
            id_usuario {Integer} -- el numero de documento del cliente o entidad
        Returns:
            boolean -- true o false de acuerdo si se desactivaron los menus(permisos) o no
    """
    def delete_menu(self, id_usuario):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE usuario_menu SET activo = false WHERE id_usuario = %s"
                cursor.execute(consulta, (id_usuario,))
                self.conn.commit()
                cursor.close()
                return True
        except Exception as e:
            print(str(e))
            return False
    
    
    """Este metodo se encarga de insertar unos o varios telefono asociada a un cliente
        
        Arguments:
            id_cliente {Integer} -- el numero de documento del cliente o entidad
            telefono {array[menu]} -- una lista de menus o permisos a insertar
        Returns:
            boolean -- true o false de acuerdo si se insertaron o no los permisos
    """
    def insert_menu(self, id_usuario, menus):

        try:
            with self.conn.cursor() as cursor:
                for menu in menus:
                    consulta = "INSERT INTO usuario_menu (id_usuario, id_menu, activo) VALUES(%s,%s,true)"
                    cursor.execute(consulta, (id_usuario, menu["id_menu"]))
                    self.conn.commit()
                cursor.close()
                return True
        except Exception as e:
            print(str(e))
            return False