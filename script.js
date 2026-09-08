// ===============================
// OBTENER ID DESDE EL QR
// ===============================

const parametros = new URLSearchParams(window.location.search);
const idMaquina = parametros.get("id");

console.log("URL:", window.location.href);
console.log("Parámetro ID:", idMaquina);

const campo = document.getElementById("idMaquina");

console.log("Campo encontrado:", campo);

campo.textContent = idMaquina || "Sin ID";

console.log("Valor final:", campo.textContent);


// ===============================
// FIREBASE
// ===============================

import {
    initializeApp
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";

import {
    getDatabase,
    ref,
    push,
    set,
    get
} from "https://www.gstatic.com/firebasejs/10.12.2/firebase-database.js";


const firebaseConfig = {
    apiKey: "AIzaSyDlO56Q3zGl6l_mwmBw5cAK4cwRwgnFzdU",
    authDomain: "piloto-614ca.firebaseapp.com",
    databaseURL: "https://piloto-614ca-default-rtdb.firebaseio.com",
    projectId: "piloto-614ca",
    storageBucket: "piloto-614ca.firebasestorage.app",
    messagingSenderId: "617118308517",
    appId: "1:617118308517:web:1e6465cd22cdf7022f954c"
};


const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

console.log("Firebase conectado correctamente");


// ===============================
// ELEMENTOS
// ===============================

const boton = document.getElementById("btnEnviar");

const botonHistorial =
    document.getElementById("btnHistorial");

const historial =
    document.getElementById("historial");

const listaHistorial =
    document.getElementById("listaHistorial");

const temperaturaInput =
    document.getElementById("temperatura");

const humedadInput =
    document.getElementById("humedad");

const porcentajeLInput =
    document.getElementById("porcentajeL");


// ===============================
// MENSAJE DE CONFIRMACIÓN
// ===============================

function mostrarMensaje(mensaje) {

    const mensajeAnterior =
        document.getElementById("mensajeExito");

    if (mensajeAnterior) {
        mensajeAnterior.remove();
    }


    const mensajeExito =
        document.createElement("div");

    mensajeExito.id = "mensajeExito";

    mensajeExito.innerHTML = `
        <span>✓</span>
        ${mensaje}
    `;


    boton.parentNode.insertBefore(
        mensajeExito,
        boton
    );


    setTimeout(() => {

        mensajeExito.style.opacity = "0";

        setTimeout(() => {

            mensajeExito.remove();

        }, 300);

    }, 2500);

}


// ===============================
// MOSTRAR HISTORIAL
// ===============================

async function cargarHistorial() {

    if (!idMaquina) {

        listaHistorial.innerHTML = `
            <p class="sin-registros">
                No hay ID de máquina.
            </p>
        `;

        return;

    }


    // Mostrar mensaje de carga

    listaHistorial.innerHTML = `
        <p class="cargando">
            ⏳ Cargando historial...
        </p>
    `;


    // ===============================
    // REFERENCIA FIREBASE
    // ===============================

    const registrosRef = ref(
        database,
        "maquinas/" + idMaquina + "/registros"
    );


    try {

        console.log(
            "Buscando registros de:",
            idMaquina
        );


        const snapshot =
            await get(registrosRef);


        // ===============================
        // NO HAY REGISTROS
        // ===============================

        if (!snapshot.exists()) {

            listaHistorial.innerHTML = `
                <p class="sin-registros">
                    No hay registros para ${idMaquina}.
                </p>
            `;

            return;

        }


        // ===============================
        // OBTENER DATOS
        // ===============================

        const datos = snapshot.val();

        console.log(
            "Registros encontrados:",
            datos
        );


        // Convertir objeto a arreglo

        const registros =
            Object.values(datos);


        // Los últimos registros primero

        registros.reverse();


        // Solo los últimos 5

        const ultimosRegistros =
            registros.slice(0, 5);


        // Limpiar historial

        listaHistorial.innerHTML = "";


        // ===============================
        // CREAR TARJETAS
        // ===============================

        ultimosRegistros.forEach((registro) => {

            const tarjeta =
                document.createElement("div");

            tarjeta.className = "registro";


            const porcentajeL =
                registro.porcentajeL ??
                registro.luminosidad ??
                "-";


            tarjeta.innerHTML = `

                <div class="registro-header">

                    <span>
                         ${registro.fecha || "-"}
                    </span>

                    <span>
                         ${registro.hora || "-"}
                    </span>

                </div>


                <div class="registro-body">


                    <div class="fila">

                        <strong>
                            🌡 Temperatura
                        </strong>

                        <span>
                            ${registro.temperatura ?? "-"} °C
                        </span>

                    </div>


                    <div class="fila">

                        <strong>
                             Humedad
                        </strong>

                        <span>
                            ${registro.humedad ?? "-"} %
                        </span>

                    </div>


                    <div class="fila">

                        <strong>
                             %L
                        </strong>

                        <span>
                            ${porcentajeL} %
                        </span>

                    </div>


                </div>

            `;


            listaHistorial.appendChild(tarjeta);

        });


    } catch (error) {

        console.error(
            "Error al cargar historial:",
            error
        );


        listaHistorial.innerHTML = `
            <p class="sin-registros">
                Error al cargar el historial.
            </p>
        `;

    }

}


// ===============================
// BOTÓN ENVIAR
// ===============================

boton.addEventListener("click", async () => {

    const temperatura =
        Number(temperaturaInput.value);

    const humedad =
        Number(humedadInput.value);

    const porcentajeL =
        Number(porcentajeLInput.value);



    // ===============================
    // VALIDAR CAMPOS VACÍOS
    // ===============================

    if (
        temperaturaInput.value === "" ||
        humedadInput.value === "" ||
        porcentajeLInput.value === ""
    ) {

        alert("Completa todos los campos");
        return;

    }


    // ===============================
    // VALIDAR TEMPERATURA
    // ===============================

    if (
        temperatura < -50 ||
        temperatura > 150
    ) {

        alert("La temperatura debe estar entre -50 °C y 150 °C");
        return;

    }


    // ===============================
    // VALIDAR HUMEDAD
    // ===============================

    if (
        humedad < 0 ||
        humedad > 100
    ) {

        alert("La humedad debe estar entre 0 % y 100 %");
        return;

    }


    // ===============================
    // VALIDAR %L
    // ===============================

    if (
        porcentajeL < 0 ||
        porcentajeL > 100
    ) {

        alert("%L debe estar entre 0 % y 100 %");
        return;

    }


    // ===============================
    // VALIDAR ID
    // ===============================

    if (!idMaquina) {

        alert("No hay ID de máquina");

        return;

    }


    // ===============================
    // CREAR REGISTRO
    // ===============================

    const registro = push(
        ref(
            database,
            "maquinas/" + idMaquina + "/registros"
        )
    );


    // ===============================
    // FECHA Y HORA
    // ===============================

    const ahora = new Date();


    try {

        // ===============================
        // GUARDAR EN FIREBASE
        // ===============================

        await set(registro, {

            idMaquina: idMaquina,

            temperatura: temperatura,

            humedad: humedad,

            porcentajeL: porcentajeL,

            fecha: ahora.toLocaleDateString("es-MX"),

            hora: ahora.toLocaleTimeString("es-MX")

        });


        console.log("Datos guardados correctamente");


        // ===============================
        // LIMPIAR CAMPOS
        // ===============================

        temperaturaInput.value = "";

        humedadInput.value = "";

        porcentajeLInput.value = "";


        // ===============================
        // MENSAJE BONITO
        // ===============================

        mostrarMensaje(
            "Datos enviados correctamente"
        );


        // ===============================
        // ACTUALIZAR HISTORIAL
        // ===============================

        if (
            historial.style.display === "block"
        ) {

            await cargarHistorial();

        }


        // Regresar al primer campo

        temperaturaInput.focus();


    } catch (error) {

        console.error(
            "Error:",
            error
        );


        alert(
            "Error al enviar los datos"
        );

    }

});


// ===============================
// BOTÓN VER HISTORIAL
// ===============================

botonHistorial.addEventListener(
    "click",
    async () => {

        console.log(
            "Botón historial presionado"
        );


        // Mostrar sección

        historial.style.display =
            "block";


        // Cargar historial

        await cargarHistorial();

    }
);


// ===============================
// ENTER ENTRE CAMPOS
// ===============================

temperaturaInput.addEventListener(
    "keydown",
    (event) => {

        if (event.key === "Enter") {

            event.preventDefault();

            humedadInput.focus();

        }

    }
);


humedadInput.addEventListener(
    "keydown",
    (event) => {

        if (event.key === "Enter") {

            event.preventDefault();

            porcentajeLInput.focus();

        }

    }
);


porcentajeLInput.addEventListener(
    "keydown",
    (event) => {

        if (event.key === "Enter") {

            event.preventDefault();

            boton.click();

        }

    }
);