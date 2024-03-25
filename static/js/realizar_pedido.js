// Funcion ocultar boton 
function mostrarDireccionLocal() {
    var txtDireccionLocal = document.getElementById('txtDireccionLocal')
    txtDireccionLocal.style.display = 'block'
}

document.querySelectorAll('input[name="metodo_pago"]').forEach(function (radio) {
    radio.addEventListener('change', function () {
        // Ocultar todos los contenidos        
        document.getElementById('infoEfectivo').style.display = 'none';
        document.getElementById('infoNequi').style.display = 'none';

        // Mostrar el contenido correspondiente a la opción seleccionada
        if (this.value === 'efectivo') {
            document.getElementById('infoEfectivo').style.display = 'block';
        } else if (this.value === 'nequi') {
            document.getElementById('infoNequi').style.display = 'block';
        }
    });
});
