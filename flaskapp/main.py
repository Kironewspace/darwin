from flask import Flask, render_template, abort, redirect, request, url_for
import pyodbc
import base64
import random

app = Flask(__name__)

# Configuración de conexión a la base de datos
sql_config = {
    'driver': 'ODBC Driver 18 for SQL Server',
    'server': 'Miguel-PC',
    'database': 'DarwinCell',
    'user': 'SA',
    'password': 'MTp070213.'
}
conn_str = (
    f"DRIVER={sql_config['driver']};"
    f"SERVER={sql_config['server']};"
    f"DATABASE={sql_config['database']};"
    f"UID={sql_config['user']};"
    f"PWD={sql_config['password']};"
    "TrustServerCertificate=yes;"
)

def get_db_connection():
    return pyodbc.connect(conn_str)

# Función para obtener productos por categoría
def obtener_productos(categoria=None):
    productos = []
    query = """
        SELECT id, nombre, modelo, precio, imagen, categoria
        FROM Productos
    """
    if categoria and categoria != "todos":
        query += " WHERE categoria = ?"
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            if categoria and categoria != "todos":
                cursor.execute(query, categoria)
            else:
                cursor.execute(query)
            rows = cursor.fetchall()
            for row in rows:
                productos.append({
                    'id': row.id,
                    'nombre': row.nombre,
                    'modelo': row.modelo,
                    'precio': row.precio,
                    'categoria': row.categoria,
                    'imagen': base64.b64encode(row.imagen).decode('utf-8') if row.imagen else None
                })
    except Exception as e:
        print(f"Error al obtener productos: {e}")
    return productos

# Ruta para la página principal (muestra todos los productos)
@app.route('/')
def productos():
    productos = obtener_productos()
    return render_template('showproducts.html', productos=productos, categoria='todos')

# Ruta dinámica para categorías (teléfonos, cargadores, accesorios)
@app.route('/<string:categoria>')
def mostrar_productos_por_categoria(categoria):
    categorias_validas = ['telefono', 'cargador', 'accesorio']
    if categoria not in categorias_validas:
        return abort(404, description="Categoría no válida")

    productos = obtener_productos(categoria)
    return render_template('showproducts.html', productos=productos, categoria=categoria)

# Ruta para detalles del producto
@app.route('/producto/<int:producto_id>')
def producto_detalle(producto_id):
    query = """
        SELECT id, nombre, modelo, especificaciones, precio, stock, imagen 
        FROM Productos 
        WHERE id = ?
    """
    producto = None
    try:
        with pyodbc.connect(conn_str) as conn:
            cursor = conn.cursor()
            cursor.execute(query, producto_id)
            row = cursor.fetchone()
            if row:
                producto = {
                    'id': row.id,
                    'nombre': row.nombre,
                    'modelo': row.modelo,
                    'especificaciones': row.especificaciones,
                    'precio': row.precio,
                    'stock': row.stock,
                    'imagen': base64.b64encode(row.imagen).decode('utf-8') if row.imagen else None
                }
    except Exception as e:
        print(f"Error al obtener el producto: {e}")
    if producto:
        return render_template('details.html', producto_detalle=producto)
    else:
        return abort(404, description="Producto no encontrado")

# Ruta para redirigir al formulario en la misma aplicación
@app.route('/comprar/<int:producto_id>', methods=['POST'])
def comprar(producto_id):
    cantidad = request.form.get('cantidad')
    if not cantidad:
        return "Cantidad no especificada", 400
    return redirect(url_for('formulario_cliente', producto_id=producto_id, cantidad=cantidad))

# Ruta para mostrar el formulario de cliente
@app.route('/formulario/<int:producto_id>/<int:cantidad>', methods=['GET', 'POST'])
def formulario_cliente(producto_id, cantidad):
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        email = request.form.get('email')

        # Generar un código de pedido
        codigo_pedido = 'UF-' + ''.join([str(random.randint(0, 9)) for _ in range(6)])

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Guardar al cliente en la tabla Clientes
            cursor.execute(
                """
                INSERT INTO Clientes (nombre, telefono, email)
                VALUES (?, ?, ?)
                """,
                (nombre, telefono, email)
            )
            id_cliente = cursor.execute("SELECT @@IDENTITY").fetchone()[0]

            # Obtener el nombre del producto para el pedido
            cursor.execute("SELECT nombre FROM Productos WHERE id = ?", producto_id)
            producto = cursor.fetchone()
            if not producto:
                return "Producto no encontrado", 404

            nombre_producto = producto[0]

            # Guardar el pedido en la tabla Pedido
            cursor.execute(
                """
                INSERT INTO Pedido (codigo_pedido, id_cliente, nombre_cliente, id_producto, cantidad)
                VALUES (?, ?, ?, ?, ?)
                """,
                (codigo_pedido, id_cliente, nombre, producto_id, cantidad)
            )
            conn.commit()
        except Exception as e:
            return f"Error al guardar el pedido: {e}", 500
        finally:
            conn.close()

        # Redirigir al endpoint correcto: agradecimiento
        return redirect(url_for('agradecimiento', codigo_pedido=codigo_pedido))
    return render_template('shop.html', producto_id=producto_id, cantidad=cantidad)

# Ruta para mostrar la página de agradecimiento
@app.route('/agradecimiento/<codigo_pedido>')
def agradecimiento(codigo_pedido):
    return render_template('thanks.html', codigo_pedido=codigo_pedido)

# Inicio del servidor
if __name__ == '__main__':
    app.run(debug=True, port=5001)
