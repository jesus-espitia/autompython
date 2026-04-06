import pandas as pd
from flask import render_template, request, send_file
import tempfile
from io import BytesIO


# -------------------------
# LECTURA DE ARCHIVOS
# -------------------------
def leer_archivo(ruta, nombre):
    nombre = nombre.lower()

    try:
        if nombre.endswith((".xlsx", ".xlsm", ".xlsb", ".xls")):
            return pd.read_excel(ruta, engine="openpyxl")

        elif nombre.endswith(".csv"):
            return pd.read_csv(ruta)

        elif nombre.endswith(".txt"):
            return pd.read_csv(ruta, delimiter=None, engine="python")

        else:
            return None
    except Exception:
        return None


# -------------------------
# MARCAR DUPLICADOS
# -------------------------
def marcar_duplicados(df, columna):
    contador = {}
    nuevos_valores = []

    for val in df[columna]:
        if val in contador:
            contador[val] += 1
            nuevos_valores.append(f"{val} (duplicado {contador[val]})")
        else:
            contador[val] = 0
            nuevos_valores.append(val)

    df[columna] = nuevos_valores
    return df


# -------------------------
# FUNCIÓN PRINCIPAL
# -------------------------
def archivosPares():
    columnas_a = None
    columnas_b = None
    resultado = None
    error = None

    ruta_a = request.form.get("ruta_a")
    ruta_b = request.form.get("ruta_b")
    nombre_a = request.form.get("nombre_a")
    nombre_b = request.form.get("nombre_b")

    if request.method == "POST":
        accion = request.form.get("accion")

        # =========================
        # ANALIZAR
        # =========================
        if accion == "analizar":
            archivo_a = request.files.get("archivo_a")
            archivo_b = request.files.get("archivo_b")

            if not archivo_a or not archivo_b:
                error = "Debe seleccionar ambos archivos"
                return render_template("F_archivosPares.html", error=error)

            temp_a = tempfile.NamedTemporaryFile(delete=False)
            temp_b = tempfile.NamedTemporaryFile(delete=False)

            archivo_a.save(temp_a.name)
            archivo_b.save(temp_b.name)

            ruta_a = temp_a.name
            ruta_b = temp_b.name
            nombre_a = archivo_a.filename
            nombre_b = archivo_b.filename

            df_a = leer_archivo(ruta_a, nombre_a)
            df_b = leer_archivo(ruta_b, nombre_b)

            if df_a is None or df_b is None:
                error = "No se pudo interpretar uno de los archivos"
                return render_template("F_archivosPares.html", error=error)

            columnas_a = list(df_a.columns)
            columnas_b = list(df_b.columns)

            return render_template(
                "F_archivosPares.html",
                columnas_a=columnas_a,
                columnas_b=columnas_b,
                ruta_a=ruta_a,
                ruta_b=ruta_b,
                nombre_a=nombre_a,
                nombre_b=nombre_b
            )

        # =========================
        # PROCESAR Y EXPORTAR (MISMA LÓGICA)
        # =========================
        if accion in ["procesar", "exportar"]:

            if not ruta_a or not ruta_b:
                error = "Debe analizar los archivos primero"
                return render_template("F_archivosPares.html", error=error)

            df_a = leer_archivo(ruta_a, nombre_a)
            df_b = leer_archivo(ruta_b, nombre_b)

            col_a = request.form.get("columna_a")
            col_b = request.form.get("columna_b")
            tipo_join = request.form.get("tipo_join")

            columnas_a = list(df_a.columns)
            columnas_b = list(df_b.columns)

            df_a = marcar_duplicados(df_a, col_a)
            df_b = marcar_duplicados(df_b, col_b)

            try:
                df_resultado = pd.merge(
                    df_a,
                    df_b,
                    left_on=col_a,
                    right_on=col_b,
                    how=tipo_join
                )

                # =========================
                # SOLO MOSTRAR EN PANTALLA
                # =========================
                if accion == "procesar":
                    resultado = df_resultado.fillna("").to_dict(orient="records")

                # =========================
                # EXPORTAR A EXCEL (MEMORIA)
                # =========================
                if accion == "exportar":
                    output = BytesIO()
                    df_resultado.to_excel(output, index=False)
                    output.seek(0)

                    return send_file(
                        output,
                        as_attachment=True,
                        download_name="resultado_cruce.xlsx",
                        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )

            except Exception as e:
                error = f"Error: {str(e)}"

    return render_template(
        "F_archivosPares.html",
        columnas_a=columnas_a,
        columnas_b=columnas_b,
        resultado=resultado,
        error=error,
        ruta_a=ruta_a,
        ruta_b=ruta_b,
        nombre_a=nombre_a,
        nombre_b=nombre_b
    )