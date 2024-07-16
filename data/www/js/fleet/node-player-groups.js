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

    $(document).on('click', '.node-player-group-player-assign', function () {
        const route = $(this).attr('data-route');
        showPickers('modal-node-player-explr-picker', function (nodePlayer) {
            if (!nodePlayer.group_id || (nodePlayer.group_id && confirm(l.js_fleet_node_player_assign_confirmation))) {
                document.location.href = route.replace('__id__', nodePlayer.id);
            }
        });
    });

    $(document).on('click', '.node-player-group-unassign-player', function () {
        if (confirm(l.js_fleet_node_player_delete_confirmation)) {
            const $item = $(this).parents('.player-item:eq(0)');
            if ($item.parents('ul:eq(0)').find('.player-item').length === 1) {
                document.location.href = $(this).attr('data-route');
            } else {
                $item.remove();
                $.ajax({
                    method: 'DELETE',
                    url: $(this).attr('data-route'),
                    headers: {'Content-Type': 'application/json'},
                    success: function (response) {
                        $('.node-player-group-item-' + response.group_id + ' .players-counter').html(response.pcounter);
                    }
                });
            }
        }
    });


    main();
});
