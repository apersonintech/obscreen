jQuery(document).ready(function ($) {

    $(document).on('click', '.protected', function(e) {
        e.preventDefault();
        e.stopPropagation();

        if (confirm(l.js_common_are_you_sure)) {
            if ($(this).is('a')) {
                if ($(this).attr('target') == '_blank') {
                    window.open($(this).attr('href'));
                } else {
                    document.location.href = $(this).attr('href');
                }
            }
        }

        return false;
    })
});