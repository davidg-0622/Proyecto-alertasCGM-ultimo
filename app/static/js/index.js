// 1. Cálculo de cantidad
function calcularCantidad() {
    const inicial = parseInt(document.getElementById('Instancia_Inicial').value) || 0;
    const final = parseInt(document.getElementById('Instancia_Final').value) || 0;
    let total = (final >= inicial && inicial > 0) ? (final - inicial) + 1 : 0;
    document.getElementById('cantidad').value = total;
}

// 2. Selección desde la tabla
function seleccionarJob(nombre, subsistema) {
    document.getElementById('proceso').value = nombre;
    document.getElementById('subsistema_val').value = subsistema;
    const procesoInput = document.getElementById('proceso');
    procesoInput.style.backgroundColor = '#d4edda';
    setTimeout(() => procesoInput.style.backgroundColor = '', 500);
}

// 3. Buscador AJAX
function actualizarTabla(pagina) {
    const filtro = document.getElementById('inputFiltro').value;
    const url = `/jobs/listar?page=${pagina}&filtro=${encodeURIComponent(filtro)}`;

    fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');

            const nuevaTabla = doc.getElementById('contenedor-tabla');
            const nuevoConteo = doc.getElementById('conteo-filtro');
            const nuevoTotal = doc.getElementById('total-base-card');

            if (nuevaTabla) document.getElementById('contenedor-tabla').innerHTML = nuevaTabla.innerHTML;
            if (nuevoConteo) document.getElementById('conteo-filtro').innerHTML = nuevoConteo.innerHTML;
            if (nuevoTotal) document.getElementById('total-base-card').innerHTML = nuevoTotal.innerHTML;
        })
        .catch(err => console.error("Error al actualizar:", err));
}

function limpiarBusqueda() {
    document.getElementById('inputFiltro').value = '';
    actualizarTabla(1);
}

// 4. Envío de Acciones (Eliminar/Editar)
async function enviarAccion(tipo) {
    const resDiv = document.getElementById('resultado');
    
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

    let url = tipo === 'eliminar' ? '/jobs/eliminar-pasos' : 
              tipo === 'editar' ? '/jobs/editar-pasos' : '/jobs/test-pasos';
    
    resDiv.innerText = "⌛ Ejecutando en iSeries... Valide la ventana emergente.";
    resDiv.className = "mt-3 small text-center text-primary fw-bold";

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await response.json();
        resDiv.innerText = data.message;
        resDiv.className = data.ok ? "mt-3 small text-center text-success fw-bold" : "mt-3 small text-center text-danger";
    } catch (e) {
        resDiv.innerText = "Error de comunicación.";
        resDiv.className = "mt-3 small text-center text-warning";
    }
}

// 5. Inicialización de eventos
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('Instancia_Inicial')?.addEventListener('input', calcularCantidad);
    document.getElementById('Instancia_Final')?.addEventListener('input', calcularCantidad);
});
