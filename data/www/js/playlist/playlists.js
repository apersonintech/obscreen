jQuery(document).ready(function ($) {
    const $tableActive = $('table.active-playlists');
    const $tableInactive = $('table.inactive-playlists');
    const $modalsRoot = $('.modals');

    const getId = function ($el) {
        return $el.is('tr') ? $el.attr('data-level') : $el.parents('tr:eq(0)').attr('data-level');
    };

    const updateTable = function () {
        $('table').each(function () {
            if ($(this).find('tbody tr.playlist-item:visible').length === 0) {
                $(this).find('tr.empty-tr').removeClass('hidden');
            } else {
                $(this).find('tr.empty-tr').addClass('hidden');
            }
        });
    };

    const showModal = function (modalClass) {
        $modalsRoot.removeClass('hidden').find('form').trigger('reset');
        $modalsRoot.find('.modal').addClass('hidden');
        $modalsRoot.find('.modal.' + modalClass).removeClass('hidden');
    };

    const hideModal = function () {
        $modalsRoot.addClass('hidden').find('form').trigger('reset');
    };

    const main = function () {

    };

    $(document).on('change', 'input[type=checkbox]', function () {
        $.ajax({
            url: '/playlist/toggle',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify({id: getId($(this)), enabled: $(this).is(':checked')}),
            method: 'POST',
        });

        const $tr = $(this).parents('tr:eq(0)').remove().clone();

        if ($(this).is(':checked')) {
            $tableActive.append($tr);
        } else {
            $tableInactive.append($tr);
        }

        updateTable();
    });

    $(document).on('click', '.modal-close', function () {
        hideModal();
    });

    $(document).on('click', '.playlist-add', function () {
        showModal('modal-playlist-add');
        $('.modal-playlist-add input:eq(0)').focus().select();
    });

    $(document).on('click', '.playlist-edit', function () {
        const playlist = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-playlist-edit');
        $('.modal-playlist-edit input:visible:eq(0)').focus().select();
        $('#playlist-edit-name').val(playlist.name);
        $('#playlist-edit-id').val(playlist.id);
    });

    $(document).on('click', '.playlist-delete', function () {
        if (confirm(l.js_playlist_delete_confirmation)) {
            const $tr = $(this).parents('tr:eq(0)');
            $.ajax({
                method: 'DELETE',
                url: '/playlist/delete',
                headers: {'Content-Type': 'application/json'},
                data: JSON.stringify({id: getId($(this))}),
                success: function(data) {
                    $tr.remove();
                    updateTable();
                },
                error: function(data) {
                    $('.alert-error').html(data.responseJSON.message).removeClass('hidden');
                }
            });
        }
    });

    $(document).keyup(function (e) {
        if (e.key === "Escape") {
            hideModal();
        }
    });

    main();
});
