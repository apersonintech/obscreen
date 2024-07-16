jQuery(document).ready(function ($) {

    const main = function () {
        const $qrcode = $('#qrcode');

        if ($qrcode.length) {
            new QRCode($qrcode.get(0), {
                text: $qrcode.attr('data-qrcode-payload'),
                width: 128,
                height: 128,
                colorDark: '#222',
                colorLight: '#fff',
                correctLevel: QRCode.CorrectLevel.H
            });
        }
    };

    $(document).on('click', '.playlist-add', function () {
        showModal('modal-playlist-add');
        $('.modal-playlist-add input:eq(0)').focus().select();
    });

    $(document).on('click', '.playlist-preview', function () {
        const $iframe = $('<iframe>', {
            src: $(this).attr('data-url'),
            frameborder: 0
        });

        $(this).parents('.preview:eq(0)').append($iframe);
        $(this).remove();
    });

    main();
});
