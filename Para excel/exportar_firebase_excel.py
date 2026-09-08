import urllib.request
import json
import os
import shutil
from datetime import datetime, timedelta
from openpyxl import load_workbook


# =========================================================
# CONFIGURACIÓN
# =========================================================

URL_FIREBASE = "https://piloto-614ca-default-rtdb.firebaseio.com/maquinas.json"

ARCHIVO_PLANTILLA = "Control_Maquinas_Semanal.xlsx"

ARCHIVO_PRUEBA_ANTERIOR = "Control_Maquinas_Semanal_actualizado.xlsx"

ARCHIVO_HISTORICO = "Control_Maquinas_Historico.xlsx"


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

columnas_dias = {
    0: 2,   # Lunes
    1: 5,   # Martes
    2: 8,   # Miércoles
    3: 11,  # Jueves
    4: 14,  # Viernes
    5: 17,  # Sábado
    6: 20   # Domingo
}


# =========================================================
# CONVERTIR FECHA Y HORA
# =========================================================

def convertir_fecha_hora(registro):

    fecha_texto = registro.get("fecha", "")
    hora_texto = registro.get("hora", "")

    if not fecha_texto:
        return None

    fecha = None

    # Fecha normal
    formatos = [
        "%d/%m/%Y",
        "%d/%m/%y"
    ]

    for formato in formatos:

        try:

            fecha = datetime.strptime(
                fecha_texto,
                formato
            )

            break

        except ValueError:
            pass


    # Fecha ISO antigua
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


    # Si no hay hora
    if not hora_texto:
        return fecha


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


    # Hora AM / PM
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


    # Hora 24 horas
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
# NOMBRE DE UNA SEMANA
# =========================================================

def nombre_semana(inicio, fin):

    meses = [
        "Ene",
        "Feb",
        "Mar",
        "Abr",
        "May",
        "Jun",
        "Jul",
        "Ago",
        "Sep",
        "Oct",
        "Nov",
        "Dic"
    ]

    mes_inicio = meses[
        inicio.month - 1
    ]

    mes_fin = meses[
        fin.month - 1
    ]


    if inicio.month == fin.month:

        return (
            f"{inicio.day:02d}-"
            f"{fin.day:02d} "
            f"{mes_inicio}"
        )

    return (
        f"{inicio.day:02d} "
        f"{mes_inicio}-"
        f"{fin.day:02d} "
        f"{mes_fin}"
    )


# =========================================================
# OBTENER SEMANA ACTUAL
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

nombre_hoja_actual = nombre_semana(
    inicio_semana,
    fin_semana
)


# =========================================================
# SEMANA ANTERIOR
# =========================================================

inicio_semana_anterior = (
    inicio_semana - timedelta(days=7)
)

fin_semana_anterior = (
    inicio_semana - timedelta(
        seconds=1
    )
)

nombre_hoja_anterior = nombre_semana(
    inicio_semana_anterior,
    fin_semana_anterior
)


# =========================================================
# ENCABEZADO
# =========================================================

print()
print("==========================================")
print("   EXPORTADOR FIREBASE -> EXCEL")
print("==========================================")
print()

print(
    "Semana actual:",
    inicio_semana.strftime("%d/%m/%Y"),
    "-",
    fin_semana.strftime("%d/%m/%Y")
)

print(
    "Hoja actual:",
    nombre_hoja_actual
)


# =========================================================
# CONECTAR FIREBASE
# =========================================================

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


print(
    "Firebase conectado correctamente."
)


# =========================================================
# CREAR HISTÓRICO SI NO EXISTE
# =========================================================

if not os.path.exists(
    ARCHIVO_HISTORICO
):

    print()
    print(
        "Creando archivo histórico..."
    )

    shutil.copy2(
        ARCHIVO_PLANTILLA,
        ARCHIVO_HISTORICO
    )


# =========================================================
# ABRIR HISTÓRICO
# =========================================================

try:

    wb = load_workbook(
        ARCHIVO_HISTORICO
    )

except Exception as error:

    print()
    print(
        "ERROR al abrir el histórico:"
    )

    print(error)

    input("\nPresiona Enter para cerrar...")
    exit()


# =========================================================
# RECUPERAR SEMANA ANTERIOR DE LA PRUEBA
# =========================================================
#
# Esto se ejecuta solamente si:
#
# - existe Control_Maquinas_Semanal_actualizado.xlsx
# - todavía no existe la hoja anterior
#
# Así recuperamos nuestra prueba 03-09 Ago.
# =========================================================

