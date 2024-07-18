jQuery(document).ready(function ($) {
    var done = function () {
        setTimeout(function() {
            document.location.reload();
        }, 3000);
    };

    $(document).on('click', '.sysinfo-restart', function () {
        if (confirm(l.js_sysinfo_restart_confirmation)) {
            $('body').html($('<div class="reboot">').html(l.js_sysinfo_restart_loading)).css({margin:200});
            $.ajax({
                url: route_sysinfo_restart + '?secret_key='+secret_key,
                headers: {'Content-Type': 'application/json'},
                data: '',
                method: 'POST',
            }).done(done).catch(done);
        }

    });
});