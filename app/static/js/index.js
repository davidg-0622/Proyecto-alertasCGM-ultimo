let controller;

// 1. Cálculo de Cantidad (Optimizado)
function actualizarCantidad() {
    const ini = parseInt(document.getElementById('Instancia_Inicial').value) || 0;
    const fin = parseInt(document.getElementById('Instancia_Final').value) || 0;
    const cantInput = document.getElementById('cantidad');
    const total = (fin - ini) + 1;
    cantInput.value = (ini > 0 && fin >= ini) ? total : 0;
}

// 2. Escuchas de eventos (Asegúrate de que estos IDs existan en el HTML)
document.getElementById('Instancia_Inicial')?.addEventListener('input', actualizarCantidad);
document.getElementById('Instancia_Final')?.addEventListener('input', actualizarCantidad);

// 3. Función para Buscar y Paginación (CORREGIDA PARA ARCHIVO EXTERNO)
function actualizarTabla(pagina) {
    const filtroInput = document.getElementById('inputFiltro');
    const filtro = filtroInput ? filtroInput.value : '';
    
    // CAMBIO CLAVE: Usamos la ruta manual porque url_for no funciona en archivos .js externos
    const url = `/jobs/listar?page=${pagina}&filtro=${encodeURIComponent(filtro)}`;

    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            
            // Actualizamos la tabla
            const tabla = doc.getElementById('contenedor-tabla');
            if (tabla) document.getElementById('contenedor-tabla').innerHTML = tabla.innerHTML;
            
            // Actualizamos los Cards de indicadores
            const conteo = doc.getElementById('conteo-filtro');
            if (conteo) document.getElementById('conteo-filtro').innerHTML = conteo.innerHTML;
            
            const totalBase = doc.getElementById('total-base-card');
            if (totalBase) document.getElementById('total-base-card').innerHTML = totalBase.innerHTML;
        })
        .catch(err => console.error("Error en búsqueda:", err));
}

// 4. Limpiar Búsqueda
function limpiarBusqueda() {
    const input = document.getElementById('inputFiltro');
    if (input) input.value = '';
    actualizarTabla(1);
}

// 5. Cargar datos de la tabla al formulario (Nueva para completar tu flujo)
function seleccionarJob(nombre, subsistema) {
    document.getElementById('proceso').value = nombre;
    document.getElementById('subsistema_val').value = subsistema;
}

// 6. Enviar Acciones (Tu lógica de fetch actual)
async function enviarAccion(tipo) {
    const resDiv = document.getElementById('resultado');
    const btnStop = document.getElementById('btnStop');
    
    const payload = {
        instancia_inicial: document.getElementById('Instancia_Inicial').value,
        instancia_final: document.getElementById('Instancia_Final').value,
        equipo: document.getElementById('equipo').value,
        subsistema: document.getElementById('subsistema_val').value,
        proceso: document.getElementById('proceso').value,
        descripcion: document.getElementById('descripcion').value
    };

    if(!payload.instancia_inicial || !payload.instancia_final) {
        resDiv.innerText = "Por favor completa los datos del formulario.";
        resDiv.className = "mt-3 small text-center text-danger";
        return;
    }

    // --- NUEVA LÓGICA DE CONFIRMACIÓN EN EL NAVEGADOR ---
    if (tipo === 'eliminar') {
        const confirmar = confirm(`¿Estás seguro de ELIMINAR las instancias desde la ${payload.instancia_inicial} hasta la ${payload.instancia_final}?`);
        if (!confirmar) return; // Se detiene aquí si el usuario cancela
    }
    
    if (tipo === 'editar') {
        const confirmar = confirm(`¿Deseas EDITAR las instancias seleccionadas?`);
        if (!confirmar) return;
    }

    let url = '/jobs/test-pasos'; 
    let mensajeEspera = "Procesando...";

    if (tipo === 'eliminar') {
        url = '/jobs/eliminar-pasos';
        mensajeEspera = "⌛ Ejecutando eliminación en iSeries...";
    } else if (tipo === 'editar') {
        url = '/jobs/editar-pasos';
        mensajeEspera = "⌛ Ejecutando edición en iSeries...";
    }

    resDiv.innerText = mensajeEspera;
    resDiv.className = "mt-3 small text-center text-primary fw-bold";
    
    controller = new AbortController();
    btnStop.disabled = false;
    btnStop.classList.replace('btn-secondary', 'btn-dark');

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload),
            signal: controller.signal 
        });
        const data = await response.json();
        resDiv.innerText = data.message;
        resDiv.className = data.ok ? "mt-3 small text-center text-success fw-bold" : "mt-3 small text-center text-danger";
    } catch (e) {
        if (e.name === 'AbortError') {
            resDiv.innerText = "Ejecución detenida por el usuario.";
            resDiv.className = "mt-3 small text-center text-warning fw-bold";
        } else {
            resDiv.innerText = "Error de comunicación con el servidor";
            resDiv.className = "mt-3 small text-center text-danger";
        }
    } finally {
        btnStop.disabled = true;
        btnStop.classList.replace('btn-dark', 'btn-secondary');
    }
}

async function detenerEjecucion() {
    try {
        await fetch('/jobs/detener', { method: 'POST' });
    } catch (err) {
        console.error("No se pudo contactar al servidor.");
    }
    if (controller) controller.abort(); 
}
