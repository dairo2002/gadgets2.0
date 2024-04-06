new DataTable('#tblAdmin', {
    layout: {
        topStart: {
            buttons: ['copy', 'excel', 'pdf', 'colvis']
        }
    },
    language: {
        "sProcessing": "Procesando...",
        "sLengthMenu": "Mostrar _MENU_ registros",
        "sZeroRecords": "No se encontraron resultados",
        "sEmptyTable": "Ningún dato disponible en esta tabla",
        "sInfo": "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
        "sInfoEmpty": "Mostrando registros del 0 al 0 de un total de 0 registros",
        "sInfoFiltered": "(filtrado de un total de _MAX_ registros)",
        "sInfoPostFix": "",
        "sSearch": "Buscar:",
        "sUrl": "",
        "sInfoThousands": ",",
        "sLoadingRecords": "Cargando...",
        "oPaginate": {
            "sFirst": "Primero",
            "sLast": "Último",
            "sNext": "Siguiente",
            "sPrevious": "Anterior"
        },
        "oAria": {
            "sSortAscending": ": Activar para ordenar la columna de manera ascendente",
            "sSortDescending": ": Activar para ordenar la columna de manera descendente"
        },
        "buttons": {
            "copy": "Copiar",
            "colvis": "Visibilidad"
        }
    }
});



/*$(document).ready(function() {
    $('#tblAdmin').DataTable({
        dom: "Bfrtip",
        buttons: [
            'excel',
            'pdf',
            'print'            
        ],
        language: {
             "decimal": ",",
             "thousands": ".",
             "sEmptyTable": "No hay datos disponibles en la tabla",
             "sInfo": "Mostrando _START_ a _END_ de _TOTAL_ entradas",
             "sInfoEmpty": "Mostrando 0 a 0 de 0 entradas",
             "sInfoFiltered": "(filtrado de _MAX_ entradas totales)",
             "sInfoPostFix": "",
             "sInfoThousands": ",",
             "sLengthMenu": "Mostrar _MENU_ entradas",
             "sLoadingRecords": "Cargando...",
             "sProcessing": "Procesando...",
             "sSearch": "Buscar:",
             "sZeroRecords": "No se encontraron registros coincidentes",
             "oPaginate": {
                 "sFirst": "Primero",
                 "sLast": "Último",
                 "sNext": "Siguiente",
                 "sPrevious": "Anterior"
             },
             "oAria": {
                 "sSortAscending": ": activar para ordenar la columna ascendente",
                 "sSortDescending": ": activar para ordenar la columna descendente"
             },
             "select": {
                 "rows": {
                     "_": "Seleccionado %d filas",
                     "0": "Haga clic en una fila para seleccionarla",
                     "1": "1 fila seleccionada"
                 }
             }
         }
    });
  });*/

