
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



//** peticon filtron de departamentos a municipios */
document.addEventListener('DOMContentLoaded', function () {
    document.getElementById('selectDepartamento').addEventListener('change', function () {
        var codigo_departamento = this.value
        var selectMunicipio = document.getElementById('selectMunicipio')
        selectMunicipio.disabled = true // Deshabilita el select

        // '?' se utiliza pra enviar datos al servidor, GET con un parametro
        // parametro: codigo_departamento = request.GET.get("codigo_departamento")  
        // + codigo_departamento, se llama la variable declarada y se concatena con el valor 

        fetch('/pedido/regiones/?codigo_departamento=' + codigo_departamento)
            .then((response) => response.json())
            .then((data) => {
                selectMunicipio.innerHTML = '' // Vacía el select de municipios
                data.municipios.forEach(function (municipio) {
                    selectMunicipio.innerHTML += '<option value="' + municipio.codigo + '">' + municipio.nombre + '</option>'
                })
                selectMunicipio.disabled = false
            })
            .catch((error) => {
                selectMunicipio.innerHTML = '<option value="">Error al cargar</option>'
                console.error('Error:', error)
            })
    })
})