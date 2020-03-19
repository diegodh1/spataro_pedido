import io
import pandas as pd
import base64

class Referencia:
    def __init__(self, conn):
        self.conn = conn

    def guardar_referencia(self, base64_excel, tipo):
        if tipo == "UND":
            return self.guardar_referencia_u(base64_excel)
        else:
            return self.guardar_referencia_m(base64_excel)

    def guardar_referencia_m(self, base64_excel):
        e = base64.b64decode(base64_excel)
        df = pd.read_excel(e)
        size = df.shape
        rows = size[0]
        try:
            for i in range(rows):
                self.insertar_referenca(df['referencia'][i], df['activo'][i])
                self.insertar_color(df['color'][i], df['activo'][i])
                self.insertar_ref_color(df['referencia'][i],df['color'][i],df['activo'][i])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],36,df['talla36'][i],df['precio'][i+1])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],37,df['talla37'][i],df['precio'][i+1])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],38,df['talla38'][i],df['precio'][i+1])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],39,df['talla39'][i],df['precio'][i+1])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],40,df['talla40'][i],df['precio'][i+1])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],41,df['talla41'][i],df['precio'][i+1])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],42,df['talla42'][i],df['precio'][i+1])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],43,df['talla43'][i],df['precio'][i+1])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],44,df['talla44'][i],df['precio'][i+1])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],45,df['talla45'][i],df['precio'][i+1])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],46,df['talla46'][i],df['precio'][i+1])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],47,df['talla47'][i],df['precio'][i+1])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],48,df['talla48'][i],df['precio'][i+1])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],49,df['talla49'][i],df['precio'][i+1])
                self.insertar_ref_color_talla_m(df['referencia'][i],df['color'][i],50,df['talla50'][i],df['precio'][i+1])
            return {"mensaje": "Registros Realizados", "status": "200"}
        except Exception as e:
            return {"mensaje": "No se pudo realizar el registro "+str(e), "status": "500"}

    def guardar_referencia_u(self, base64_excel):
        e = base64.b64decode(base64_excel)
        df = pd.read_excel(e)
        size = df.shape
        rows = size[0]
        try:
            for i in range(rows):
                self.insertar_referenca(df['referencia'][i], df['activo'][i])
                self.insertar_color(df['color'][i], df['activo'][i])
                self.insertar_ref_color(df['referencia'][i],df['color'][i],df['activo'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],36,df['talla36'][i],df['precio'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],37,df['talla37'][i],df['precio'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],38,df['talla38'][i],df['precio'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],39,df['talla39'][i],df['precio'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],40,df['talla40'][i],df['precio'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],41,df['talla41'][i],df['precio'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],42,df['talla42'][i],df['precio'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],43,df['talla43'][i],df['precio'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],44,df['talla44'][i],df['precio'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],45,df['talla45'][i],df['precio'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],46,df['talla46'][i],df['precio'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],47,df['talla47'][i],df['precio'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],48,df['talla48'][i],df['precio'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],49,df['talla49'][i],df['precio'][i])
                self.insertar_ref_color_talla_u(df['referencia'][i],df['color'][i],50,df['talla50'][i],df['precio'][i])
            return {"mensaje": "Registros Realizados", "status": "200"}
        except Exception as e:
            return {"mensaje": "No se pudo realizar el registro"+str(e), "status": "500"}

    #-----metodos necesarios para crear o editar una referencia-----
    def insertar_referenca(self, id_referencia, activo):
        try:
            if self.existe_referencia(id_referencia):
                self.editar_referencia(id_referencia, activo)
            else:
                with self.conn.cursor() as cursor:
                    consulta = "INSERT INTO referencia (id_referencia, activo) VALUES(%s,%s)"
                    cursor.execute(consulta, (id_referencia, activo))
                    self.conn.commit()
                    cursor.close()
            return {"message": "Registro Realizado", "status": "1"}
        except Exception as e:
            return {"message": "Error"+str(e), "status": "2"}

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
            print(str(e))
            return False

    def editar_referencia(self, id_referencia, activo):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE referencia  SET activo = %s WHERE id_referencia = %s"
                cursor.execute(consulta, (activo, id_referencia))
                self.conn.commit()
                cursor.close()
                return {"message": "Registro Realizado", "status": "1"}
        except Exception as e:
            return {"message": "Error"+str(e), "status": "2"}


    #-----metodos necesarios para crear o editar un color-----
    def insertar_color(self, id_color, activo):
        try:
            if self.existe_color(id_color):
                self.editar_color(id_color, activo)
            else:
                with self.conn.cursor() as cursor:
                    consulta = "INSERT INTO color (id_color, activo) VALUES(%s,%s)"
                    cursor.execute(consulta, (id_color, activo))
                    self.conn.commit()
                    cursor.close()

            return {"message": "Registro Realizado", "status": "1"}
        except Exception as e:
            return {"message": "Error"+str(e), "status": "2"}
    
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
            print(str(e))
            return False

    def editar_color(self, id_color, activo):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE color SET activo = %s WHERE id_color = %s"
                cursor.execute(consulta, (activo, id_color))
                self.conn.commit()
                cursor.close()
                return {"message": "Registro Realizado", "status": "1"}
        except Exception as e:
            return {"message": "Error"+str(e), "status": "2"}

    #-----metodos necesarios para crear o editar un ref_color-----
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

            return {"message": "Registro Realizado", "status": "1"}
        except Exception as e:
            return {"message": "Error"+str(e), "status": "2"}
    
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
            print(str(e))
            return False

    def editar_ref_color(self,id_referencia, id_color, activo):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE ref_color SET activo = %s WHERE id_referencia=%s AND id_color = %s"
                cursor.execute(consulta, (activo, id_referencia, id_color))
                self.conn.commit()
                cursor.close()
                return {"message": "Registro Realizado", "status": "1"}
        except Exception as e:
            return {"message": "Error"+str(e), "status": "2"}

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
            print(str(e))
            return '-1'

    #-----metodos necesarios para crear o editar un ref_color_talla-----
    def insertar_ref_color_talla_u(self,id_referencia, id_color, id_talla, unidades, precio):
        
        try:
            id_ref_color = self.select_ref_color(id_referencia,id_color)
            if self.existe_ref_color_talla(id_ref_color, id_talla):
                self.editar_ref_color_talla_u(id_ref_color, id_talla, unidades, precio)
            else:
                with self.conn.cursor() as cursor:
                    consulta = "INSERT INTO ref_color_talla (id_ref_color, id_talla, unidades, precio, metros) VALUES(%s,%s,%s,%s,0)"
                    cursor.execute(consulta, (id_ref_color, id_talla, int(str(unidades)), int(str(precio))))
                    self.conn.commit()
                    cursor.close()
            return {"message": "Registro Realizado", "status": "200"}
        except Exception as e:
            print(str(e))
            return {"message": "Error"+str(e), "status": "500"}

    def insertar_ref_color_talla_m(self,id_referencia, id_color, id_talla, metros, precio):
        try:
            id_ref_color = self.select_ref_color(id_referencia,id_color)
            if self.existe_ref_color_talla(id_ref_color, id_talla):
                self.editar_ref_color_talla_u(id_ref_color, id_talla, metros, precio)
            else:
                with self.conn.cursor() as cursor:
                    consulta = "INSERT INTO ref_color_talla (id_ref_color, id_talla, metros, precio, unidades) VALUES(%s,%s,%s,%s,0)"
                    cursor.execute(consulta, (id_ref_color, id_talla, metros, precio))
                    self.conn.commit()
                    cursor.close()

            return {"message": "Registro Realizado", "status": "200"}
        except Exception as e:
            print(str(e))
            return {"message": "Error"+str(e), "status": "500"}
    
    def existe_ref_color_talla(self, id_ref_color, id_talla):
        try:
            with self.conn.cursor() as cursor:
                consulta = "SELECT COUNT(*) as cantidad FROM ref_color_talla WHERE id_ref_color = %s AND id_talla=%s"
                cursor.execute(consulta, (id_ref_color,id_talla))
                rows = cursor.fetchall()
                esta = False
                for row in rows:
                    if row[0] > 0:
                        esta = True
                cursor.close()
                return esta
        except Exception as e:
            str(e)
            return False

    def editar_ref_color_talla_u(self,id_ref_color, id_talla, unidades, precio):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE ref_color_talla SET unidades = %s, precio=%s  WHERE id_ref_color=%s AND id_talla = %s"
                cursor.execute(consulta, (int(str(unidades)), int(str(precio)), id_ref_color, id_talla))
                self.conn.commit()
                cursor.close()
                return {"message": "Registro Realizado", "status": "1"}
        except Exception as e:
            return {"message": "Error"+str(e), "status": "2"}

    def editar_ref_color_talla_m(self,id_ref_color, id_talla, metros, precio):
        try:
            with self.conn.cursor() as cursor:
                consulta = "UPDATE ref_color_talla SET metros = %s, precio=%s  WHERE id_ref_color=%s AND id_talla = %s"
                cursor.execute(consulta, (int(str(metros)), int(str(precio)), id_ref_color, id_talla))
                self.conn.commit()
                cursor.close()
                return {"message": "Registro Realizado", "status": "1"}
        except Exception as e:
            return {"message": "Error"+str(e), "status": "2"}