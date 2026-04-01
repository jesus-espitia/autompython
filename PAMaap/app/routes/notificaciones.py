from flask import session, request, current_app
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# 🔒 Control para evitar múltiples envíos en una misma petición
_notificado = False


def enviar_notificacion_uso(funcion):
    global _notificado

    # Evitar duplicados en la misma request
    if _notificado:
        return

    try:
        usuario = session.get("user", {})
        nombre = usuario.get("fullname", "Desconocido")
        correo_usuario = usuario.get("email", "No disponible")

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ip = request.remote_addr or "No disponible"

        destinatarios = [
            correo_usuario,
            current_app.config["EMAIL_ADDRESS"]
        ]

        msg = MIMEMultipart("alternative")
        msg["Subject"] = "📊 Uso de función - PAMaap"
        msg["From"] = current_app.config["EMAIL_ADDRESS"]
        msg["To"] = ", ".join(destinatarios)
        html = f"""
        <html>
        <body style="margin:0;padding:0;background:#050505;font-family:Segoe UI,Arial;">
            <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0;">
                <tr>
                    <td align="center">
                        <table width="500" cellpadding="0" cellspacing="0"
                            style="background:#0f0f0f;border-radius:12px;border:1px solid #252525;padding:40px;text-align:center;">

                            <tr>
                                <td style="color:#ffffff;font-size:22px;font-weight:700;">
                                    Notificación de uso - PAMaap
                                </td>
                            </tr>

                            <tr>
                                <td style="color:#a0a0a0;font-size:14px;padding:20px 0;">
                                    Hola <strong style="color:#ffffff;">{nombre}</strong>,<br>
                                    Se ha detectado el uso de una función dentro de la plataforma:
                                </td>
                            </tr>

                            <tr>
                                <td>
                                    <div style="background:#141414;border:1px solid #252525;
                                        border-radius:10px;padding:15px;font-size:18px;
                                        font-weight:600;color:#ffd000;">
                                        {funcion}
                                    </div>
                                </td>
                            </tr>

                            <tr>
                                <td style="color:#a0a0a0;font-size:13px;padding-top:20px;text-align:left;">
                                    <strong style="color:#ffffff;">Detalles:</strong><br><br>

                                    Usuario: <span style="color:#ffffff;">{nombre}</span><br>
                                    Correo: <span style="color:#ffffff;">{correo_usuario}</span><br>
                                    Fecha: <span style="color:#ffffff;">{fecha}</span><br>
                                    IP: <span style="color:#ffffff;">{ip}</span>
                                </td>
                            </tr>

                            <tr>
                                <td style="color:#5a5a5a;font-size:12px;padding-top:25px;">
                                    Este es un mensaje automático de seguridad y monitoreo de PAMaap.
                                </td>
                            </tr>

                            <tr>
                                <td align="center" style="padding-top:30px;">
                                    <img src="https://raw.githubusercontent.com/jesus-espitia/autompython/refs/heads/main/PAMaap/app/Static/img/firma/firma_PAMaap.png"
                                            alt="Firma PAMaap"
                                            style="width:590px;opacity:0.95;">
                                </td>
                            </tr>

                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, "html"))

        server = smtplib.SMTP(
            current_app.config["SMTP_SERVER"],
            current_app.config["SMTP_PORT"]
        )
        server.starttls()
        server.login(
            current_app.config["EMAIL_ADDRESS"],
            current_app.config["EMAIL_PASSWORD"]
        )
        server.sendmail(
            current_app.config["EMAIL_ADDRESS"],
            destinatarios,
            msg.as_string()
        )
        server.quit()

        _notificado = True

    except Exception as e:
        print("Error notificación:", e)


# 🔥 FUNCIÓN AUTOMÁTICA (LA CLAVE)
def activar_notificaciones(app):
    
    @app.after_request
    def detectar_funciones(response):
        global _notificado
        _notificado = False  # reset por request

        try:
            if "user" not in session:
                return response

            ruta = request.path

            # 🎯 SOLO rutas de funciones (tus tarjetas)
            if ruta.startswith("/funcion/"):

                # evitar archivos estáticos
                if any(x in ruta for x in ["static", ".js", ".css", ".png", ".jpg", "favicon"]):
                    return response

                # limpiar nombre
                nombre_funcion = ruta.replace("/funcion/", "").replace("_", " ").title()

                enviar_notificacion_uso(nombre_funcion)

        except Exception as e:
            print("Error automático:", e)

        return response

    return app


# 🔗 Tu ruta manual (no se toca)
def generarNotificacionSMTP():
    enviar_notificacion_uso("Prueba de notificación")
    return "Correo enviado correctamente"