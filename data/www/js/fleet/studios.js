jQuery(document).ready(function ($) {
    const $tableActive = $('table.active-studios');
    const $tableInactive = $('table.inactive-studios');
    const $modalsRoot = $('.modals');

    const getId = function ($el) {
        return $el.is('tr') ? $el.attr('data-level') : $el.parents('tr:eq(0)').attr('data-level');
    };

    const updateTable = function () {
        $('table').each(function () {
            if ($(this).find('tbody tr.studio-item:visible').length === 0) {
                $(this).find('tr.empty-tr').removeClass('hidden');
            } else {
                $(this).find('tr.empty-tr').addClass('hidden');
            }
        }).tableDnDUpdate();
        updatePositions();
    };

    const showModal = function (modalClass) {
        $modalsRoot.removeClass('hidden').find('form').trigger('reset');
        $modalsRoot.find('.modal').addClass('hidden');
        $modalsRoot.find('.modal.' + modalClass).removeClass('hidden');
    };

    const hideModal = function () {
        $modalsRoot.addClass('hidden').find('form').trigger('reset');
    };

    const updatePositions = function (table, row) {
        const positions = {};
        $('.studio-item').each(function (index) {
            positions[getId($(this))] = index;
        });

        $.ajax({
            method: 'POST',
            url: '/fleet/studio/position',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify(positions),
        });
    };

    const main = function () {
        $("table").tableDnD({
            dragHandle: 'td a.studio-sort',
            onDrop: updatePositions
        });
    };

    $(document).on('change', 'input[type=checkbox]', function () {
        $.ajax({
            url: '/fleet/studio/toggle',
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

    $(document).on('change', '#studio-add-type', function () {
        const value = $(this).val();
        const inputType = $(this).find('option').filter(function (i, el) {
            return $(el).val() === value;
        }).data('input');

        $('.studio-add-object-input')
            .addClass('hidden')
            .prop('disabled', true)
            .filter('#studio-add-object-input-' + inputType)
            .removeClass('hidden')
            .prop('disabled', false)
        ;
    });

    $(document).on('click', '.modal-close', function () {
        hideModal();
    });

    $(document).on('click', '.studio-add', function () {
        showModal('modal-studio-add');
        $('.modal-studio-add input:eq(0)').focus().select();
    });

    $(document).on('click', '.studio-edit', function () {
        const studio = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-studio-edit');
        $('.modal-studio-edit input:visible:eq(0)').focus().select();
        $('#studio-edit-name').val(studio.name);
        $('#studio-edit-host').val(studio.host);
        $('#studio-edit-port').val(studio.port);
        $('#studio-edit-id').val(studio.id);
    });

    $(document).on('click', '.studio-delete', function () {
        if (confirm(l.js_fleet_studio_delete_confirmation)) {
            const $tr = $(this).parents('tr:eq(0)');
            $tr.remove();
            updateTable();
            $.ajax({
                method: 'DELETE',
                url: '/fleet/studio/delete',
                headers: {'Content-Type': 'application/json'},
                data: JSON.stringify({id: getId($(this))}),
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