import email, smtplib, ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
                return {"message": "Registro Realizado", "status": 200,"id_pedido":pedido}
        except Exception as e:
            self.anular_transaccion()
            return {"message": "Error "+str(e), "status": 500,"id_pedido": -1}

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
        cliente = {"id_cliente": "", "id_tipo_doc": "", "nombre": "", "apellido": "", "correo": "","activo": "", "direcciones": [], "telefonos": []}
        pedido = {"id_pedido":"", "id_cliente": "", "id_usuario": "", "fecha":"", "firma":"", "observacion":"", "activo": "", "direccion":""}
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
        cliente = {"id_cliente": "", "id_tipo_doc":"", "nombre":"", "apellido": "", "correo": "","activo": 0}
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
                        return {"message": "Registro Realizado", "status": 200}
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
    def editar_pedido(self, id_pedido, id_cliente,fecha, firma, observacion, activo, direccion):
               
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE pedido SET id_cliente = %s, fecha = %s, firma = %s, observacion = %s, activo =%s, direccion=%s WHERE id_pedido = %s"
                cursor.execute(consulta, (id_cliente, fecha, firma, observacion, activo, direccion, id_pedido))
                self.conn.commit()
                cursor.close()
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
                precio_total = str(self.sumar_items_guardados(id_pedido))
                unidades_total = str(self.contar_items_guardados(id_pedido))
                return {"items": items, "precio_total": precio_total, "unidades_total": unidades_total, "status": 200}
        except Exception as e:
            print(str(e))
            self.anular_transaccion()
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
                    sugerencias.append({"label":row[0], "value": row[0]})
                cursor.close()
                return {"status":200, "sugerencias": sugerencias}
        except Exception as e:
            str(e)
            self.anular_transaccion()
            return {"status":500, "sugerencias": []}

    """este metodo se encarga de buscar una lista de referencia-color que coincida con el input
        
    Arguments:
    id_referencia {char(50)} -- el id de la referencia a buscar
        
    Returns:
        retorna una lista de referencias-color que coinciden con el patron
    """ 
    def buscar_referencia_color(self, id_referencia):
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT DISTINCT RC.id_ref_color, RC.id_color FROM referencia as R INNER JOIN ref_color AS RC ON RC.id_referencia = R.id_referencia AND RC.activo = 'A' 
                WHERE R.id_referencia = %s and R.activo = 'A'"""
                cursor.execute(consulta, (id_referencia.upper(),))
                rows = cursor.fetchall()
                sugerencias = []
                for row in rows:
                    sugerencias.append({"value":row[0], "label": row[1]})
                cursor.close()
                return {"status":200, "sugerencias": sugerencias}
        except Exception as e:
            str(e)
            self.anular_transaccion()
            return {"status":500, "sugerencias": []}

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
                    sugerencias.append({"id_ref_color":row[0], "id_talla": row[1], "id_consecutivo": row[2],
                    "unidades": row[3], "metros": row[4], "precio": row[5]})
                cursor.close()
                return {"status":200, "sugerencias": sugerencias}
        except Exception as e:
            str(e)
            self.anular_transaccion()
            return {"status":500, "sugerencias": []}

    """este metodo se encarga de dar el encabezado del pedido a imprimir
        
    Arguments:
    id_referencia {char(50)} -- el id del pedido
        
    Returns:
        retorna un objeto con la información del pedido
    """ 
    def get_encabezado_pedido(self, id_pedido):
        today = str(date.today())
        data =[]
        data.append(['Fecha', 'Vendedor','Id Vendedor', 'Cliente', 'NIT O C.C','Dirección Despacho', 'Fecha Despacho'])
        pedido ={"data": data,"firma":"", "observacion": ""}
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT (USU.nombre||' '||USU.apellido) as vendedor, USU.id_usuario as id_vendedor, (CL.nombre || ' '||CL.apellido) as cliente, CL.id_cliente, PE.direccion as direccion_desp, TO_CHAR(PE.fecha, 'YYYY-MM-DD') as fecha_desp, PE.firma, PE.observacion FROM pedido AS PE JOIN cliente AS CL ON CL.id_cliente = PE.id_cliente 
                JOIN usuario AS USU ON USU.id_usuario = PE.id_usuario WHERE PE.id_pedido = %s"""
                cursor.execute(consulta, (id_pedido,))
                rows = cursor.fetchall()
                for row in rows:
                    data.append([today, row[0], row[1], row[2], row[3], row[4], row[5]])
                    pedido ={"observacion": row[7],"firma":row[6], "data": data}
                cursor.close()
                return pedido
        except Exception as e:
            print(str(e))
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
    """este metodo se encarga de dar las tallas para imprimir
        
    Arguments:
        
    Returns:
        retorna un objeto con la información de las tallas
    """ 
    def get_tallas(self,id_pedido):
        data =[]
        numeros = ['REFERENCIA', 'COLORES']
        medidas = ['','','S','','M','','','L','','XL','','XXL','','','XXXL','','','','']
        alternativas = ['','']
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT id_talla, talla_alternativa FROM talla"""
                cursor.execute(consulta)
                rows = cursor.fetchall()
                for row in rows:
                    numeros.append(row[0])
                    alternativas.append(row[1])
                cursor.close()
                numeros.append('PRECIO UNITARIO')
                numeros.append('VALOR')
                alternativas.append('')
                alternativas.append('')
                data.append(numeros)
                data.append(medidas)
                data.append(alternativas)
                data = self.get_registros_pedido(id_pedido,data)
                return {"data": data, "numeros":numeros}
        except Exception as e:
            print(str(e))
            self.anular_transaccion()
            return {"data": data, "numeros":numeros}

    """este metodo se encarga de dar las unidades registradas de un pedido       
    Arguments:
        id_pedido: el id del pedido
    Returns:
        retorna un arreglo con las unidades registradas
    """ 
    def get_registros_pedido(self, id_pedido, tabla):
        temp = ['','','36','37','38','39','40','41','42','43','44','45','46','47','48','49','50','','']
        try:
            with self.conn.cursor() as cursor:
                consulta = """SELECT RC.id_referencia,RC.id_color,RCT.id_talla, PD.unidades, PD.precio, PD.precio*PD.unidades FROM ped_referencia AS PD 
                        JOIN ref_color_talla AS RCT ON RCT.id_consecutivo = PD.id_consecutivo
                        JOIN ref_color as RC ON RC.id_ref_color = RCT.id_ref_color
                        WHERE id_pedido = %s"""
                cursor.execute(consulta,(id_pedido,))
                rows = cursor.fetchall()
                for row in rows:
                    temp_reg = ['','','','','','','','','','','','','','','','','','','']
                    temp_reg[0]=row[0]
                    temp_reg[1]=row[1]
                    for i in range(0,len(temp)):
                        if str(row[2]) == str(temp[i]):
                            temp_reg[i]=row[3]
                    locale.setlocale( locale.LC_ALL, '' )
                    precio = locale.currency(float(row[4]), grouping=True)
                    valor_total = locale.currency(float(row[5]), grouping=True)
                    temp_reg[17]=precio
                    temp_reg[18]=valor_total
                    tabla.append(temp_reg)
                cursor.close()
                return tabla
        except Exception as e:
            print(str(e))
            self.anular_transaccion()
            tabla

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
        table_style = TableStyle([('BACKGROUND',(0,0),(8,0), colors.gold),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('FONTNAME',(0,0),(-1,-1),'Times-Italic'),
        ('ALIGN',(0,0),(-1,-1),'CENTER')])
        story.append(Paragraph("Orden de Pedido # "+str(id_pedido),title_style))
        data=self.get_encabezado_pedido(id_pedido)
        encabezado_pedido=data["data"]
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
        ('BACKGROUND',(0,0),(0,2), colors.gold),
        ('BACKGROUND',(1,0),(1,2), colors.gold),
        ('BACKGROUND',(17,0),(17,2), colors.gold),
        ('BACKGROUND',(18,0),(18,2), colors.gold),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TEXTCOLOR',(0,0),(-1,0),colors.black),
        ('FONTNAME',(0,0),(-1,-1),'Times-Italic'),
        ('GRID', (0,0), (-1,-1), 0.25, colors.red),
        ('SPAN', (0, 0), (0, 2)),
        ('SPAN', (1, 0), (1, 2)),
        ('SPAN', (2, 1), (3, 1)),
        ('SPAN', (4, 1), (6, 1)),
        ('SPAN', (7, 1), (8, 1)),
        ('SPAN', (9, 1), (10, 1)),
        ('SPAN', (11, 1), (13, 1)),
        ('SPAN', (14, 1), (16, 1)),
        ('SPAN', (17, 0), (17, 2)),
        ('SPAN', (18, 0), (18, 2)),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN',(0,0),(-1,-1),'CENTER')])
        data_pedido = self.get_tallas(id_pedido)
        detalle_encabezado = data_pedido['data']
        table_encabezado = Table(detalle_encabezado)
        table_encabezado.setStyle(table_style)
        story.append(table_encabezado)
        story.append(Spacer(0,10))
        informacion_final = self.dar_items_guardados(id_pedido)
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
        story.append(Paragraph("""Nota:""",normal_style))
        story.append(Spacer(0,8))
        story.append(Paragraph("""Los despachos podrán tener una toleracia de más o menos 10% en unidades.""",normal_style))
        story.append(Spacer(0,5))
        story.append(Paragraph("""El cliente que aparece en este documento compra la mercancia incluida en el exclusivamente para su venta al detal.""",normal_style))
        story.append(Spacer(0,5))
        story.append(Paragraph("""La mercancia que trata el presente documento se considera en consignación hasta tanto no haya sido cancelada la totalidad de su valor.""",normal_style))
        
        
        doc = SimpleDocTemplate(str(id_usuario)+".pdf", pagesize=landscape(letter))
        doc.build(story, onFirstPage=self.addPageNumber, onLaterPages=self.addPageNumber)