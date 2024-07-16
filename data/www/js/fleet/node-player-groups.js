jQuery(document).ready(function ($) {

    const main = function () {

    };

    $(document).on('click', '.node-player-group-add', function () {
        showModal('modal-node-player-group-add');
        $('.modal-node-player-group-add input:eq(0)').focus().select();
    });

    $(document).on('click', '.node-player-group-preview', function () {
        const $iframe = $('<iframe>', {
            src: $(this).attr('data-url'),
            frameborder: 0
        });

        $(this).parents('.preview:eq(0)').append($iframe);
        $(this).remove();
    });

    main();
});
