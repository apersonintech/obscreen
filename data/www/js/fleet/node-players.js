jQuery(document).ready(function ($) {

    const main = function () {
        inputOperatingSystemUpdate();
    };

    window.nodePlayerEdit = function ($this) {
        const nodePlayer = JSON.parse($this.parents('li:eq(0)').attr('data-entity-json'));
        showModal('modal-node-player-edit');
        $('.modal-node-player-edit input:visible:eq(0)').focus().select();
        $('#node-player-edit-name').val(nodePlayer.name);
        $('#node-player-edit-host').val(nodePlayer.host);
        $('#node-player-edit-id').val(nodePlayer.id);
        inputOperatingSystemUpdate();
    };

    const inputOperatingSystemUpdate = function () {
        const $el = $('form:visible .operating-system-select');
        if ($el.length === 0) return;
        const $form = $el.parents('form:eq(0)');
        const value = $el.val();
        const $selectedOption = $el.find('option[value='+value+']');
        const optionAttributes = $selectedOption.get(0).attributes;
        const color = optionAttributes['data-color'].value;
        $('.operating-system-icon').attr('class', 'operating-system-icon fa ' + optionAttributes['data-icon'].value);
        $('.tab-select .widget').attr('class', 'widget ' + ('border-' + color) + ' ' + color);
        $form.find('button[type=submit]').attr('class', 'btn ' + ('btn-' + color));
    };

    $(document).on('change', '.operating-system-select', inputOperatingSystemUpdate);

    $(document).on('click', '.folder-add', function () {
        $('.dirview .new-folder').removeClass('hidden');
        $('.page-content').animate({scrollTop: 0}, 0);
        $('.dirview input').focus();
    });

    $(document).on('click', '.node-player-add', function () {
        showModal('modal-node-player-add');
        inputOperatingSystemUpdate();
        $('.modal-node-player-add input:eq(0)').focus().select();
    });

    $(document).on('submit', '.modal-node-player-add form', function () {
        const $modal = $(this).parents('.modal:eq(0)');
        $modal.find('button[type=submit]').addClass('hidden');
        $modal.find('.btn-loading').removeClass('hidden');
    });

    main();
});
