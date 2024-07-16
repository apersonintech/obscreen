jQuery(document).ready(function ($) {

    const main = function () {
        const qrcodeElement = document.getElementById('qrcode');

        if (qrcodeElement) {
            new QRCode(qrcodeElement, {
                text: qrcodeElement.attributes['data-qrcode-payload'].value,
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
