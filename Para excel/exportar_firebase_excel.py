import urllib.request
import json
from datetime import datetime, timedelta
from openpyxl import load_workbook


# =========================================================
# CONFIGURACIÓN
# =========================================================

URL_FIREBASE = "https://piloto-614ca-default-rtdb.firebaseio.com/maquinas.json"

ARCHIVO_EXCEL = "Control_Maquinas_Semanal.xlsx"

ARCHIVO_SALIDA = "Control_Maquinas_Semanal_actualizado.xlsx"


# =========================================================
# DÍAS
# =========================================================

dias = {
    0: "LUNES",
    1: "MARTES",
    2: "MIERCOLES",
    3: "JUEVES",
    4: "VIERNES",
    5: "SABADO",
    6: "DOMINGO"
}


# =========================================================
# COLUMNAS DEL EXCEL
# =========================================================
#
# LUNES      B C D
# MARTES     E F G
# MIERCOLES  H I J
# JUEVES     K L M
# VIERNES    N O P
# SABADO     Q R S
# DOMINGO    T U V
#
# Cada día:
# °C | %H | %L
# =========================================================

columnas_dias = {
    0: 2,
    1: 5,
    2: 8,
    3: 11,
    4: 14,
    5: 17,
    6: 20
}


# =========================================================
# CONVERTIR FECHA Y HORA
# =========================================================

def convertir_fecha_hora(registro):

    fecha_texto = registro.get("fecha", "")
    hora_texto = registro.get("hora", "")

    if not fecha_texto:
        return None


    # -----------------------------------------------------
    # FORMATO ACTUAL
    #
    # 5/8/2026
    # -----------------------------------------------------

    formatos_fecha = [
        "%d/%m/%Y",
        "%d/%m/%y"
    ]

    fecha = None

    for formato in formatos_fecha:

        try:

            fecha = datetime.strptime(
                fecha_texto,
                formato
            )

            break

        except ValueError:
            pass


    # -----------------------------------------------------
    # FORMATO ANTIGUO ISO
    #
    # 2026-07-31T18:30:10.348Z
    # -----------------------------------------------------

    if fecha is None:

        try:

            fecha = datetime.fromisoformat(
                fecha_texto.replace(
                    "Z",
                    "+00:00"
                )
            )

            fecha = fecha.replace(
                tzinfo=None
            )

        except:

            return None


    # -----------------------------------------------------
    # SI NO HAY HORA
    # -----------------------------------------------------

    if not hora_texto:

        return fecha


    # -----------------------------------------------------
    # LIMPIAR HORA
    #
    # Ejemplo:
    # 4:09:42 p.m.
    #
    # Lo convertimos a:
    # 4:09:42 PM
    # -----------------------------------------------------

    hora_limpia = hora_texto.lower()

    hora_limpia = hora_limpia.replace(
        "a.m.",
        "AM"
    )

    hora_limpia = hora_limpia.replace(
        "p.m.",
        "PM"
    )

    hora_limpia = hora_limpia.strip()


    # -----------------------------------------------------
    # INTENTAR CON HORA AM / PM
    # -----------------------------------------------------

    try:

        hora = datetime.strptime(
            hora_limpia,
            "%I:%M:%S %p"
        )

        return fecha.replace(
            hour=hora.hour,
            minute=hora.minute,
            second=hora.second
        )

    except:

        pass


    # -----------------------------------------------------
    # INTENTAR HORA 24 HORAS
    # -----------------------------------------------------

    try:

        hora = datetime.strptime(
            hora_limpia,
            "%H:%M:%S"
        )

        return fecha.replace(
            hour=hora.hour,
            minute=hora.minute,
            second=hora.second
        )

    except:

        pass


    return fecha


# =========================================================
# CONECTAR CON FIREBASE
# =========================================================

print()
print("==========================================")
print("   EXPORTADOR FIREBASE -> EXCEL")
print("==========================================")
print()

print("Conectando con Firebase...")


try:

    respuesta = urllib.request.urlopen(
        URL_FIREBASE,
        timeout=20
    )

    datos_firebase = json.loads(
        respuesta.read().decode("utf-8")
    )

except Exception as error:

    print()
    print("ERROR al conectar con Firebase:")
    print(error)

    input("\nPresiona Enter para cerrar...")
    exit()


print("Firebase conectado correctamente.")


# =========================================================
# COMPROBAR FIREBASE
# =========================================================

if not datos_firebase:

    print()
    print("No existen máquinas en Firebase.")

    input("\nPresiona Enter para cerrar...")
    exit()


# =========================================================
# ABRIR EXCEL
# =========================================================

try:

    wb = load_workbook(
        ARCHIVO_EXCEL
    )

    ws = wb.active

except Exception as error:

    print()
    print("ERROR al abrir el Excel:")
    print(error)

    input("\nPresiona Enter para cerrar...")
    exit()


# =========================================================
# SEMANA ACTUAL
# =========================================================

hoy = datetime.now()

inicio_semana = hoy - timedelta(
    days=hoy.weekday()
)

inicio_semana = inicio_semana.replace(
    hour=0,
    minute=0,
    second=0,
    microsecond=0
)


fin_semana = inicio_semana + timedelta(
    days=6,
    hours=23,
    minutes=59,
    seconds=59
)


print()
print(
    "Semana:",
    inicio_semana.strftime("%d/%m/%Y"),
    "-",
    fin_semana.strftime("%d/%m/%Y")
)


# =========================================================
# BUSCAR FILAS DEL EXCEL
# =========================================================

