from flask import Flask, request, render_template_string
import pandas as pd

app = Flask(__name__)

HTML_FORM = """
<!doctype html>
<html>
    <head><title>Subir archivo</title></head>
    <body>
        <h2>Sube un archivo TXT</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="archivo">
            <input type="submit" value="Cargar">
        </form>
    </body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "archivo" not in request.files:
            return "No se ha seleccionado ningún archivo."
        
        archivo = request.files["archivo"]
        if archivo.filename == "":
            return "Nombre de archivo vacío."
        
        try:
            # Leer el archivo con pandas
            df = pd.read_csv(archivo, sep="\t")  # Ajusta el separador según corresponda
            return f"Archivo cargado correctamente:<br>{df.head().to_html()}"
        except Exception as e:
            return f"Error al procesar el archivo: {str(e)}"
    
    return render_template_string(HTML_FORM)

if __name__ == "__main__":
    app.run(debug=True)
