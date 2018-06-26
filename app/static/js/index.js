// $(document).ready(function() {
//     $("#submit_filter").click(function(){
//         $.ajax({
//             url: '/_ajax',
//             data: $("#filter_form").serialize(),
//             type: 'GET',
//             success: function(response) {
//                 console.log(response);
//                 var response_data = response;
//                 var data = $(filtered_source.data;
//                 data['x'] = [0, 1, 2, 3, 4, 5, 6, 7, 14, 21, 28, 45, 60, 90, 180, 365];
//                 data['y'] = response_data['y_vals'];
//                 filtered_source.trigger.emit();
//             },
//             error: function(error) {
//                 console.log(error);
//             }
//             // age: $("#age").val(),
//             // breed: $("#breed").val(),
//             // sex: $("#sex").val(),
//             // n_photos: $("#nPhotos").val(),
//             // size: $("#size").val(),
//             // altered: $("#altered").val(),
//             // specialNeeds: $("#specialNeeds").val(),
//             // noKids: $("#noKids").val(),
//             // noCats: $("#noCats").val(),
//             // noDogs: $("#noDogs").val(),
//             // housetrained: $("#housetrained").val(),
//             // listing_state: $("#listing_state").val(),
//             // urban: $("#urban").val()
//         });
//     });
// });
