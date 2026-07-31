// ===============================
// OBTENER ID DESDE EL QR
// ===============================

const parametros = new URLSearchParams(window.location.search);
const idMaquina = parametros.get("id");

console.log("URL:", window.location.href);
console.log("Parámetro ID:", idMaquina);

const campo = document.getElementById("idMaquina");

console.log("Campo encontrado:", campo);

campo.value = idMaquina || "Sin ID";

console.log("Valor final:", campo.value);


// ===============================
// FIREBASE
// ===============================

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";

import {
    getDatabase,
    ref,
    push,
    set
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
// BOTÓN ENVIAR
// ===============================

const boton = document.getElementById("btnEnviar");

boton.addEventListener("click", () => {

    const temperaturaInput = document.getElementById("temperatura");
    const humedadInput = document.getElementById("humedad");
    const porcentajeLInput = document.getElementById("porcentajeL");


    const temperatura = Number(temperaturaInput.value);
    const humedad = Number(humedadInput.value);
    const porcentajeL = Number(porcentajeLInput.value);


    // ===============================
    // VALIDAR CAMPOS
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
        ref(database, "maquinas/" + idMaquina + "/registros")
    );


    // ===============================
    // FECHA Y HORA
    // ===============================

    const ahora = new Date();


    // ===============================
    // GUARDAR EN FIREBASE
    // ===============================

    set(registro, {

        idMaquina: idMaquina,

        temperatura: temperatura,

        humedad: humedad,

        porcentajeL: porcentajeL,

        fecha: ahora.toLocaleDateString("es-MX"),

        hora: ahora.toLocaleTimeString("es-MX")

    })

    .then(() => {

        alert("Datos enviados correctamente");

    })

    .catch((error) => {

        console.error("Error:", error);

        alert("Error al enviar datos");

    });

});