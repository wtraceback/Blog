$(function() {
    var render_time = function() {
        return moment($(this).data('timestamp')).format('lll')
    }

    $('[data-toggle="tooltip"]').tooltip({
        title: render_time
    });
})
