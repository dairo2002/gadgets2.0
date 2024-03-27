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
        id: producto_id,
        // cantidad: cantidad
    }

    fetch("/carrito/agregar_carrito/", {
        method: "POST",
        headers: {"Content-Type": "application/json", "X-CSRFToken": csrftoken},
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Contador de producto
        // document.getElementById("contador").innerHTML = data
        console.log(data);
    })
    .catch(error => {
        console.log(error);
    })

}


