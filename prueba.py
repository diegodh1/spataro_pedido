import conection
import modulos.Pedido as pedido
import pdb

nuevo_pedido = pedido.Pedido(conection.conn)
print(nuevo_pedido.generar_pdf(71,12345))