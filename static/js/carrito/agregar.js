function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Creamos el csrftoken para cookie
const csrftoken = getCookie('csrftoken');

// let btn = document.getElementById("btnAgregarCarrito")
// btn.addEventListener('click', agregarCarrito)

let btn = document.querySelectorAll(".contaninerProductos button")
btn.forEach(bt => {
    bt.addEventListener('click', agregarCarrito)
})

function agregarCarrito(e) {
    // e = asigna el evento DOM a la variable con el valor 
    let producto_id = e.target.value
    let data = {
        id: producto_id
        // cantidad: cantidad
    }

    fetch("/carrito/agregar_carrito/", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            if (data.redirect) {
                window.localtion.href = data.redirect;
            }
            // Contador de producto
            // document.getElementById("contador").innerHTML = data
            //console.log(data);
        })
        .catch(error => {
            //console.log(error);
        })

}

document.addEventListener("DOMContentLoaded", function() {
    // Selecciona todos los botones de eliminar y agrega un evento de clic a cada uno
    const eliminarBotones = document.querySelectorAll(".deleteProductCart");
    eliminarBotones.forEach(btn => {
        btn.addEventListener("click", function() {
            // Obtén el ID del producto del atributo data-producto-id del elemento padre
            const productoID = btn.value;
            eliminarProductoDelCarrito(productoID);
        });
    });
});

// deleteProductCart

// let btnEliminar = document.getElementById("deleteProductCart")
// btn.addEventListener('click', eliminarProductoDelCarrito)


function eliminarProductoDelCarrito(producto_id) {
    // Crear el objeto de datos que se enviará en la solicitud    
    const data = { id: producto_id };

    // Realizar la solicitud Fetch para eliminar el producto del carrito
    fetch("/carrito/eliminar_carrito/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrftoken
        },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
        })
        .catch(error => {
            // Capturar y manejar errores de la solicitud Fetch
            console.error("Error:", error);
        });
}
