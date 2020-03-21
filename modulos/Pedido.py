import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#LINK:https://realpython.com/python-send-email/

class Pedido:
    def __init__(self, conn):
        self.conn = conn
    """Este metodo se encarga de realizar un nuevo pedido
        Arguments:
            id_cliente {bigint} -- el id del cliente al cual se le va a realizar el pedido
            id_usuario {bigint} -- el id del usuario que realizo el pedido
            fecha {date} -- la fecha que se realizo el pedido
            firma {text} -- la firma es una imagen en base64
            observacion {text} -- la descripcion del pedido
        
        Returns:
            retorna un json que contiene un mensaje del resultado de la operacion
    """    
    def crear_pedido(self, id_cliente, id_usuario,fecha, firma, observacion):
        try:
            with self.conn.cursor() as cursor:
                consulta = "INSERT INTO pedido (id_cliente, id_usuario, fecha, firma, observacion, activo) VALUES(%s,%s,%s,%s,%s,'PENDIENTE')"
                cursor.execute(consulta, (id_cliente, id_usuario, fecha, firma, observacion))
                self.conn.commit()
                cursor.close()
                return {"message": "Registro Realizado", "status": 200}
        except Exception as e:
            return {"message": "Error "+str(e), "status": 500}

    """Este metodo se encarga de agregar un nuevo item al pedido 
        
        Arguments:
            id_pedido {bigint} -- id del pedido al cual vamos a agregar los items
            id_consecutivo {bigint} -- id del item que esta asociado a la tabla ref_color_talla
            unidades {int} -- el numero de unidades del item
            precio {float} -- el precio unitario del item
        
        Returns:
            retorna un json el cual contiene un mensaje indicando el resultado de la operacion
    """  
    def agregar_item_pedido(self, id_pedido, id_consecutivo, unidades, precio):
      
        try:
            valores = self.dar_unidades_disponibles(id_consecutivo)
            und = valores["unidades"]
            mts = valores["metros"]
            mts = mts - (1.5*unidades)
            if und > 0 and und >= unidades:
                with self.conn.cursor() as cursor:
                    consulta = "INSERT INTO ped_referencia (id_pedido, id_consecutivo, unidades, precio) VALUES(%s,%s,%s,%s)"
                    cursor.execute(consulta, (id_pedido, id_consecutivo, unidades, precio))
                    self.conn.commit()
                    cursor.close()
                    und = und - unidades
                    if self.actualizar_unidades(id_consecutivo,und):
                        return {"message": "Registro Realizado", "status": 200}
                    else:
                        self.anular_transaccion()
                        return {"message": "No se pudo actaulizar las unidades", "status": 200}
            elif mts >= 0:
                with self.conn.cursor() as cursor:
                    consulta = "INSERT INTO ped_referencia (id_pedido, id_consecutivo, unidades, precio) VALUES(%s,%s,%s,%s)"
                    cursor.execute(consulta, (id_pedido, id_consecutivo, unidades, precio))
                    self.conn.commit()
                    cursor.close()
                    if self.actualizar_metros(id_consecutivo,mts):
                        return {"message": "Registro Realizado", "status": 200}
                    else:
                        self.anular_transaccion()
                        return {"message": "No se pudo actaulizar las unidades", "status": 200}
            else:
                return  {"message": "No hay unidades disponibles para su solicitud", "status": 200}

        except Exception as e:
            return {"message": "Error "+str(e), "status": 500}

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

    """este metodo me permite actualizar las unidades disponibles de una referencia-talla en la base de datos
        
        Arguments:
            id_consecutivo {bigint} -- id del item que esta asociado a la tabla ref_color_talla
            unidades {int} -- la cantidad actual de unidades
        
        Returns:
            retorna un true o false de acuerdo al resultado de la operacion
     """
    def actualizar_unidades(self, id_consecutivo, unidades):

        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE ref_color_talla SET unidades = %s WHERE id_consecutivo = %s"
                cursor.execute(consulta, (unidades, id_consecutivo))
                self.conn.commit()
                cursor.close()
                return True
        except Exception as e:
            print(str(e))
            return False

    """este metodo me permite actualizar los metros disponibles de una referencia-talla en la base de datos
        
        Arguments:
            id_consecutivo {bigint} -- id del item que esta asociado a la tabla ref_color_talla
            unidades {int} -- la cantidad actual de metros
        
        Returns:
            retorna un true o false de acuerdo al resultado de la operacion
     """
    def actualizar_metros(self, id_consecutivo, metros):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE ref_color_talla SET metros = %s WHERE id_consecutivo = %s"
                cursor.execute(consulta, (metros, id_consecutivo))
                self.conn.commit()
                cursor.close()
                return True
        except Exception as e:
            print(str(e))
            return False   

    """Este metodo me permite dar las unidades y metros disponibles de una referencia-talla
        
        Arguments:
            id_consecutivo {bigint} -- id del item que esta asociado a la tabla ref_color_talla
        
        Returns:
            retorna un json el cual contiene la cantidad de unidades y metros disponibles de la referencia-talla
     """           

    def dar_unidades_disponibles(self, id_consecutivo):
        valores ={"unidades": 0, "metros": 0}
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT unidades, metros FROM ref_color_talla WHERE id_consecutivo = %s"
                cursor.execute(consulta, (id_consecutivo,))
                rows = cursor.fetchall()
                for row in rows:
                    valores ={"unidades": row[0], "metros": row[1]}
                cursor.close()
                return valores
        except Exception as e:
            print(str(e))
            return valores

    """Este metodo me permite eliminar una referencia-talla de un pedido
        
        Arguments:
            id_consecutivo {bigint} -- id del item que esta asociado a la tabla ref_color_talla
            id_pedido {bigint} -- id del pedido
        
        Returns:
            retorna un json el cual contiene un mensaje con el resultado de la operacion
     """ 
    def eliminar_ref_unidades(self, id_pedido, id_consecutivo):
        try:
            with self.conn.cursor() as cursor:
                consulta = "DELETE FROM ped_referencia WHERE id_pedido=%s AND id_consecutivo=%s"
                cursor.execute(consulta, (id_pedido, id_consecutivo))
                self.conn.commit()
                cursor.close()
                return {"message": "Registro Eliminado", "status": 200}
        except Exception as e:
            return {"message": "Error "+str(e), "status": 500}
    
    """Este metodo me permite editar la informacion de un pedido
        
        Arguments:
            id_pedido {bigint} -- el id del pedido
            id_cliente {bigint} -- el id del cliente
            fecha {date} -- fecha de despacho
            firma {text} -- firma del cliente
            observacion {text} -- observacion del pedido
            activo {char(20)} -- estado del pedido
        
        Returns:
            retorna un json indicando el resultado de la operacion
    """ 
    def editar_pedido(self, id_pedido, id_cliente,fecha, firma, observacion, activo):
               
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE pedido SET id_cliente = %s, fecha = %s, firma = %s, observacion = %s, acivo =%s WHERE id_pedido = %s"
                cursor.execute(consulta, (id_cliente, fecha, firma, observacion, activo, id_pedido))
                self.conn.commit()
                cursor.close()
                return {"message": "Cambios Realizados", "status": 200}
        except Exception as e:
            return {"message": "Error "+str(e), "status": 500}

    """este metodo se encarga de dar los items guardados por el usuario
        
    Arguments:
        id_pedido {bigint} -- el id del pedido 
        
    Returns:
        retorna una lista con todos los items guardados del pedido
    """
    def dar_items_guardados(self, id_pedido):        
        items = []
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT RC.id_referencia, RC.id_color, PR.unidades, PR.precio FROM ref_color AS RC INNER JOIN ref_color_talla AS RCT ON RCT.id_ref_color = RC.id_ref_color INNER JOIN 
                ped_referencia AS PR ON PR.id_consecutivo = RCT.id_consecutivo WHERE  PR.id_pedido = %s AND PR.activo = true
                """
                cursor.execute(consulta, (id_pedido,))
                rows = cursor.fetchall()
                for row in rows:
                    items ={"referencia": row[0], "color": row[1], "unidades": row[2], "precio": row[3]}
                cursor.close()
                precio_total = self.sumar_items_guardados(id_pedido)
                unidades_total = self.contar_items_guardados(id_pedido)
                return {"items": items, "precio_total": precio_total, "unidades_total": unidades_total, "status": 200}
        except Exception as e:
            print(str(e))
            return {"items": [], "precio_total": 0, "unidades_total": 0, "status": 500}


    """este metodo se encarga de dar sumar los precios*unidad de los items guardados por el usuario
        
    Arguments:
        id_pedido {bigint} -- el id del pedido 
        
    Returns:
        el valor total del pedido
    """ 
    def sumar_items_guardados(self, id_pedido):
        suma = 0
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT SUM(PR.precio*PR.unidades) FROM ref_color AS RC INNER JOIN ref_color_talla AS RCT ON RCT.id_ref_color = RC.id_ref_color INNER JOIN 
                ped_referencia AS PR ON PR.id_consecutivo = RCT.id_consecutivo WHERE  PR.id_pedido = %s AND PR.activo = true
                """
                cursor.execute(consulta, (id_pedido,))
                rows = cursor.fetchall()
                for row in rows:
                    suma = row[0]
                cursor.close()
                return suma
        except Exception as e:
            print(str(e))
            return suma

    """este metodo se encarga de dar sumar las unidades de los items guardados por el usuario
        
    Arguments:
        id_pedido {bigint} -- el id del pedido 
        
    Returns:
        el valor total de las unidades
    """ 
    def contar_items_guardados(self, id_pedido):
        contar = 0
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT SUM(PR.unidades) FROM ref_color AS RC INNER JOIN ref_color_talla AS RCT ON RCT.id_ref_color = RC.id_ref_color INNER JOIN 
                ped_referencia AS PR ON PR.id_consecutivo = RCT.id_consecutivo WHERE  PR.id_pedido = %s AND PR.activo = true
                """
                cursor.execute(consulta, (id_pedido,))
                rows = cursor.fetchall()
                for row in rows:
                    contar = row[0]
                cursor.close()
                return contar
        except Exception as e:
            print(str(e))
            return contar
