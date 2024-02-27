jQuery(document).ready(function ($) {
    $(document).on('click', '.sysinfo-restart', function () {
        if (confirm(l.js_sysinfo_restart_confirmation)) {
            $('body').html(l.js_sysinfo_restart_loading).css({margin:200});
            $.ajax({
                url: '/sysinfo/restart',
                headers: {'Content-Type': 'application/json'},
                data: '',
                method: 'POST',
            }).catch(function () {
                setTimeout(function() {
                    document.location.reload();
                }, 3000);
            });
        }

    });
});