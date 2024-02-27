jQuery(document).ready(function ($) {
    const $tableActive = $('table.active-screens');
    const $tableInactive = $('table.inactive-screens');
    const $modalsRoot = $('.modals');

    const getId = function ($el) {
        return $el.is('tr') ? $el.attr('data-level') : $el.parents('tr:eq(0)').attr('data-level');
    };

    const updateTable = function () {
        $('table').each(function () {
            if ($(this).find('tbody tr.screen-item:visible').length === 0) {
                $(this).find('tr.empty-tr').removeClass('hidden');
            } else {
                $(this).find('tr.empty-tr').addClass('hidden');
            }
        }).tableDnDUpdate();
        updatePositions();
    }

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
        $('.screen-item').each(function (index) {
            positions[getId($(this))] = index;
        });

        $.ajax({
            method: 'POST',
            url: '/fleet/screen/position',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify(positions),
        });
    };

    const main = function () {
        $("table").tableDnD({
            dragHandle: 'td a.screen-sort',
            onDrop: updatePositions
        });
    };

    $(document).on('change', 'input[type=checkbox]', function () {
        $.ajax({
            url: 'fleet/screen/toggle',
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

    $(document).on('change', '#screen-add-type', function () {
        const value = $(this).val();
        const inputType = $(this).find('option').filter(function (i, el) {
            return $(el).val() === value;
        }).data('input');

        $('.screen-add-object-input')
            .addClass('hidden')
            .prop('disabled', true)
            .filter('#screen-add-object-input-' + inputType)
            .removeClass('hidden')
            .prop('disabled', false)
        ;
    });

    $(document).on('click', '.modal-close', function () {
        hideModal();
    });

    $(document).on('click', '.screen-add', function () {
        showModal('modal-screen-add');
        $('.modal-screen-add input:eq(0)').focus().select();
    });

    $(document).on('click', '.screen-edit', function () {
        const screen = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-screen-edit');
        $('.modal-screen-edit input:visible:eq(0)').focus().select();
        $('#screen-edit-name').val(screen.name);
        $('#screen-edit-host').val(screen.host);
        $('#screen-edit-port').val(screen.port);
        $('#screen-edit-id').val(screen.id);
    });

    $(document).on('click', '.screen-delete', function () {
        if (confirm(l.fleet_screen_delete_confirmation)) {
            const $tr = $(this).parents('tr:eq(0)');
            $tr.remove();
            updateTable();
            $.ajax({
                method: 'DELETE',
                url: '/fleet/screen/delete',
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