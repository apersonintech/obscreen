jQuery(document).ready(function ($) {
    const initExplr = function () {
        $('.explr').each(function() {
            $(this).explr({
                classesPlus: 'fa fa-plus',
                classesMinus: 'fa fa-minus',
                onLoadFinish: function ($tree) {
                    $tree.removeClass('hidden');
                }
            });

            // Open complete path in explorer sidebar
            explrSidebarOpenFromFolder($(this).attr('data-working-folder-id'));
        });
    };

    const initDrags = function () {
        $('.draggable').each(function() {
            $(this).draggable({
                revert: "invalid",
            });
        });

        $('.droppable').each(function() {
            $(this).droppable({
                accept: ".draggable",
                over: function (event, ui) {
                    $(this).addClass("highlight-drop");
                },
                out: function (event, ui) {
                    $(this).removeClass("highlight-drop");
                },
                drop: function (event, ui) {
                    $(this).removeClass("highlight-drop");
                    const $form = $('#folder-move-form');
                    const $moved = ui.draggable;
                    const $target = $(this);
                    $form.find('[name=is_folder]').val($moved.attr('data-folder'))
                    $form.find('[name=entity_id]').val($moved.attr('data-id'))
                    $form.find('[name=new_folder_id]').val($target.attr('data-id'))
                    ui.draggable.position({
                        my: "center",
                        at: "center",
                        of: $(this),
                        using: function (pos) {
                            $(this).animate(pos, 50);
                        }
                    });
                    $form.submit();
                }
            });
        });
    };

    const main = function () {
        initExplr();
        initDrags();
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

    $(document).on('click', '.explr-item-edit', function () {
        const $item = $('.explr-dirview .highlight-clicked');
        const is_folder = $item.attr('data-folder') === '1';

        if (is_folder) {
            $item.addClass('renaming');
            $item.find('input').focus().select();
        } else {
            document.location.href = $(this).attr('data-node-player-route').replace('!c!', $item.attr('data-id'));
        }
    });

    $(document).on('click', '.explr-item-delete', function () {
        const $item = $('.explr-dirview .highlight-clicked');
        const is_folder = $item.attr('data-folder') === '1';
        let route;

        if (is_folder) {
            route = $(this).attr('data-folder-route') + '?id=' + $item.attr('data-id');
        } else {
            route = $(this).attr('data-node-player-route') + '?id=' + $item.attr('data-id');
        }

        if (confirm(l.js_fleet_node_player_delete_confirmation)) {
            document.location.href = route;
        }
    });

    $(document).on('click', '.node-player-edit', function () {
        const node_player = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-node-player-edit');



        $('.modal-node-player-edit input:visible:eq(0)').focus().select();
        $('#node-player-edit-id').val(node_player.id);
    });

    $(document).on('submit', '.modal-node-player-add form', function () {
        const $modal = $(this).parents('.modal:eq(0)');
        $modal.find('button[type=submit]').addClass('hidden');
        $modal.find('.btn-loading').removeClass('hidden');
    });

     $(document).keyup(function (e) {
        if (e.key === "Escape") {
            $('.dirview .new-folder').addClass('hidden');
        }
    });

    main();
});
