jQuery(document).ready(function ($) {
    const $tableActive = $('table.active-node-players');
    const $tableInactive = $('table.inactive-node-players');

    const getId = function ($el) {
        return $el.is('tr') ? $el.attr('data-level') : $el.parents('tr:eq(0)').attr('data-level');
    };

    const updateTable = function () {
        $('table').each(function () {
            if ($(this).find('tbody tr.node-player-item:visible').length === 0) {
                $(this).find('tr.empty-tr').removeClass('hidden');
            } else {
                $(this).find('tr.empty-tr').addClass('hidden');
            }
        }).tableDnDUpdate();
        updatePositions();
    };

    const updatePositions = function (table, row) {
        const positions = {};
        $('.node-player-item').each(function (index) {
            positions[getId($(this))] = index;
        });

        $.ajax({
            method: 'POST',
            url: '/fleet/node-player/position',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify(positions),
        });
    };

    const main = function () {
        $("table").tableDnD({
            dragHandle: 'td a.node-player-sort',
            onDrop: updatePositions
        });
    };

    $(document).on('change', 'input[type=checkbox]', function () {
        $.ajax({
            url: '/fleet/node-player/toggle',
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

    $(document).on('change', '#node-player-add-type', function () {
        const value = $(this).val();
        const inputType = $(this).find('option').filter(function (i, el) {
            return $(el).val() === value;
        }).data('input');

        $('.node-player-add-object-input')
            .addClass('hidden')
            .prop('disabled', true)
            .filter('#node-player-add-object-input-' + inputType)
            .removeClass('hidden')
            .prop('disabled', false)
        ;
    });


    $(document).on('click', '.node-player-add', function () {
        showModal('modal-node-player-add');
        $('.modal-node-player-add input:eq(0)').focus().select();
    });

    $(document).on('click', '.node-player-edit', function () {
        const nodePlayer = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-node-player-edit');
        $('.modal-node-player-edit input:visible:eq(0)').focus().select();
        $('#node-player-edit-name').val(nodePlayer.name);
        $('#node-player-edit-host').val(nodePlayer.host);
        $('#node-player-edit-id').val(nodePlayer.id);
    });

    $(document).on('click', '.node-player-delete', function () {
        if (confirm(l.js_fleet_node_player_delete_confirmation)) {
            const $tr = $(this).parents('tr:eq(0)');
            $tr.remove();
            updateTable();
            $.ajax({
                method: 'DELETE',
                url: '/fleet/node-player/delete',
                headers: {'Content-Type': 'application/json'},
                data: JSON.stringify({id: getId($(this))}),
            });
        }
    });

    main();
});