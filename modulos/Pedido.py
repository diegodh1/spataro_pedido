import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
import email
import email.mime.application
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4, landscape, legal
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak, Spacer, Image
from datetime import date
import base64
import locale
#LINK:https://realpython.com/python-send-email/

class Pedido:
    def __init__(self, conn):
        self.conn = conn

    def enviar_correo(self,id_usuario,id_pedido, correo):
        subject = "Nuevo Pedido Generado"
        body = "El pedido "+str(id_pedido)+" ha sido generado por el usuario "+str(id_usuario)
        sender_email = "spataro.comunicador@gmail.com"
        receiver_email = correo
        password ="Spataro123456"
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message["Bcc"] = receiver_email
        message.attach(MIMEText(body, "plain"))
        filename = str(id_usuario)+".pdf"
        with open(filename, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition",f"attachment; filename= {filename}",)
        message.attach(part)
        text = message.as_string()
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)

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
    def crear_pedido(self, id_cliente, id_usuario,fecha, firma, observacion, direccion):
        try:
            with self.conn.cursor() as cursor:
                consulta = "INSERT INTO pedido (id_cliente, id_usuario, fecha, firma, observacion, direccion, activo) VALUES(%s,%s,%s,%s,%s,%s,'PENDIENTE')"
                cursor.execute(consulta, (id_cliente, id_usuario, fecha, firma, observacion,direccion))
                self.conn.commit()
                cursor.close()
                pedido = self.get_last_id_pedido(id_usuario)
                return {"message": "Registro Realizado", "status": 200,"payload":pedido}
        except Exception as e:
            self.anular_transaccion()
            return {"message": "Error "+str(e), "status": 500,"payload": -1}

    """Este metodo se encarga de dar el id del ultimo pedido que creo el usuario
        Arguments:
            id_usuario {bigint} -- el id del usuario que realizo el pedido
        Returns:
            retorna un json que contiene un mensaje del resultado de la operacion
    """
    def get_last_id_pedido(self, id_usuario):
        pedido = -1
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT id_pedido FROM pedido WHERE id_usuario = %s ORDER BY id_pedido DESC LIMIT 1"
                cursor.execute(consulta, (id_usuario,))
                rows = cursor.fetchall()
                for row in rows:
                    pedido = row[0]
                cursor.close()
                return pedido
        except Exception as e:
            print(str(e))
            self.anular_transaccion()
            return pedido

    """Este metodo se encarga de buscar un pedido que coincida con el input
        Arguments:
            id_pedido {bigint} -- el id del usuario que realizo el pedido
        Returns:
            retorna un json que contiene un mensaje del resultado de la operacion
    """
    def search_pedido(self, id_pedido):
        id_cliente = -1
        cliente = {"id_cliente": 0, "id_tipo_doc": "", "nombre": "", "apellido": "", "correo": "","activo": "", "direcciones": [], "telefonos": []}
        pedido = {"id_pedido":-1, "id_cliente": 0, "id_usuario":0, "fecha":"", "firma":"", "observacion":"", "activo": "", "direccion":""}
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT id_pedido, id_cliente, id_usuario,TO_CHAR(fecha, 'YYYY-MM-DD'), firma, observacion, activo, direccion  FROM pedido WHERE id_pedido = %s "
                cursor.execute(consulta, (id_pedido,))
                rows = cursor.fetchall()
                for row in rows:
                    pedido = {"id_pedido":row[0], "id_cliente": row[1], "id_usuario": row[2], "fecha":row[3], "firma":row[4], "observacion":row[5], "activo": row[6], "direccion":row[7]}
                    id_cliente = row[1]
                cursor.close()
                cliente = self.search_cliente(id_cliente)
                unidades = self.dar_items_guardados(id_pedido)
                return {"pedido": pedido, "cliente": cliente, "unidades": unidades}
        except Exception as e:
            print(str(e))
            self.anular_transaccion()
            return pedido

    def search_cliente(self, id_cliente):
        cliente = {"id_cliente": 0, "id_tipo_doc":"", "nombre":"", "apellido": "", "correo": "","activo": 0}
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT * FROM cliente WHERE id_cliente = %s"
                cursor.execute(consulta, (id_cliente,))
                rows = cursor.fetchall()
                for row in rows:
                    cliente = {"id_cliente": row[0], "id_tipo_doc": row[1], "nombre": row[2], "apellido": row[3], "correo": row[4],"activo": row[5]}
                cursor.close()
                return cliente
        except Exception as e:
            self.anular_transaccion()
            print(str(e))
            return cliente

    def search_pedidos_usuario(self, id_usuario):
        pedidos = []
        try:
            with self.conn.cursor() as cursor:
                consulta = "select pedido.id_pedido, concat(cliente.nombre,' ',cliente.apellido) from pedido join cliente on cliente.id_cliente = pedido.id_cliente where id_usuario = %s order by pedido.id_pedido desc"
                cursor.execute(consulta, (id_usuario,))
                rows = cursor.fetchall()
                for row in rows:
                    pedidos.append({"id_pedido": row[0], "id_cliente": row[1]})
                cursor.close()
                return {"payload":pedidos, "status":200}
        except Exception as e:
            self.anular_transaccion()
            return {"payload":pedidos, "status":500}

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
            unidades = int(unidades)
            und = valores["unidades"]
            mts = valores["metros"]
            mts = mts - (1.5*unidades)
            if und > 0 and und >= unidades:
                with self.conn.cursor() as cursor:
                    consulta = "INSERT INTO ped_referencia (id_pedido, id_consecutivo, unidades, precio, metros,activo) VALUES(%s,%s,%s,%s,0,true)"
                    cursor.execute(consulta, (id_pedido, id_consecutivo, unidades, precio))
                    self.conn.commit()
                    cursor.close()
                    und = und - unidades
                    if self.actualizar_unidades(id_consecutivo,und):
                        return {"message": "Nueva Referencia Agregada", "status": 200}
                    else:
                        self.anular_transaccion()
                        return {"message": "No se pudo actaulizar las unidades", "status": 200}
            elif mts >= 0:
                with self.conn.cursor() as cursor:
                    consulta = "INSERT INTO ped_referencia (id_pedido, id_consecutivo, unidades, precio, metros,activo) VALUES(%s,%s,%s,%s,0,true)"
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
            self.anular_transaccion()
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
            self.anular_transaccion()
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
            self.anular_transaccion()
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
            self.anular_transaccion()
            return valores

    """Este metodo me permite dar las unidades y metros disponibles de una referencia-talla
        
        Arguments:
            id_consecutivo {bigint} -- id del item que esta asociado a la tabla ref_color_talla
        
        Returns:
            retorna un json el cual contiene la cantidad de unidades y metros disponibles de la referencia-talla
     """           

    def sumar_unidades_pedido_cons(self, id_consecutivo, id_pedido):
        valores ={"unidades": 0, "metros": 0}
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT SUM(unidades), SUM(metros) FROM ped_referencia WHERE id_consecutivo = %s and id_pedido = %s"
                cursor.execute(consulta, (id_consecutivo,id_pedido))
                rows = cursor.fetchall()
                for row in rows:
                    valores ={"unidades": row[0], "metros": row[1]}
                cursor.close()
                return valores
        except Exception as e:
            print(str(e))
            self.anular_transaccion()
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
            valores = self.dar_unidades_disponibles(id_consecutivo)
            und = valores["unidades"]
            valores_agregar = self.sumar_unidades_pedido_cons(id_consecutivo, id_pedido)
            und_agregar = valores_agregar["unidades"]
            print(und, und_agregar)
            und = int(und)+int(und_agregar)
            with self.conn.cursor() as cursor:
                consulta = "DELETE FROM ped_referencia WHERE id_pedido = %s AND id_consecutivo = %s"
                cursor.execute(consulta, (id_pedido, id_consecutivo))
                self.conn.commit()
                cursor.close()
                self.actualizar_unidades(id_consecutivo,und)
                return {"message": "Registro Eliminado", "status": 200}
        except Exception as e:
            self.anular_transaccion()
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
    def editar_pedido(self, id_pedido, id_cliente,fecha, firma, observacion, activo, direccion, id_usuario):
               
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE pedido SET id_cliente = %s, fecha = %s, firma = %s, observacion = %s, activo =%s, direccion=%s WHERE id_pedido = %s"
                cursor.execute(consulta, (id_cliente, fecha, firma, observacion, activo, direccion, id_pedido))
                self.conn.commit()
                cursor.close()
                if(activo == 'ENVIADO'):
                    self.generar_pdf(id_pedido, id_usuario)
                    correo = self.dar_correo_cliente(id_pedido)
                    self.enviar_correo(id_usuario,id_pedido,correo)
                    self.enviar_correo(id_usuario,id_pedido,"asistente.mercadeo@spataro.com.co")
                return {"message": "Cambios Realizados", "status": 200}
        except Exception as e:
            self.anular_transaccion()
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
                consulta = """SELECT RC.id_referencia, RC.id_color, PR.unidades, PR.precio, RCT.id_talla, PR.id_consecutivo FROM ref_color AS RC INNER JOIN ref_color_talla AS RCT ON RCT.id_ref_color = RC.id_ref_color INNER JOIN 
                ped_referencia AS PR ON PR.id_consecutivo = RCT.id_consecutivo WHERE  PR.id_pedido = %s AND PR.activo = true
                """
                cursor.execute(consulta, (id_pedido,))
                rows = cursor.fetchall()
                for row in rows:
                    items.append({"referencia": row[0], "color": row[1], "unidades": str(row[2]), "precio": str(row[3]), "id_talla": str(row[4]), "id_consecutivo": str(row[5])})
                cursor.close()
                suma = self.sumar_items_guardados(id_pedido)
                count = self.contar_items_guardados(id_pedido)
                precio_total = suma if suma != None else 0
                unidades_total = count if count != None else 0
                return {"payload":{"items": items, "precio_total": str(precio_total), "unidades_total": str(unidades_total)}, "status": 200}
        except Exception as e:
            print(str(e))
            self.anular_transaccion()
            return {"payload":{"items": [], "precio_total": 0, "unidades_total": 0}, "status": 500}

    def dar_correo_cliente(self, id_pedido):
        correo = "leonardo.sabogal@spataro.com"
        try:
            with self.conn.cursor() as cursor:
                consulta = """select cliente.correo from pedido join cliente on cliente.id_cliente = pedido.id_cliente where pedido.id_pedido = %s
                """
                cursor.execute(consulta, (id_pedido,))
                rows = cursor.fetchall()
                for row in rows:
                    correo = row[0]
                cursor.close()
                return correo
        except Exception as e:
            print(str(e))
            self.anular_transaccion()
            return correo


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
            self.anular_transaccion()
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
            self.anular_transaccion()
            return contar

    """este metodo se encarga de buscar una lista de referencias que coincida con el input
        
    Arguments:
    id_referencia {char(50)} -- el id de la referencia a buscar
        
    Returns:
        retorna una lista de referencias-color que coinciden con el patron
    """ 
    def buscar_referencia(self, id_referencia):
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT R.id_referencia FROM referencia AS R WHERE R.id_referencia like UPPER(%s) and R.activo = 'A' LIMIT 10"""
                ref_pattern = '%{}%'.format(id_referencia)
                cursor.execute(consulta, (ref_pattern,))
                rows = cursor.fetchall()
                sugerencias = []
                for row in rows:
                    sugerencias.append(row[0])
                cursor.close()
                return {"payload":sugerencias}
        except Exception as e:
            str(e)
            self.anular_transaccion()
            return {"payload":[]}

    """este metodo se encarga de buscar una lista de referencia-color que coincida con el input
        
    Arguments:
    id_referencia {char(50)} -- el id de la referencia a buscar
        
    Returns:
        retorna una lista de referencias-color que coinciden con el patron
    """ 
    def buscar_referencia_color(self, id_referencia):
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT DISTINCT RC.id_ref_color, (RC.id_color ||' '||COL.nombre) FROM referencia as R INNER JOIN ref_color AS RC ON RC.id_referencia = R.id_referencia AND RC.activo = 'A' 
                 INNER JOIN color AS COL ON COL.id_color = RC.id_color WHERE R.id_referencia = %s and R.activo = 'A'"""
                cursor.execute(consulta, (id_referencia.upper(),))
                rows = cursor.fetchall()
                sugerencias = []
                for row in rows:
                    sugerencias.append({"value":row[0], "label": row[1]})
                cursor.close()
                return {"status":200, "payload": sugerencias}
        except Exception as e:
            str(e)
            self.anular_transaccion()
            return {"status":500, "payload": []}

    """este metodo se encarga de buscar una lista de referencia-color-talla que coincida con el input
        
    Arguments:
    id_referencia {char(50)} -- el id de la referencia-color a buscar
        
    Returns:
        retorna una lista de referencias-color-talla que coinciden con el patron
    """ 
    def buscar_referencia_color_talla(self, id_ref_color):
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT DISTINCT * FROM ref_color_talla WHERE id_ref_color = %s"""
                cursor.execute(consulta, (id_ref_color,))
                rows = cursor.fetchall()
                sugerencias = []
                for row in rows:
                    sugerencias.append({"id_talla": row[5], "id_consecutivo": row[1],"unidades": row[2], "metros": row[3], "precio": row[4]})
                cursor.close()
                return {"status":200, "payload": sugerencias}
        except Exception as e:
            str(e)
            self.anular_transaccion()
            return {"status":500, "payload": []}

    """este metodo se encarga de dar el encabezado del pedido a imprimir
        
    Arguments:
    id_referencia {char(50)} -- el id del pedido
        
    Returns:
        retorna un objeto con la información del pedido
    """ 
    def get_encabezado_pedido(self, id_pedido):
        today = str(date.today())
        data =[]
        pedido ={"data": data,"firma":"", "observacion": ""}
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT (USU.nombre||' '||USU.apellido) as vendedor, USU.id_usuario as id_vendedor, (CL.nombre || ' '||CL.apellido) as cliente, CL.id_cliente, PE.direccion as direccion_desp, TO_CHAR(PE.fecha, 'YYYY-MM-DD') as fecha_desp, PE.firma, PE.observacion FROM pedido AS PE JOIN cliente AS CL ON CL.id_cliente = PE.id_cliente 
                JOIN usuario AS USU ON USU.id_usuario = PE.id_usuario WHERE PE.id_pedido = %s"""
                cursor.execute(consulta, (id_pedido,))
                rows = cursor.fetchall()
                for row in rows:
                    data.append(['Fecha', 'Vendedor','I.D Vendedor',''])
                    data.append([today, row[0], row[1]])
                    data.append(['Cliente', 'NIT O C.C','Dirección Despacho','Fecha Despacho'])
                    data.append([row[2], row[3], row[4], row[5]])
                    pedido ={"observacion": row[7],"firma":row[6], "data": data}
                cursor.close()
                return pedido
        except Exception as e:
            print(str(data))
            self.anular_transaccion()
            return pedido

    """este metodo se encarga de dar las direcciones del cliente del pedido a imprimir
        
    Arguments:
    id_referencia {char(50)} -- el id del pedido
        
    Returns:
        retorna un objeto con la información del cliente
    """ 
    def get_telefonos_cliente(self, id_pedido):
        data =[]
        data.append(['Cliente', 'Teléfono','Ciudad', 'País'])
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT (CL.nombre|| ' ' ||CL.apellido) as nombre, TL.telefono, TL.id_ciudad, TL.id_pais 
                    FROM pedido AS PD join cliente as CL on CL.id_cliente = PD.id_cliente 
                    join telefono as TL on TL.id_cliente = CL.id_cliente
                    where PD.id_pedido = %s"""
                cursor.execute(consulta, (id_pedido,))
                rows = cursor.fetchall()
                for row in rows:
                    data.append([row[0], row[1], row[2], row[3]])
                cursor.close()
                return data
        except Exception as e:
            print(str(e))
            self.anular_transaccion()
            return data

    """este metodo se encarga de dar las unidades registradas de un pedido       
    Arguments:
        id_pedido: el id del pedido
    Returns:
        retorna un arreglo con las unidades registradas
    """ 
    def get_registros_pedido(self, id_pedido):
        resultado = [['REFERENCIA', 'COLOR', 'TALLA', 'UNIDADES', 'PRECIO UNITARIO']]
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT RC.id_referencia,RC.id_color,RCT.id_talla, PD.unidades, PD.precio FROM ped_referencia AS PD 
                        JOIN ref_color_talla AS RCT ON RCT.id_consecutivo = PD.id_consecutivo
                        JOIN ref_color as RC ON RC.id_ref_color = RCT.id_ref_color
                        WHERE id_pedido = %s"""
                cursor.execute(consulta,(id_pedido,))
                rows = cursor.fetchall()
                for row in rows:
                    resultado.append([row[0],row[1],row[2],row[3],row[4]])
                cursor.close()
                return resultado
        except Exception as e:
            print(str(e))
            self.anular_transaccion()
            return resultado

    """
    Add the page number
    """
    def addPageNumber(self,canvas, doc):
        page_num = canvas.getPageNumber()
        text = "Página # %s" % page_num
        canvas.drawRightString(200*mm, 20*mm, text)

    """Arguments:
    id_usuario {char(50)} -- el id del usuario que està generando el pdf
        
    Returns:
        retorna un archivo pdf
    """ 
    def generar_pdf(self, id_pedido,id_usuario):
        styles = getSampleStyleSheet()
        #stylos del titulo
        title_style = styles['Title']
        title_style.fontName = 'Times-BoldItalic'
        title_style.fontSize = 20
        story = []
        #stylos de la tabla
        table_style = TableStyle([('BACKGROUND',(0,0),(3,0), colors.gold),
        ('BACKGROUND',(0,2),(3,2), colors.gold),
        ('SPAN',(1,0),(2,0)),
        ('SPAN',(1,1),(2,1)),
        ('FONTSIZE', (0, 0), (-1, 0), 13),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('FONTNAME',(0,0),(-1,-1),'Times-Italic'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.red),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN',(0,0),(-1,-1),'CENTER')])
        im = Image("logo_spataro.png", width=150, height=150)
        im.hAlign = 'LEFT'
        story.append(im)
        story.append(Paragraph("Orden de Pedido # "+str(id_pedido),title_style))
        data=self.get_encabezado_pedido(id_pedido)
        encabezado_pedido=data["data"]
        table_style = TableStyle([('BACKGROUND',(0,0),(3,0), colors.gold),
        ('FONTSIZE', (0, 0), (-1, 0), 13),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('FONTNAME',(0,0),(-1,-1),'Times-Italic'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.red),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN',(0,0),(-1,-1),'CENTER')])
        table = Table(encabezado_pedido)
        table.setStyle(table_style)
        story.append(Spacer(0,10))
        story.append(table)
        story.append(Spacer(0,10))
        telefono_cliente = self.get_telefonos_cliente(id_pedido)
        table_phone = Table(telefono_cliente)
        table_phone.setStyle(table_style)
        story.append(table_phone)
        story.append(Spacer(0,10))
        #estilos de parrago normal
        normal_style = styles['Title']
        normal_style.fontName = 'Times-Italic'
        normal_style.fontSize = 16
        story.append(Paragraph("Detalles del pedido",normal_style))
        story.append(Spacer(0,10))
        #tabla detalle
        table_style = TableStyle([('BACKGROUND',(0,0),(18,0), colors.gold),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('FONTNAME',(0,0),(-1,-1),'Times-Italic'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.red),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN',(0,0),(-1,-1),'CENTER')])
        detalle_encabezado = self.get_registros_pedido(id_pedido)
        table_encabezado = Table(detalle_encabezado)
        table_encabezado.setStyle(table_style)
        story.append(table_encabezado)
        story.append(Spacer(0,10))
        informacion_final = self.dar_items_guardados(id_pedido)["payload"]
        story.append(Paragraph("Total Unidades: "+informacion_final['unidades_total'],normal_style))
        locale.setlocale( locale.LC_ALL, '' )
        valor = locale.currency(float(informacion_final['precio_total']), grouping=True)
        story.append(Paragraph("Valor Total: "+valor,normal_style))
        #observacion
        try:
            firma = data["firma"]
            if(firma != ''):
                image_64_decode = base64.b64decode(data["firma"])
                with open(str(id_usuario)+".png", 'wb+') as f:
                    f.write(image_64_decode)
                f.close()
                im = Image(str(id_usuario)+".png", width=100, height=100)
                im.hAlign = 'CENTER'
                story.append(im)
            else:
                im = Image("sin_firma.png", width=100, height=100)
                im.hAlign = 'CENTER'
                story.append(im)
        except Exception:
            print('error')
        normal_style = styles['Title']
        normal_style.fontName = 'Times-Italic'
        normal_style.fontSize = 16
        story.append(Paragraph("Firma del Cliente",normal_style))
        normal_style = styles['Normal']
        normal_style.fontName = 'Times-Italic'
        normal_style.fontSize = 16
        story.append(Paragraph("Observación: "+data["observacion"],normal_style))
        story.append(Spacer(0,10))
        normal_style = styles['Normal']
        normal_style.fontName = 'Times-Italic'
        normal_style.fontSize = 16
        normal_style.leading = 20
        story.append(Paragraph("""Nota:""",normal_style))
        story.append(Spacer(0,8))
        story.append(Paragraph("""Los despachos podrán tener una toleracia de más o menos 10% en unidades.""",normal_style))
        story.append(Spacer(0,5))
        story.append(Paragraph("""El cliente que aparece en este documento compra la mercancia incluida en el exclusivamente para su venta al detal.""",normal_style))
        story.append(Spacer(0,5))
        story.append(Paragraph("""La mercancia que trata el presente documento se considera en consignación hasta tanto no haya sido cancelada la totalidad de su valor.""",normal_style))
        
        
        doc = SimpleDocTemplate(str(id_usuario)+".pdf", pagesize=legal, topMargin=3)
        doc.build(story, onFirstPage=self.addPageNumber, onLaterPages=self.addPageNumber)