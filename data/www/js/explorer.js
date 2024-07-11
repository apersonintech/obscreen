jQuery(function ($) {

    const initExplr = function () {
        $('.explr').each(function () {
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

        $('.draggable').each(function () {
            $(this).draggable({
                revert: "invalid",
            });
        });

        $('.droppable').each(function () {
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
    };

    $(document).on('click', '.explr-item-edit', function () {
        const $item = $('.explr-dirview .highlight-clicked');
        const is_folder = $item.attr('data-folder') === '1';

        if (is_folder) {
            $item.addClass('renaming');
            $item.find('input').focus().select();
        } else {
            document.location.href = $(this).attr('data-entity-route').replace('!c!', $item.attr('data-id'));
        }
    });

    $(document).on('click', '.explr-item-delete', function () {
        const $item = $('.explr-dirview .highlight-clicked');
        const is_folder = $item.attr('data-folder') === '1';
        let route;

        if (is_folder) {
            route = $(this).attr('data-folder-route') + '?id=' + $item.attr('data-id');
        } else {
            route = $(this).attr('data-entity-route') + '?id=' + $item.attr('data-id');
        }

        if (confirm(l.common_are_you_sure)) {
            document.location.href = route;
        }
    });

    $(document).keyup(function (e) {
        if (e.key === "Escape") {
            $('.dirview .new-folder').addClass('hidden');
        }
    });

    main();
});