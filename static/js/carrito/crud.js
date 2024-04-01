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



/*document.addEventListener("DOMContentLoaded", function () {
    const carritoContainer = document.getElementById("carrito-container");

    // Si el elemento existe, continúa con la lógica para mostrar el carrito
    if (carritoContainer) {
        fetch("/carrito/")
            .then(response => response.json())
            .then(data => {
                let html = ''
                data.articulo_carrito.forEach(element => {
                    html += `                    
                    <tr>
                      <td class="align-middle text-center">
                        <img src="${element.imagen}" class="img-fluid" alt="imagen carrito" style="max-width: 100px; max-height: 100px;" />
                      </td>
                      <td class="align-middle" style="min-width: 180px;">${articulo.producto}</td>
                      <td class="align-middle text-center" style="min-width: 100px;">
                        <input type="number" min="0" data-product-id="{{ articulo.producto.id }}" value="${articulo.cantidad}" class="text-center form-control form-control-sm inputCantidadCarrito bg-light quantity-input" />
                      </td>
                      <td class="align-middle text-center" style="min-width: 150px;">
                        {% if articulo.producto.categoria.descuento %}
                          <p class="mb-0">$ {{ articulo.subtotal }}</p>
                          <del class="text-muted">
                            <small class="text-muted">$ {{ articulo.producto.descuentoFormatiado }}</small>
                          </del>
                        {% else %}
                          <p class="mb-0">$ {{ articulo.subtotal }}</p>
                          <small class="mb-0 text-muted">$ {{ articulo.producto.precioFormatiado }}</small>
                        {% endif %}
                      </td>
                      <td class="align-middle text-center" width="90px">
                        <div class="">
                          <button class="btn p-1 border border-0 deleteProductCart" value="{{ articulo.producto.id }}"><i class="fa-solid fa-xmark fa-xl"></i></button>
                        </div>
                      </td>
                    </tr>`
                });

                carritoContainer.innerHTML = html;
            })
            .catch(error => {
                console.error("Error:", error);
            });
    } else {
        console.error("El elemento 'carrito-container' no existe en el DOM.");
    }
});
*/

/*<table class="table">
<tbody>
  {% for articulo in articulo_carrito %}
    <tr>
      <td class="align-middle text-center">
        <img src="{{ articulo.producto.imagen.url }}" class="img-fluid" alt="imagen carrito" style="max-width: 100px; max-height: 100px;" />
      </td>
      <td class="align-middle" style="min-width: 180px;">{{ articulo.producto.nombre }}</td>
      <td class="align-middle text-center" style="min-width: 100px;">
        <input type="number" min="0" data-product-id="{{ articulo.producto.id }}" value="{{ articulo.cantidad }}" class="text-center form-control form-control-sm inputCantidadCarrito bg-light quantity-input" />
      </td>
      <td class="align-middle text-center" style="min-width: 150px;">
        {% if articulo.producto.categoria.descuento %}
          <p class="mb-0">$ {{ articulo.subtotal }}</p>
          <del class="text-muted">
            <small class="text-muted">$ {{ articulo.producto.descuentoFormatiado }}</small>
          </del>
        {% else %}
          <p class="mb-0">$ {{ articulo.subtotal }}</p>
          <small class="mb-0 text-muted">$ {{ articulo.producto.precioFormatiado }}</small>
        {% endif %}
      </td>
      <td class="align-middle text-center" width="90px">
        <div class="">
          <button class="btn p-1 border border-0 deleteProductCart"  value="{{articulo.producto.id}}"> <i class="fa-solid fa-xmark fa-xl" ></i></button>
        </div>
      </td>
    </tr>
  {% endfor %}
</tbody>
</table>*/



let btn = document.querySelectorAll(".btnAgregarProducto")
btn.forEach(bt => {
    bt.addEventListener('click', agregarCarrito)
})

function agregarCarrito(e) {
    // e = asigna el evento DOM a la variable con el valor 
    let producto_id = e.target.value
    let data = {
        id: producto_id        
    }

    fetch("/carrito/agregar_carrito/", {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": csrftoken },
        body: JSON.stringify(data)
    })
        .then(response => response.json())
        .then(data => {
            window.location.href = data.redirect;
            //Contador de producto
            //document.getElementById("contador").innerHTML = data
            //console.log(data);
        })
        .catch(error => {
            console.log(error);
        })

}


document.addEventListener("DOMContentLoaded", function () {
    const btnActualizarTodo = document.getElementById("btnActualizarTodo");

    btnActualizarTodo.addEventListener("click", function () {
        const inputCantidades = document.querySelectorAll(".inputCantidadCarrito");

        inputCantidades.forEach(input => {
            const productoId = input.dataset.productId;
            const nuevaCantidad = input.value;

            actualizarCantidadEnCarrito(productoId, nuevaCantidad);
        });
    });

    function actualizarCantidadEnCarrito(productoId, nuevaCantidad) {
        const data = {
            id: productoId,
            cantidad: nuevaCantidad
        };

        fetch("/carrito/actualizar_carrito/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                window.location.href = data.redirect;
            })
            .catch(error => {
                console.error("Error al actualizar la cantidad:", error);
            });
    }



});


document.addEventListener("DOMContentLoaded", function () {
    const eliminarBotones = document.querySelectorAll(".deleteProductCart");
    eliminarBotones.forEach(btn => {
        btn.addEventListener("click", function () {
            const productoID = btn.value;
            eliminarProductoDelCarrito(productoID);
        });
    });
});


function eliminarProductoDelCarrito(producto_id) {
    const data = { id: producto_id };
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
            window.location.href = data.redirect;
        })
        .catch(error => {
            console.error("Error:", error);
        });
}