filas_maquinas = {}


for fila in range(
    3,
    ws.max_row + 1
):

    valor = ws.cell(
        row=fila,
        column=1
    ).value

    if valor:

        id_maquina = str(
            valor
        ).strip()

        filas_maquinas[
            id_maquina
        ] = fila


print()
print(
    "Máquinas encontradas en Excel:",
    len(filas_maquinas)
)


# =========================================================
# CONTADORES
# =========================================================

total_actualizados = 0

total_ignoradas = 0


# =========================================================
# RECORRER FIREBASE
# =========================================================

for id_maquina, informacion in datos_firebase.items():

    print()
    print("------------------------------------------")
    print("Máquina:", id_maquina)
    print("------------------------------------------")


    # -----------------------------------------------------
    # COMPROBAR SI EXISTE EN EL EXCEL
    # -----------------------------------------------------

    if id_maquina not in filas_maquinas:

        print(
            "  Esta máquina no está en el Excel."
        )

        print(
            "  Se ignora."
        )

        continue


    registros = informacion.get(
        "registros",
        {}
    )


    if not registros:

        print(
            "  No tiene registros."
        )

        continue


    # =====================================================
    # GUARDAR REGISTROS POR DÍA
    # =====================================================
    #
    # Ejemplo:
    #
    # MIÉRCOLES:
    #   registro 1
    #   registro 2
    #   registro 3
    #
    # Al final solamente conservaremos
    # el MÁS RECIENTE.
    # =====================================================

    registros_por_dia = {}


    for registro_id, registro in registros.items():

        if not isinstance(
            registro,
            dict
        ):
            continue


        fecha_hora = convertir_fecha_hora(
            registro
        )


        if fecha_hora is None:

            print(
                "  Registro con fecha no reconocida:",
                registro_id
            )

            continue


        # -------------------------------------------------
        # COMPROBAR SI PERTENECE A ESTA SEMANA
        # -------------------------------------------------

        if fecha_hora < inicio_semana:
            continue

        if fecha_hora > fin_semana:
            continue


        dia_semana = fecha_hora.weekday()


        # -------------------------------------------------
        # COMPROBAR SI YA HAY UN REGISTRO ESE DÍA
        # -------------------------------------------------

        registro_anterior = registros_por_dia.get(
            dia_semana
        )


        if registro_anterior is None:

            registros_por_dia[
                dia_semana
            ] = (
                fecha_hora,
                registro
            )

        else:

            fecha_anterior = registro_anterior[0]


            # ---------------------------------------------
            # SOLO REEMPLAZAR SI ES MÁS RECIENTE
            # ---------------------------------------------

            if fecha_hora > fecha_anterior:

                registros_por_dia[
                    dia_semana
                ] = (
                    fecha_hora,
                    registro
                )


    # =====================================================
    # ESCRIBIR RESULTADOS EN EXCEL
    # =====================================================

    fila_excel = filas_maquinas[
        id_maquina
    ]


    if not registros_por_dia:

        print(
            "  No tiene registros de esta semana."
        )

        continue


    for dia_semana, datos in registros_por_dia.items():

        fecha_hora = datos[0]

        registro = datos[1]


        nombre_dia = dias[
            dia_semana
        ]


        columna = columnas_dias[
            dia_semana
        ]


        # -------------------------------------------------
        # TEMPERATURA
        # -------------------------------------------------

        temperatura = registro.get(
            "temperatura",
            ""
        )


        # -------------------------------------------------
        # HUMEDAD
        # -------------------------------------------------

        humedad = registro.get(
            "humedad",
            ""
        )


        # -------------------------------------------------
        # %L
        #
        # Aceptamos los dos nombres:
        #
        # porcentajeL
        # luminosidad
        # -------------------------------------------------

        porcentajeL = registro.get(
            "porcentajeL"
        )


        if porcentajeL is None:

            porcentajeL = registro.get(
                "luminosidad",
                ""
            )


        # -------------------------------------------------
        # ESCRIBIR EN EXCEL
        # -------------------------------------------------

        ws.cell(
            row=fila_excel,
            column=columna
        ).value = temperatura


        ws.cell(
            row=fila_excel,
            column=columna + 1
        ).value = humedad


        ws.cell(
            row=fila_excel,
            column=columna + 2
        ).value = porcentajeL


        # -------------------------------------------------
        # MOSTRAR RESULTADO
        # -------------------------------------------------

        print()

        print(
            "  Día:",
            nombre_dia
        )

        print(
            "  Registros seleccionados: 1"
        )

        print(
            "  Último registro:",
            fecha_hora.strftime(
                "%d/%m/%Y %H:%M:%S"
            )
        )

        print(
            "  →",
            temperatura,
            "°C |",
            humedad,
            "%H |",
            porcentajeL,
            "%L"
        )


        total_actualizados += 1


# =========================================================
# GUARDAR ARCHIVO
# =========================================================

try:

    wb.save(
        ARCHIVO_SALIDA
    )

except Exception as error:

    print()
    print(
        "ERROR al guardar el Excel:"
    )

    print(error)

    input("\nPresiona Enter para cerrar...")
    exit()


# =========================================================
# RESULTADO FINAL
# =========================================================

print()
print("==========================================")

print(
    "PROCESO TERMINADO"
)

print(
    "Registros escritos en Excel:",
    total_actualizados
)

print()
print(
    "Archivo generado:"
)

print(
    ARCHIVO_SALIDA
)

print("==========================================")

input(
    "\nPresiona Enter para cerrar..."
)