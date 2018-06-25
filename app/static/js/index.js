$(document).ready(function() {
    $("#submit_filter").click(function(){
        $.getJSON($SCRIPT_ROOT + '/_ajax', {
            age: $('input[name="age"]').val(),
            breed: $('input[name="breed"]').val(),
            sex: $('input[name="sex"]').val(),
            n_photos: $('input[name="nPhotos"]').val(),
            size: $('input[name="size"]').val(),
            altered: $('input[name="altered"]').val(),
            specialNeeds: $('input[name="specialNeeds"]').val(),
            noKids: $('input[name="noKids"]').val(),
            noCats: $('input[name="noCats"]').val(),
            noDogs: $('input[name="noDogs"]').val(),
            housetrained: $('input[name="housetrained"]').val(),
            listing_state: $('input[name="listing_state"]').val(),
            urban: $('input[name="urban"]').val()
        }).done(function(response) {
            var response_data = JSON.parse(response);
            var data = filtered_source.data;
            data['y'] = response_data['subset_vals'];
            filtered_source.trigger.emit();
        });
    });
});
