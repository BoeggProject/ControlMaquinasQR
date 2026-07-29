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
import { getDatabase, ref, push, set } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-database.js";


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

    const temperatura = document.getElementById("temperatura").value;
    const humedad = document.getElementById("humedad").value;
    const luminosidad = document.getElementById("luminosidad").value;


    if (!idMaquina) {
        alert("No hay ID de máquina");
        return;
    }


    const registro = push(
        ref(database, "maquinas/" + idMaquina + "/registros")
    );


    set(registro, {
        temperatura: temperatura,
        humedad: humedad,
        luminosidad: luminosidad,
        fecha: new Date().toISOString()
    })
    .then(() => {
        alert("Datos enviados correctamente");
    })
    .catch((error) => {
        console.error("Error:", error);
        alert("Error al enviar datos");
    });

});