import psycopg2

#parametros de la conexion
server = 'localhost'
db_name = 'spataro_pedidos'
user = 'postgres'
password = 'cristiano1994'

try:
    conn = psycopg2.connect(host=server,database=db_name, user=user, password=password)
    print("Conexion realizada")
    # OK! conexion exitosa
except Exception as e:
    # Atrapar error
    print("Ocurrio un error al conectar a SQL Server: ", e)