jQuery(document).ready(function ($) {

    const main = function () {

    };

    $(document).on('click', '.folder-add', function () {
        $('.dirview .new-folder').removeClass('hidden');
        $('.page-content').animate({scrollTop: 0}, 0);
        $('.dirview input').focus();
    });

    $(document).on('click', '.node-player-add', function () {
        showModal('modal-node-player-add');
        $('.modal-node-player-add input:eq(0)').focus().select();
    });

    $(document).on('submit', '.modal-node-player-add form', function () {
        const $modal = $(this).parents('.modal:eq(0)');
        $modal.find('button[type=submit]').addClass('hidden');
        $modal.find('.btn-loading').removeClass('hidden');
    });

    main();
});
