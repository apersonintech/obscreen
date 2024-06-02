jQuery(document).ready(function ($) {

    const getId = function ($el) {
        return $el.is('tr') ? $el.attr('data-level') : $el.parents('tr:eq(0)').attr('data-level');
    };

    const updateTable = function () {
        $('table').each(function () {
            if ($(this).find('tbody tr.node-player-group-item:visible').length === 0) {
                $(this).find('tr.empty-tr').removeClass('hidden');
            } else {
                $(this).find('tr.empty-tr').addClass('hidden');
            }
        });
    };

    const main = function () {
        
    };

    $(document).on('change', '#node-player-group-add-type', function () {
        const value = $(this).val();
        const inputType = $(this).find('option').filter(function (i, el) {
            return $(el).val() === value;
        }).data('input');

        $('.node-player-group-add-object-input')
            .addClass('hidden')
            .prop('disabled', true)
            .filter('#node-player-group-add-object-input-' + inputType)
            .removeClass('hidden')
            .prop('disabled', false)
        ;
    });

    $(document).on('click', '.node-player-group-add', function () {
        showModal('modal-node-player-group-add');
        $('.modal-node-player-group-add input:eq(0)').focus().select();
    });

    $(document).on('click', '.node-player-group-edit', function () {
        const nodePlayerGroup = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-node-player-group-edit');
        $('.modal-node-player-group-edit input:visible:eq(0)').focus().select();
        $('#node-player-group-edit-name').val(nodePlayerGroup.name);
        $('#node-player-group-edit-id').val(nodePlayerGroup.id);
    });

    $(document).on('click', '.node-player-group-delete', function () {
        if (confirm(l.js_fleet_node_player_delete_confirmation)) {
            const $tr = $(this).parents('tr:eq(0)');
            $tr.remove();
            updateTable();
            $.ajax({
                method: 'DELETE',
                url: '/fleet/node-player-group/delete',
                headers: {'Content-Type': 'application/json'},
                data: JSON.stringify({id: getId($(this))}),
            });
        }
    });

    main();
});