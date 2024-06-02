jQuery(document).ready(function ($) {
    const $tableActive = $('table.active-node-studios');
    const $tableInactive = $('table.inactive-node-studios');

    const getId = function ($el) {
        return $el.is('tr') ? $el.attr('data-level') : $el.parents('tr:eq(0)').attr('data-level');
    };

    const updateTable = function () {
        $('table').each(function () {
            if ($(this).find('tbody tr.node-studio-item:visible').length === 0) {
                $(this).find('tr.empty-tr').removeClass('hidden');
            } else {
                $(this).find('tr.empty-tr').addClass('hidden');
            }
        }).tableDnDUpdate();
        updatePositions();
    };

    const updatePositions = function (table, row) {
        const positions = {};
        $('.node-studio-item').each(function (index) {
            positions[getId($(this))] = index;
        });

        $.ajax({
            method: 'POST',
            url: '/fleet/node-studio/position',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify(positions),
        });
    };

    const main = function () {
        $("table").tableDnD({
            dragHandle: 'td a.node-studio-sort',
            onDrop: updatePositions
        });
    };

    $(document).on('change', 'input[type=checkbox]', function () {
        $.ajax({
            url: '/fleet/node-studio/toggle',
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

    $(document).on('change', '#node-studio-add-type', function () {
        const value = $(this).val();
        const inputType = $(this).find('option').filter(function (i, el) {
            return $(el).val() === value;
        }).data('input');

        $('.node-studio-add-object-input')
            .addClass('hidden')
            .prop('disabled', true)
            .filter('#node-studio-add-object-input-' + inputType)
            .removeClass('hidden')
            .prop('disabled', false)
        ;
    });

    $(document).on('click', '.node-studio-add', function () {
        showModal('modal-node-studio-add');
        $('.modal-node-studio-add input:eq(0)').focus().select();
    });

    $(document).on('click', '.node-studio-edit', function () {
        const nodeStudio = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-node-studio-edit');
        $('.modal-node-studio-edit input:visible:eq(0)').focus().select();
        $('#node-studio-edit-name').val(nodeStudio.name);
        $('#node-studio-edit-host').val(nodeStudio.host);
        $('#node-studio-edit-port').val(nodeStudio.port);
        $('#node-studio-edit-id').val(nodeStudio.id);
    });

    $(document).on('click', '.node-studio-delete', function () {
        if (confirm(l.js_fleet_node_studio_delete_confirmation)) {
            const $tr = $(this).parents('tr:eq(0)');
            $tr.remove();
            updateTable();
            $.ajax({
                method: 'DELETE',
                url: '/fleet/node-studio/delete',
                headers: {'Content-Type': 'application/json'},
                data: JSON.stringify({id: getId($(this))}),
            });
        }
    });

    main();
});