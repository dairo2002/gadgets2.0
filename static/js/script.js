// Tiempo cerrar alerta 
setTimeout(function () {
    let mensage_alerta = document.getElementById('messages')
    if (mensage_alerta) {
        mensage_alerta.style.transition = 'opacity 2s';
        mensage_alerta.style.opacity = '0';
        setTimeout(function () {
            mensage_alerta.style.display = 'none'
        }, 2000);

    }
}, 4000)