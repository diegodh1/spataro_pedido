import io
import pandas as pd
import base64

class Referencia:
    def __init__(self, conn):
        self.conn = conn

    """este metodo se encarga de guardar una referencia en la base de datos
        
    Arguments:
        base64_excel {text} -- es un archivo de excel en base 64
        tipo {char(10)} -- si quiere guardar la referencia en unidades o metros
        
    Returns:
        retorna una operacion auxiliar el cual dependiendo del tipo dara un json
    """
    def guardar_referencia(self, excel, tipo):
        excel = base64.b64decode(excel)
        if tipo == "UND":
            return self.guardar_referencia_u(excel)
        else:
            return self.guardar_referencia_m(excel)

    """este metodo se encarga de guardar las referencias en metros
        
    Arguments:
         base64_excel {text} -- es un archivo de excel en base 64
        
    Returns:
        retorna un json el cual es el resultado de la operacion
    """ 
    def guardar_referencia_m(self, f):
        df = pd.read_excel(f)
        size = df.shape
        rows = size[0]
        try:
            for i in range(rows):
                self.insertar_referenca(df['referencia'][i],df['medida'][i], df['activo'][i])
                self.insertar_color(df['color'][i],df['nombre'][i], df['activo'][i])
                self.insertar_ref_color(df['referencia'][i],df['color'][i],df['activo'][i])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],df['talla'][i],df['unidades'][i],df['precio'][i])
            return {"mensaje": "Registros Realizados", "status": 200}
        except Exception as e:
            self.anular_transaccion()
            return {"mensaje": "No se pudo realizar el registro "+str(e), "status": 500}

    """este metodo se encarga de guardar las referencias en unidades
        
    Arguments:
         base64_excel {text} -- es un archivo de excel en base 64
        
    Returns:
        retorna un json el cual es el resultado de la operacion
    """ 
    def guardar_referencia_u(self, f):
        df = pd.read_excel(f)
        size = df.shape
        rows = size[0]
        try:
            for i in range(rows):
                self.insertar_referenca(df['referencia'][i], df['medida'][i], df['activo'][i])
                self.insertar_color(df['color'][i],df['nombre'][i],df['activo'][i])
                self.insertar_ref_color(df['referencia'][i],df['color'][i],df['activo'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],df['talla'][i],df['unidades'][i],df['precio'][i])
            return {"mensaje": "Registros Realizados", "status": 200}
        except Exception as e:
            self.anular_transaccion()
            return {"mensaje": "No se pudo realizar el registro"+str(e), "status": 500}

    #-----metodos necesarios para crear o editar una referencia-----

    """este metodo se encarga de insertar una referencia en la base de datos
        
    Arguments:
        id_referencia {char(50)} -- el id de la referencia a insertar
        activo {char(10)} -- el estado de la referencia
        
    Returns:
        un json indicando el resultado de la operacion
    """  
    def insertar_referenca(self, id_referencia,id_medida, activo):
        try:
            if self.existe_referencia(id_referencia):
                self.editar_referencia(id_referencia,id_medida, activo)
            else:
                with self.conn.cursor() as cursor:
                    consulta = "INSERT INTO referencia (id_referencia, id_medida, activo) VALUES(%s,%s,%s)"
                    cursor.execute(consulta, (id_referencia, id_medida, activo))
                    self.conn.commit()
                    cursor.close()
            return {"message": "Registro Realizado", "status": "1"}
        except Exception as e:
            self.anular_transaccion()
            return {"message": "Error"+str(e), "status": "2"}

    """este metodo se encarga de comprobar si existe o no una referencia en la base de datos
        
    Arguments:
        id_referencia {char(50)} -- el id de la referencia a buscar
        
    Returns:
        retorna falso o verdadero dependiendo si esta o no
    """
    def existe_referencia(self, id_referencia):    
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT COUNT(*) as cantidad FROM referencia WHERE id_referencia = %s"
                cursor.execute(consulta, (id_referencia,))
                rows = cursor.fetchall()
                esta = False
                for row in rows:
                    if row[0] > 0:
                        esta = True
                cursor.close()
                return esta
        except Exception as e:
            self.anular_transaccion()
            return False

    """este metodo se encarga de editar una referencia en la base de datos 
        
    Arguments:
        id_referencia {char(50)} -- el id de la referencia a editar
        activo {char(10)} -- el estado de la referencia
        
    Returns:
        retorna un json indicando el resultado de la operacion
    """ 
    def editar_referencia(self, id_referencia, id_medida, activo):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE referencia  SET activo = %s, id_medida=%s WHERE id_referencia = %s"
                cursor.execute(consulta, (activo, id_medida, id_referencia))
                self.conn.commit()
                cursor.close()
                return {"message": "Registro Realizado", "status": 200}
        except Exception as e:
            self.anular_transaccion()
            return {"message": "Error"+str(e), "status": 500}


    #-----metodos necesarios para crear o editar un color-----
    """este metodo se encarga de insertar un color a la base de datos
        
    Arguments:
        id_color {char(50)} -- el id del color que queremos insertar
        activo {char(10)} -- el estado del color a insertar
        
    Returns:
        retorna un json indicando el resultado de la operacion
    """  
    def insertar_color(self, id_color,nombre, activo):
        try:
            if self.existe_color(id_color):
                self.editar_color(id_color,nombre, activo)
            else:
                with self.conn.cursor() as cursor:
                    consulta = "INSERT INTO color (id_color,nombre, activo) VALUES(%s,%s,%s)"
                    cursor.execute(consulta, (id_color,nombre,activo))
                    self.conn.commit()
                    cursor.close()

            return {"message": "Registro Realizado", "status": 200}
        except Exception as e:
            self.anular_transaccion()
            return {"message": "Error"+str(e), "status": 500}
    
    """este metodo se encarga de comprobar si existe un color o no en la base de datos
        
    Arguments:
        id_color {char(50)} -- el id del color a buscar
        
    Returns:
        retorna falso o verdadero de acuerdo a si esta o no
    """  
    def existe_color(self, id_color):  
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT COUNT(*) as cantidad FROM color WHERE id_color = %s"
                cursor.execute(consulta, (id_color,))
                rows = cursor.fetchall()
                esta = False
                for row in rows:
                    if row[0] > 0:
                        esta = True
                cursor.close()
                return esta
        except Exception as e:
            self.anular_transaccion()
            return False

    """este metodo se encarga de editar un color en la base de datos
        
    Arguments:
        id_color {char(10)} -- el id del color a editar
        activo {char(10)} -- el estado del color
        
    Returns:
        retorna un json indicando el resultado de la operacion
    """ 
    def editar_color(self, id_color, nombre, activo):   
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE color SET activo = %s, nombre=%s WHERE id_color = %s"
                cursor.execute(consulta, (activo, nombre, id_color))
                self.conn.commit()
                cursor.close()
                return {"message": "Registro Realizado", "status": 200}
        except Exception as e:
            self.anular_transaccion()
            return {"message": "Error"+str(e), "status": 500}

    #-----metodos necesarios para crear o editar un ref_color-----
    """este metodo se encarga de insertar una referencia-color en la base de datos 
        
    Arguments:
        id_referencia {char(50)} -- el id de la referencia a insertar
        id_color {char(50)} -- el id del color a insertar
        activo {char(10)} -- el estado de la referencia-color
        
    Returns:
        retorna un json indicando el resultado de la operacion
    """ 
    def insertar_ref_color(self, id_referencia, id_color, activo):
   
        try:
            if self.existe_ref_color(id_referencia, id_color):
                self.editar_ref_color(id_referencia, id_color, activo)
            else:
                with self.conn.cursor() as cursor:
                    consulta = "INSERT INTO ref_color (id_referencia, id_color, activo) VALUES(%s,%s,%s)"
                    cursor.execute(consulta, (id_referencia, id_color, activo))
                    self.conn.commit()
                    cursor.close()

            return {"message": "Registro Realizado", "status": 200}
        except Exception as e:
            self.anular_transaccion()
            return {"message": "Error"+str(e), "status": 500}
    
    """este metodo se encarga se saber si existe o no una referencia-color
        
    Arguments:
        id_referencia {char(50)} -- el id de la referencia a comprobar
        id_color {char(50)} -- el id del color a comprobar
        
    Returns:
        retorna falso o verdadero dependiendo si esta o no
    """
    def existe_ref_color(self, id_referencia, id_color):        
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT COUNT(*) as cantidad FROM ref_color WHERE id_referencia = %s AND id_color=%s"
                cursor.execute(consulta, (id_referencia,id_color))
                rows = cursor.fetchall()
                esta = False
                for row in rows:
                    if row[0] > 0:
                        esta = True
                cursor.close()
                return esta
        except Exception as e:
            self.anular_transaccion()
            return False

    """este metodo se encarga de editar una referencia en la base de datos
        
    Arguments:
        id_referencia {char(50)} -- el id de la referencia a editar
        id_color {char(50)} -- el id del color a editar
        activo {char(20)} -- el estado del color a editar
        
    Returns:
        un json indicando el resultado de la operacion
    """ 
    def editar_ref_color(self,id_referencia, id_color, activo):   
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE ref_color SET activo = %s WHERE id_referencia=%s AND id_color = %s"
                cursor.execute(consulta, (activo, id_referencia, id_color))
                self.conn.commit()
                cursor.close()
                return {"message": "Registro Realizado", "status": 200}
        except Exception as e:
            self.anular_transaccion()
            return {"message": "Error"+str(e), "status": 500}

    """este metodo se encarga de seleccionar el id de la referencia-color
        
    Arguments:
        id_referencia {char(50)} -- el id de la referencia a editar
        id_color {char(50)} -- el id del color a editar
        
    Returns:
        el id de la referencia-color
    """ 
    def select_ref_color(self,id_referencia, id_color):
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT id_ref_color FROM ref_color WHERE id_referencia = %s AND id_color=%s"
                cursor.execute(consulta, (id_referencia,id_color))
                rows = cursor.fetchall()
                for row in rows:
                    return row[0]
                cursor.close()
                return '-1'
        except Exception as e:
            self.anular_transaccion()
            return '-1'

    #-----metodos necesarios para crear o editar un ref_color_talla-----

    """este metodo se encarga de insertar una referencia-color-talla en la base de datos en unidades
        
    Arguments:
        id_referencia {char(50)} -- el id de la referencia a insertar
        id_color {char(50)} -- el id del color a insertar
        id_talla {int} -- el id de la talla a insertar
        unidades {int} -- las unidades correspondientes
        precio {float} -- el precio de la referencia-color-talla
        
    Returns:
        un json indicando el resultado de la operacion
    """  
    def insertar_ref_color_talla_u(self,id_referencia, id_color, id_talla, unidades, precio):
        try:
            id_ref_color = self.select_ref_color(id_referencia,id_color)
            if self.existe_ref_color_talla(id_ref_color, id_talla):
                self.editar_ref_color_talla_u(id_ref_color, id_talla, unidades, precio)
            else:
                with self.conn.cursor() as cursor:
                    consulta = "INSERT INTO ref_color_talla (id_ref_color, id_talla, unidades, precio, metros) VALUES(%s,%s,%s,%s,0)"
                    unidades = int(str(unidades))
                    precio = float(str(precio))
                    cursor.execute(consulta, (id_ref_color, str(id_talla), unidades, precio))
                    self.conn.commit()
                    cursor.close()
            return {"message": "Registro Realizado", "status": 200}
        except Exception as e:
            self.anular_transaccion()
            return {"message": "Error"+str(e), "status": 500}

    """este metodo se encarga de insertar una referencia-color-talla en la base de datos en metros
        
    Arguments:
        id_referencia {char(50)} -- el id de la referencia a insertar
        id_color {char(50)} -- el id del color a insertar
        id_talla {int} -- el id de la talla a insertar
        metros {int} -- los metros correspondientes
        precio {float} -- el precio de la referencia-color-talla
        
    Returns:
        un json indicando el resultado de la operacion
    """  
    def insertar_ref_color_talla_m(self,id_referencia, id_color, id_talla, metros, precio):
        try:
            id_ref_color = self.select_ref_color(id_referencia,id_color)
            if self.existe_ref_color_talla(id_ref_color, id_talla):
                self.editar_ref_color_talla_m(id_ref_color, id_talla, metros, precio)
            else:
                with self.conn.cursor() as cursor:
                    consulta = "INSERT INTO ref_color_talla (id_ref_color, id_talla, metros, precio, unidades) VALUES(%s,%s,%s,%s,0)"
                    metros = float(str(metros))
                    precio = float(str(precio))                    
                    cursor.execute(consulta, (id_ref_color, str(id_talla), metros, precio))
                    self.conn.commit()
                    cursor.close()

            return {"message": "Registro Realizado", "status": 200}
        except Exception as e:
            self.anular_transaccion()
            return {"message": "Error"+str(e), "status": 500}
    
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
    """se encarga de comprobar si existe o no una referencia-color-talla
        
    Arguments:
        id_ref_color {bigint} -- el id de la referencia-color
        id_talla {int} -- el id de la talla
        
    Returns:
        falso o verdadero de acuerdo al resultado
    """ 
    def existe_ref_color_talla(self, id_ref_color, id_talla):   
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT COUNT(*) as cantidad FROM ref_color_talla WHERE id_ref_color = %s AND id_talla=%s"
                cursor.execute(consulta, (id_ref_color,str(id_talla)))
                rows = cursor.fetchall()
                esta = False
                for row in rows:
                    if row[0] > 0:
                        esta = True
                cursor.close()
                return esta
        except Exception as e:
            self.anular_transaccion()
            return False


    """este metodo se encarga de editar una referencia-color-talla de la base de datos en unidades
        
        Arguments:
            id_ref_color {bigint} -- el id de la referencia-color
            id_talla {int} -- el id de la talla
            unidades {int} -- las unidades
            precio {float} -- el precio
        
        Returns:
            retorna un json indicando el resultado de la operacion
    """
    def editar_ref_color_talla_u(self,id_ref_color, id_talla, unidades, precio):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE ref_color_talla SET unidades = %s, precio=%s  WHERE id_ref_color=%s AND id_talla = %s"
                cursor.execute(consulta, (int(str(unidades)), int(str(precio)), id_ref_color, str(id_talla)))
                self.conn.commit()
                cursor.close()
                return {"message": "Registro Realizado", "status": 200}
        except Exception as e:
            self.anular_transaccion()
            return {"message": "Error"+str(e), "status": 500}

    """este metodo se encarga de editar una referencia-color-talla de la base de datos en metros
        
        Arguments:
            id_ref_color {bigint} -- el id de la referencia-color
            id_talla {int} -- el id de la talla
            metros {int} -- los metros
            precio {float} -- el precio
        
        Returns:
            retorna un json indicando el resultado de la operacion
    """
    def editar_ref_color_talla_m(self,id_ref_color, id_talla, metros, precio):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE ref_color_talla SET metros = %s, precio=%s  WHERE id_ref_color=%s AND id_talla = %s"
                cursor.execute(consulta, (float(str(metros)), float(str(precio)), id_ref_color, str(id_talla)))
                self.conn.commit()
                cursor.close()
                return {"message": "Registro Realizado", "status": 200}
        except Exception as e:
            self.anular_transaccion()
            return {"message": "Error"+str(e), "status": 500}
    
    """este metodo se encarga de buscar una lista de referencia-color que coincida con el input
        
    Arguments:
    id_referencia {char(50)} -- el id de la referencia a buscar
        
    Returns:
        retorna una lista de referencias-color que coinciden con el patron
    """ 
    def buscar_referencia(self, id_referencia):
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT RC.* FROM referencia as R INNER JOIN ref_color AS RC ON RC.id_referencia = R.id_referencia AND RC.activo = 'A' 
                WHERE R.id_referencia like UPPER(%s) and R.activo = 'A' LIMIT 7"""
                ref_pattern = '%{}%'.format(id_referencia)
                cursor.execute(consulta, (ref_pattern,))
                rows = cursor.fetchall()
                sugerencias = []
                for row in rows:
                    sugerencias.append({"id_referencia":row[0], "id_color": row[1], "id_ref_color": row[2]})
                cursor.close()
                return {"status":200, "sugerencias": sugerencias}
        except Exception as e:
            self.anular_transaccion()
            return {"status":500, "sugerencias": []}

    """este metodo se encarga de buscar una lista de referencia-color-talla que coincida con el input
        
    Arguments:
    id_ref_color {bigint} -- el id de la referencia-color a buscar
        
    Returns:
        retorna una lista de referencias-color-talla que coinciden con el patron
    """ 
    def dar_tallas_referencias(self, id_ref_color):
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT * FROM ref_color_talla WHERE id_ref_color = %s"""
                cursor.execute(consulta, (id_ref_color,))
                rows = cursor.fetchall()
                referencia_talla = []
                for row in rows:
                    referencia_talla.append({"id_ref_color":row[0], "id_talla": row[1], "id_consecutivo": row[2], "unidades": row[3], "metros":row[4], "precio": row[5]})
                cursor.close()
                return {"status":200, "referencia_talla": referencia_talla}
        except Exception as e:
            self.anular_transaccion()
            return {"status":500, "referencia_talla": []}

