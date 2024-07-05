jQuery(document).ready(function ($) {
    const getId = function ($el) {
        return $el.is('tr') ? $el.attr('data-level') : $el.parents('tr:eq(0)').attr('data-level');
    };

    const updateTable = function () {
        $('table').each(function () {
            if ($(this).find('tbody tr.content-item:visible').length === 0) {
                $(this).find('tr.empty-tr').removeClass('hidden');
            } else {
                $(this).find('tr.empty-tr').addClass('hidden');
            }
        });
    };

    const inputTypeUpdate = function () {
        const $el = $('#content-add-type');
        const value = $el.val();
        const inputType = $el.find('option').filter(function (i, el) {
            return $(el).val() === value;
        }).data('input');

        $('.content-add-object-input')
            .addClass('hidden')
            .prop('disabled', true)
            .filter('#content-add-object-input-' + inputType)
            .removeClass('hidden')
            .prop('disabled', false)
        ;
    };

    const main = function () {
        $('.explr').explr();
    };

    $(document).on('change', '#content-add-type', inputTypeUpdate);

    $(document).on('click', '.content-add', function () {
        showModal('modal-content-add');
        inputTypeUpdate();
        $('.modal-content-add input:eq(0)').focus().select();
    });

    $(document).on('click', '.content-edit', function () {
        const content = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-content-edit');

        let location = content.location;

        if (content.type == 'youtube') {
            location = 'https://www.youtube.com/watch?v=' + content.location;
        }

        $('.modal-content-edit input:visible:eq(0)').focus().select();
        $('#content-edit-name').val(content.name);
        $('#content-edit-type').val(content.type);
        $('#content-edit-location').val(location).prop('disabled', !content.is_editable);
        $('#content-edit-id').val(content.id);
    });

    $(document).on('click', '.content-delete', function () {
        if (confirm(l.js_slideshow_content_delete_confirmation)) {
            const $tr = $(this).parents('tr:eq(0)');
            $tr.remove();
            updateTable();
            $.ajax({
                method: 'DELETE',
                url: '/slideshow/content/delete',
                headers: {'Content-Type': 'application/json'},
                data: JSON.stringify({id: getId($(this))}),
            });
        }
    });

    $(document).on('submit', '.modal-content-add form', function () {
        $(this).find('button[type=submit]').addClass('hidden');
        $(this).find('.btn-loading').removeClass('hidden');
    });

    main();
});
