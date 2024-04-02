$(document).ready(function() {
    $('#tblProductos').DataTable({
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
  });

// $(document).ready(function () {
//     $('#tblProductos').DataTable
//         ({
            
//             dom: "Bfrtip",
//             buttons: [
//                 'excel',
//                 'pdf',
//                 'print'
//             ],
//             tabla: true
//             // lengthMenu: [
//             //     [10, 25, 50, 100],
//             //     ['10', '25', '50', '100'] 
//             // ],
//             // lengthChange: true,
//             // language: {
//             //     "decimal": ",",
//             //     "thousands": ".",
//             //     "sEmptyTable": "No hay datos disponibles en la tabla",
//             //     "sInfo": "Mostrando _START_ a _END_ de _TOTAL_ entradas",
//             //     "sInfoEmpty": "Mostrando 0 a 0 de 0 entradas",
//             //     "sInfoFiltered": "(filtrado de _MAX_ entradas totales)",
//             //     "sInfoPostFix": "",
//             //     "sInfoThousands": ",",
//             //     "sLengthMenu": "Mostrar _MENU_ entradas",
//             //     "sLoadingRecords": "Cargando...",
//             //     "sProcessing": "Procesando...",
//             //     "sSearch": "Buscar:",
//             //     "sZeroRecords": "No se encontraron registros coincidentes",
//             //     "oPaginate": {
//             //         "sFirst": "Primero",
//             //         "sLast": "Último",
//             //         "sNext": "Siguiente",
//             //         "sPrevious": "Anterior"
//             //     },
//             //     "oAria": {
//             //         "sSortAscending": ": activar para ordenar la columna ascendente",
//             //         "sSortDescending": ": activar para ordenar la columna descendente"
//             //     },
//             //     "select": {
//             //         "rows": {
//             //             "_": "Seleccionado %d filas",
//             //             "0": "Haga clic en una fila para seleccionarla",
//             //             "1": "1 fila seleccionada"
//             //         }
//             //     }
//             // }
//         });
// });


// $('#tblProductos').DataTable( {
//     buttons: [
//         'copy', 'excel', 'pdf'
//     ]
// } );


// $('#tblProductos').DataTable(
//     {
//         dom: 'Bfrtip',
//         buttons: [
//             'excel',
//             'pdf',
//             'print'
//         ],
//         lengthMenu: [10, 25, 50, 100],
//         lengthChange: true
//     }
// );