if (
    os.path.exists(ARCHIVO_PRUEBA_ANTERIOR)
    and
    nombre_hoja_anterior not in wb.sheetnames
):

    print()
    print(
        "Se encontró el Excel de prueba anterior."
    )

    print(
        "Recuperando semana:",
        nombre_hoja_anterior
    )


    try:

        wb_prueba = load_workbook(
            ARCHIVO_PRUEBA_ANTERIOR
        )

        ws_prueba = wb_prueba.active


        # Crear hoja copiando la plantilla
        if wb.sheetnames:

            hoja_base = wb[
                wb.sheetnames[0]
            ]

            ws_anterior = wb.copy_worksheet(
                hoja_base
            )

            ws_anterior.title = (
                nombre_hoja_anterior
            )


            # Copiar valores de la prueba
            for fila in range(
                1,
                ws_prueba.max_row + 1
            ):

                for columna in range(
                    1,
                    ws_prueba.max_column + 1
                ):

                    origen = ws_prueba.cell(
                        fila,
                        columna
                    )

                    destino = ws_anterior.cell(
                        fila,
                        columna
                    )

                    destino.value = origen.value


            print(
                "Semana anterior recuperada correctamente."
            )

    except Exception as error:

        print(
            "No se pudo recuperar la semana anterior:"
        )

        print(error)


# =========================================================
# CREAR / OBTENER HOJA ACTUAL
# =========================================================

if nombre_hoja_actual in wb.sheetnames:

    print()
    print(
        "La hoja actual ya existe."
    )

    print(
        "Se actualizará."
    )

    ws = wb[
        nombre_hoja_actual
    ]

else:

    print()
    print(
        "Creando hoja:",
        nombre_hoja_actual
    )


    hoja_base = wb[
        wb.sheetnames[0]
    ]

    ws = wb.copy_worksheet(
        hoja_base
    )

    ws.title = nombre_hoja_actual


# =========================================================
# BUSCAR MÁQUINAS EN EXCEL
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
# CONTADOR
# =========================================================

total_actualizados = 0


# =========================================================
# RECORRER FIREBASE
# =========================================================

for id_maquina, informacion in datos_firebase.items():

    print()
    print("------------------------------------------")
    print(
        "Máquina:",
        id_maquina
    )
    print("------------------------------------------")


    # Máquina no existente en Excel
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
    # ÚLTIMO REGISTRO DE CADA DÍA
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

            continue


        # Solo semana actual
        if fecha_hora < inicio_semana:
            continue

        if fecha_hora > fin_semana:
            continue


        dia_semana = fecha_hora.weekday()


        anterior = registros_por_dia.get(
            dia_semana
        )


        if (
            anterior is None
            or
            fecha_hora > anterior[0]
        ):

            registros_por_dia[
                dia_semana
            ] = (
                fecha_hora,
                registro
            )


    # =====================================================
    # NO HAY REGISTROS ESTA SEMANA
    # =====================================================

    if not registros_por_dia:

        print(
            "  No tiene registros de esta semana."
        )

        continue


    # =====================================================
    # ESCRIBIR
    # =====================================================

    fila_excel = filas_maquinas[
        id_maquina
    ]


    for dia_semana, datos in registros_por_dia.items():

        fecha_hora = datos[0]

        registro = datos[1]


        columna = columnas_dias[
            dia_semana
        ]


        nombre_dia = dias[
            dia_semana
        ]


        temperatura = registro.get(
            "temperatura",
            ""
        )


        humedad = registro.get(
            "humedad",
            ""
        )


        porcentajeL = registro.get(
            "porcentajeL"
        )


        # Compatibilidad con datos antiguos
        if porcentajeL is None:

            porcentajeL = registro.get(
                "luminosidad",
                ""
            )


        # Escribir
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


        print()

        print(
            "  Día:",
            nombre_dia
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
# GUARDAR
# =========================================================

try:

    wb.save(
        ARCHIVO_HISTORICO
    )

except PermissionError:

    print()
    print(
        "ERROR: el Excel está abierto."
    )

    print(
        "Cierra Control_Maquinas_Historico.xlsx"
    )

    input("\nPresiona Enter para cerrar...")
    exit()

except Exception as error:

    print()
    print(
        "ERROR al guardar:"
    )

    print(error)

    input("\nPresiona Enter para cerrar...")
    exit()


# =========================================================
# RESULTADO
# =========================================================

print()
print("==========================================")
print("PROCESO TERMINADO")
print("==========================================")

print(
    "Hoja actual:",
    nombre_hoja_actual
)

print(
    "Registros escritos:",
    total_actualizados
)

print()
print(
    "Archivo:",
    ARCHIVO_HISTORICO
)

print("==========================================")

input(
    "\nPresiona Enter para cerrar..."
)