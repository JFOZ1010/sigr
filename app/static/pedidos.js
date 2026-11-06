// "Tiempo real": consulta los pedidos activos cada 5 s y redibuja la tabla.
const SIGUIENTE = {
  pendiente: "en_preparacion",
  en_preparacion: "listo",
  listo: "entregado",
  entregado: "pagado",
};

function formatoCop(n) {
  return "$" + Math.round(n).toLocaleString("es-CO");
}

function filaHTML(p) {
  const sig = SIGUIENTE[p.estado];
  return `<tr>
    <td>${p.id}</td><td>${p.mesa}</td>
    <td><span class="badge bg-warning text-dark">${p.estado}</span></td>
    <td>${formatoCop(p.total)}</td>
    <td><form method="post" action="/pedidos/${p.id}/estado">
      <input type="hidden" name="estado" value="${sig}">
      <button class="btn btn-sm btn-outline-success">→ ${sig}</button>
    </form></td></tr>`;
}

async function refrescar() {
  try {
    const resp = await fetch("/pedidos/api/activos");
    if (!resp.ok) return;
    const pedidos = await resp.json();
    document.getElementById("tabla-pedidos").innerHTML = pedidos.length
      ? pedidos.map(filaHTML).join("")
      : '<tr><td colspan="5" class="text-muted">No hay pedidos activos.</td></tr>';
  } catch (e) {
    // sin red: se reintenta en el siguiente ciclo
  }
}

setInterval(refrescar, 5000);
