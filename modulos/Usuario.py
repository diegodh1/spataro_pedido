import hashlib
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

    def crear_usuario(self, id_usuario, id_tipo_doc, nombre, apellido, correo, passwrd,foto, menus):

        contraseha = hashlib.new("sha1", passwrd.encode('utf-8'))
        try:
            if self.existe_usuario(id_usuario):
                return {"message": "El usuario ya está registrado", "status": "0"}
            with self.conn.cursor() as cursor:
                consulta = "INSERT INTO usuario (id_usuario, id_tipo_doc, nombre, apellido, correo, passwrd, activo, foto) VALUES(%s,%s,%s,%s,%s,%s,true,%s)"
                cursor.execute(consulta, (id_usuario, id_tipo_doc, nombre, apellido, correo, str(contraseha.digest()),foto))
                self.conn.commit()
                cursor.close()
                self.insert_menu(id_usuario, menus, "true")
                return {"message": "Registro Realizado", "status": 200}
        except Exception as e:
            self.anular_transaccion()
            return {"message": "Error "+str(e), "status": 500}
    

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

    def editar_usuario(self, id_usuario, id_tipo_doc, nombre, apellido, correo, activo, id_usuario_aux,foto, menus):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE usuario  SET id_usuario = %s, id_tipo_doc = %s, nombre = %s , apellido = %s, correo = %s, activo = %s, foto=%s WHERE id_usuario = %s"
                cursor.execute(consulta, (id_usuario, id_tipo_doc, nombre, apellido, correo, activo, foto, id_usuario_aux))
                self.conn.commit()
                cursor.close()
                self.delete_menu(id_usuario)
                self.insert_menu(id_usuario, menus, activo)
                return {"message": "Registro Realizado", "status": 200}
        except Exception as e:
            return {"message": "Error "+str(e), "status": 500}
    

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

    """Este metodo se encarga de buscar un usuario en la base de datos
        
        Arguments:
            id_usuario {Integer} -- el numero de documento del cliente o entidad
        
        Returns:
            un objecto con la información del usuario
        """
    def search_usuario(self, id_usuario):
        menus = self.menu_usuario(id_usuario)
        usuario = {"id_usuario": "", "id_tipo_doc": "", "nombre": "", "apellido": "", "correo": "", "activo": 0, "menus":menus, "foto":""}
        
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT * FROM usuario WHERE id_usuario = %s"
                cursor.execute(consulta, (id_usuario,))
                rows = cursor.fetchall()
                for row in rows:
                    usuario = {"id_usuario": row[0], "id_tipo_doc": row[1], "nombre": row[2], "apellido": row[3], "correo": row[4], "activo": row[6],"foto":row[7], "menus": menus}
                cursor.close()
                return {"status": 200, "usuario": usuario}
        except Exception as e:
            print(str(e))
            self.anular_transaccion()
            return  {"status": 500, "usuario": usuario}

    """este metodo me permite anular la ultima transaccion realizada en la base de datos
        
        Returns:
            retorna un true o false indicando el resultado de la operacion
    """  
    def anular_transaccion(self):
          
        try:
            with self.conn.cursor() as cursor:
                consulta = "ROLLBACK"
                cursor.execute(consulta)
                self.conn.commit()
                cursor.close()
                return True
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
    def insert_menu(self, id_usuario, menus, activo):

        try:
            with self.conn.cursor() as cursor:
                for menu in menus:
                    consulta = "INSERT INTO usuario_menu (activo, id_usuario, id_menu) VALUES(%s,%s,%s)"
                    esta = self.existe_menu(id_usuario, menu["id_menu"]) 
                    if esta == True:
                        consulta = "UPDATE usuario_menu SET activo = %s WHERE id_usuario = %s AND id_menu = %s"
                    print(esta)
                    cursor.execute(consulta, (activo, id_usuario, menu["id_menu"]))
                    self.conn.commit()
                cursor.close()
                return True
        except Exception as e:
            print(str(e))
            return False

    """Este metodo se encarga de comprobar si existe o no un permiso para el usuario
        
        Arguments:
            id_cliente {Integer} -- el numero de documento del cliente o entidad
            telefono {array[menu]} -- el id del permiso
        Returns:
            boolean -- true o false de acuerdo si esta o no
    """
    def existe_menu(self, id_usuario, id_menu):

        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT COUNT(*) as cantidad FROM usuario_menu WHERE id_usuario = %s AND id_menu = %s"
                cursor.execute(consulta, (id_usuario,id_menu))
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
    
    """metodo que se encarga de iniciar sesion de usuario
        
        Arguments:
            id_usuario {bigint} el id del usuario
            passwrd {char(100)} la password del usuario
        
        Returns:
            retorna un json el cual es la informacion de usuario que ingreso
    """  
    def iniciar_sesion(self, id_usuario,passwrd):
        menus = self.menu_usuario(id_usuario)
        usuario = {"id_usuario": "", "id_tipo_doc": "", "nombre": "", "apellido": "", "correo": "", "activo": 0, "menus":menus, "foto":""}
        
        try:
            contraseha = hashlib.new("sha1", passwrd.encode('utf-8'))
            with self.conn.cursor() as cursor:
                consulta = "SELECT * FROM usuario WHERE id_usuario = %s AND passwrd = %s AND activo = true"
                cursor.execute(consulta, (id_usuario,str(contraseha.digest())))
                rows = cursor.fetchall()
                for row in rows:
                    usuario = {"id_usuario": row[0], "id_tipo_doc": row[1], "nombre": row[2], "apellido": row[3], "correo": row[4], "activo": row[6],"foto":row[7], "menus": menus}
                cursor.close()
                return {"status": 200, "usuario": usuario}
        except Exception as e:
            print(str(e))
            self.anular_transaccion()
            return  {"status": 500, "usuario": usuario}

    """metodo que me da los permisos o menus relacionados a un usuario
        
        Arguments:
            id_usuario {bigint} -- el id del usuario
        
        Returns:
            una lista de strings que indican el menu correspondiente al usuario
     """
    def menu_usuario(self, id_usuario):  
        menus = []
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT id_menu FROM usuario_menu WHERE id_usuario = %s  AND activo = true"
                cursor.execute(consulta, (id_usuario,))
                rows = cursor.fetchall()
                for row in rows:
                    menus.append(row[0])
                cursor.close()
                return menus
        except Exception as e:
            print(str(e))
            return  menus

    """metodo que me da los permisos o menus activos en el sistema
        
        Arguments:
        
        Returns:
            una lista de strings que indican el nombre de cada menu
     """
    def get_menus(self):  
        menus = []
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT id_menu FROM menu WHERE activo = true"
                cursor.execute(consulta)
                rows = cursor.fetchall()
                for row in rows:
                    menus.append({"id_menu":row[0], "activo":0})
                cursor.close()
                return menus
        except Exception as e:
            print(str(e))
            return  menus

    """este metodo te permite cambiar la password de un usuario
        
        Arguments:
            id_usuario {bigint} el id del usuario
            passwrd {char(100)} la password del usuario
        
        Returns:
            retorna un json el cual contiene un mensaje indicando el resultado de la operacion
        """    
    def reset_password(self, id_usuario, passwrd):
            
        try:
            contraseha = hashlib.new("sha1", passwrd.encode('utf-8'))
            with self.conn.cursor() as cursor:
                consulta = "UPDATE usuario SET passwrd = %s WHERE id_usuario = %s AND activo = true"
                cursor.execute(consulta, (str(contraseha.digest()), id_usuario))
                self.conn.commit()
                cursor.close()
                return  {"status": 200, "mensaje": "Cambio Realizado"}
        except Exception as e:
            return {"status": 500, "mensaje": "No se pudo cambiar el password: "+str(e)}