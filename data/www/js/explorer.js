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

    const selectEpxlrLink = function ($link) {
        $('a.explr-link').removeClass('highlight-clicked');
        $('a.explr-link').parent().removeClass('highlight-clicked');
        $('body').removeClass('explr-selection explr-selection-actionable explr-selection-entity explr-selection-folder');

        if ($link.hasClass('explr-item-selectable')) {
            $link.addClass('highlight-clicked');
            $link.parent().addClass('highlight-clicked');
            $('body').addClass('explr-selection');
            if ($link.hasClass('explr-item-actionable')) {
                $('body').addClass('explr-selection-actionable');
            }
            if ($link.hasClass('explr-item-entity')) {
                $('body').addClass('explr-selection-entity');
            }
            if ($link.hasClass('explr-item-folder')) {
                $('body').addClass('explr-selection-folder');
            }
        }
    };

    const getExplrSelection = function () {
        return $('.explr-dirview .highlight-clicked');
    };

    const renameExplrItem = function($item) {
        $('.dirview .renaming').removeClass('renaming');
        $item.addClass('renaming');
        $item.find('input').focus().select();
    }

    $(document).on('click', '.explr-item-edit', function () {
        document.location.href = $(this).attr('data-entity-route').replace('!c!', getExplrSelection().attr('data-id'));
    });

    $(document).on('click', '.explr-item-rename', function () {
        renameExplrItem(getExplrSelection());
    });

    $(document).on('click', '.explr-item-delete', function () {
        const $item = getExplrSelection();
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
        const $selectedLink = $('.explr-item-selectable.highlight-clicked');
        const $selectedLi = $selectedLink.parents('li:eq(0)');

        if (e.key === "Escape") {
            $('.dirview .new-folder').addClass('hidden');
            $('.dirview .renaming').removeClass('renaming');
        } else if (e.code === "Space") {
            renameExplrItem($selectedLi);
        } else if ($selectedLink.length) {
            const $prevLi = $selectedLi.prev('li:visible');
            const $nextLi = $selectedLi.next('li:visible');
            const verticalNeighbors = getAboveBelowElement($selectedLi);

            if (e.key === "Enter") {
                $selectedLink.trigger('dblclick');
            } else if (e.key === "ArrowLeft" && $prevLi.length) {
                selectEpxlrLink($prevLi.find('.explr-link'));
            } else if (e.key === "ArrowRight" && $nextLi.length) {
                selectEpxlrLink($nextLi.find('.explr-link'));
            } else if (e.key === "ArrowUp" && verticalNeighbors.above) {
                selectEpxlrLink(verticalNeighbors.above.find('.explr-link'));
            } else if (e.key === "ArrowDown" && verticalNeighbors.below) {
                selectEpxlrLink(verticalNeighbors.below.find('.explr-link'));
            }
        }
    });

    // Explorer item selection
    $(document).on('click', 'a.explr-link', function (event) {
        event.preventDefault();
        selectEpxlrLink($(this));
    });
    $(document).on('dblclick', 'a.explr-link', function (event) {
        event.preventDefault();
        $(this).off('click');
        const href = $(this).attr('href');

        if ($(this).attr('target') === '_blank') {
            window.open(href);
        } else {
            window.location.href = href;
        }
    });
    $(document).on('click', function (event) {
        const $parentClickable = $(event.target).parents('a, button');
        if ($parentClickable.length === 0) {
            $('a.explr-link').removeClass('highlight-clicked');
            $('a.explr-link').parent().removeClass('highlight-clicked');
            $('body').removeClass('explr-selection explr-selection-entity explr-selection-folder explr-selection-actionable');
        }
    });

    const getAboveBelowElement = function ($elem) {
        const $liElements = $elem.parents('ul:eq(0)').find('li');
        const positions = [];

        // Get the Y positions of each element
        $liElements.each(function () {
            const $this = $(this);
            positions.push({
                element: $this,
                y: $this.offset().top,
                x: $this.offset().left
            });
        });

        // Group elements by their Y position
        const groupedByY = positions.reduce((acc, pos) => {
            if (!acc[pos.y]) {
                acc[pos.y] = [];
            }
            acc[pos.y].push(pos);
            return acc;
        }, {});

        // Convert groupedByY to an array of arrays
        const rows = Object.values(groupedByY);

        let targetRowIndex = -1;
        let targetColIndex = -1;

        // Find the row and column index of the target element
        rows.forEach((row, rowIndex) => {
            row.forEach((pos, colIndex) => {
                if (pos.element.is($elem)) {
                    targetRowIndex = rowIndex;
                    targetColIndex = colIndex;
                }
            });
        });

        const result = {
            above: null,
            below: null
        };

        if (targetRowIndex > 0) {
            const aboveRow = rows[targetRowIndex - 1];
            if (targetColIndex < aboveRow.length) {
                result.above = aboveRow[targetColIndex].element;
            }
        }

        if (targetRowIndex < rows.length - 1) {
            const belowRow = rows[targetRowIndex + 1];
            if (targetColIndex < belowRow.length) {
                result.below = belowRow[targetColIndex].element;
            }
        }

        return result;
    }

    main();
});