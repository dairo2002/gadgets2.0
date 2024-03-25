from tienda.models import Producto

class Cart:
    def __init__(self, request):
        self.session = request.session        
        cart = self.session.get("session_key")        
        if "session_key" not in request.session:
            cart = self.session["session_key"] = {}    
        self.cart = cart
    
    def add(self, producto, cantidad):
        producto_id = str(producto.id)
        producto_cantidad = int(cantidad)
        if producto_id in self.cart:
            self.cart[producto_id] += producto_cantidad
        else:
            self.cart[producto_id] = producto_cantidad
        self.session.modified = True
    
    
    def __len__(self):
        return len(self.cart)

    def obtener_producto(self):
        items = []  
        total  = 0 
        subtotal = 0
        subTotalFormato = 0
        totalFormato = 0
        
        for prod_id, cantidad in self.cart.items():
            producto = Producto.objects.get(id=int(prod_id))  
            if producto.aplicar_descuento():                                  
                subtotal = producto.aplicar_descuento() * cantidad
                total += subtotal
            else:
                subtotal = producto.precio * cantidad
                total += subtotal

            totalFormato = "{:,.0f}".format(total).replace(",", ".")
            subTotalFormato = "{:,.0f}".format(subtotal).replace(",", ".")
            items.append({
                "producto":producto,
                "cantidad":cantidad,
                'subtotal':subTotalFormato
            })  
        return items, totalFormato
 

    def update_quantities(self, producto_id, cantidad):                
        self.cart[str(producto_id)] = int(cantidad)                        
        self.session.modified = True
    
    # def update_quantities(self, producto_id, cantidad):
    #     for producto_id, cantidad in cantidad.items():
    #         if str(producto_id) in self.cart:
    #             self.cart[str(producto_id)] = int(cantidad)                
        
    #     self.session.modified = True

    #    def obtener_producto(self):
    #     producto_ids = self.cart.keys()    
    #     producto = Producto.objects.filter(id__in=producto_ids)   
    #     prod_cantidad = []
    #     for prod in producto:
    #         cantidad = self.cart[str(prod.pk)]
    #         prod.cantidad = cantidad
    #         prod_cantidad.append(prod)
    #     return prod_cantidad



    def update(self, producto, cantidad):
        producto_id = str(producto)
        cantidad = int(cantidad)
        if producto_id in self.cart:
            self.cart[producto_id] = cantidad
        else:
            pass
            # self.add(producto, cantidad)
        self.session.modified = True
            

    def obtener_cantidad(self):
        cantidad_pro = self.cart
        return cantidad_pro


    def delete(self, producto):
        producto_id = str(producto)        
        if producto_id in self.cart:
            del self.cart[producto_id]
        self.session.modified = True
