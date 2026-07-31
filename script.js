const boton = document.getElementById("btnEnviar");

boton.addEventListener("click", () => {

    const temperatura = Number(document.getElementById("temperatura").value);
    const humedad = Number(document.getElementById("humedad").value);
    const porcentajeL = Number(document.getElementById("porcentajeL").value);


    // ===============================
    // VALIDAR CAMPOS
    // ===============================

    if (
        document.getElementById("temperatura").value === "" ||
        document.getElementById("humedad").value === "" ||
        document.getElementById("porcentajeL").value === ""
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
    // GUARDAR EN FIREBASE
    // ===============================

    const ahora = new Date();

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