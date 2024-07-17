let onPickedElement = function (element) {
};

jQuery(function ($) {
    let lastClicked = null;
    let selectionStart = null;
    let selectionRectangle = null;

    const startSelection = function (event) {
        // mouse left button only
        if (event.button !== 0) {
            return;
        }
        selectionStart = {x: event.pageX, y: event.pageY};

        selectionRectangle = $('<div class="selection-rectangle"></div>');
        $('body').append(selectionRectangle);

        $(document).on('mousemove', updateSelection);
        $(document).on('mouseup', endSelection);

        event.preventDefault();
    };

    const isMajorSelection = function () {
        if (!selectionStart) return false;
        const width = selectionRectangle.width();
        const height = selectionRectangle.height()
        return (width > 40 && height > 40)
    };

    const updateSelection = function (event) {
        if ($('body').hasClass('dragging')) {
            endSelection()
            return;
        }

        if (!selectionStart) return;

        const current = {x: event.pageX, y: event.pageY};
        const top = Math.min(selectionStart.y, current.y);
        const left = Math.min(selectionStart.x, current.x);
        const width = Math.abs(selectionStart.x - current.x);
        const height = Math.abs(selectionStart.y - current.y);

        selectionRectangle.css({top, left, width, height});

        $('.explr-dirview li > a.explr-link').each(function () {
            const $link = $(this);
            const linkOffset = $link.offset();
            const linkWidth = $link.outerWidth();
            const linkHeight = $link.outerHeight();

            const isWithinSelection = (
                linkOffset.left < left + width &&
                linkOffset.left + linkWidth > left &&
                linkOffset.top < top + height &&
                linkOffset.top + linkHeight > top
            );

            if (isMajorSelection()) {
                if (isWithinSelection) {
                    highlightExplrLink($link);
                } else {
                    unhighlightExplrLink($link);
                }
            }
        });

        updateBodyClasses();
    };

    const endSelection = function (event) {
        $(document).off('mousemove', updateSelection);
        $(document).off('mouseup', endSelection);

        if (selectionRectangle) {
            selectionRectangle.remove();
            setTimeout(function () {
                selectionRectangle = null;
                selectionStart = null;
            }, 100);
        }

        updateBodyClasses();
    };

    const explrSidebarOpenFromFolder = function (folderId) {
        const $leaf = $('.li-explr-folder-' + folderId);
        let $parent = $leaf;
        while ($parent.length > 0) {
            const $toggler = $parent.find('.explr-toggler:eq(0)');
            if ($toggler.hasClass('explr-plus')) {
                $parent.find('.explr-toggler:eq(0)').trigger('click');
            }
            $parent = $parent.parents('.li-explr-folder:eq(0)');
        }
    };

    const initExplr = function () {
        $('.explr').each(function () {
            $(this).explr({
                classesPlus: 'fa fa-chevron-right',
                classesMinus: 'fa fa-chevron-down',
                onLoadFinish: function ($tree) {
                    $tree.removeClass('hidden');
                }
            });

            // Open complete path in explorer sidebar
            explrSidebarOpenFromFolder($(this).attr('data-working-folder-id'));
        });

        $('.draggable').each(function () {
            $(this).multiDraggable({
                revert: "invalid",
                revertDuration: 10,
                group: 'li.highlight-clicked',
                startNative: function (event, ui) {
                    $('body').addClass('dragging');
                },
                stopNative: function () {
                    $('body').removeClass('dragging');
                }
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
                    const $moved = $('.ui-draggable-dragging');
                    const $target = $(this);
                    const folder_ids = [], entity_ids = [];

                    $moved.each(function () {
                        const $item = $(this);
                        const is_folder = $item.attr('data-folder') === '1';
                        const id = $item.attr('data-id');

                        if (is_folder) {
                            folder_ids.push(id);
                        } else {
                            entity_ids.push(id);
                        }

                        $item.position({
                            my: "center",
                            at: "center",
                            of: $target,
                            using: function (pos) {
                                $item.animate(pos, 50);
                            }
                        });
                    });

                    $form.find('[name=entity_ids]').val(entity_ids.join(','))
                    $form.find('[name=folder_ids]').val(folder_ids.join(','))
                    $form.find('[name=new_folder_id]').val($target.attr('data-id'))
                    $form.submit();
                }
            });
        });
    };

    const main = function () {
        initExplr();
    };

    const updateBodyClasses = function () {
        const $selectedLinks = $('a.explr-link.highlight-clicked');
        const isMultiSelect = $selectedLinks.length > 1;
        const isSingleSelect = $selectedLinks.length === 1;
        const $link = $selectedLinks.last();

        $('body')
            .toggleClass('explr-selection', isSingleSelect)
            .toggleClass('explr-selection-actionable', isSingleSelect && $link.hasClass('explr-item-actionable'))
            .toggleClass('explr-selection-entity', isSingleSelect && $link.hasClass('explr-item-entity'))
            .toggleClass('explr-selection-folder', isSingleSelect && $link.hasClass('explr-item-folder'))
            .toggleClass('explr-multiselection', isMultiSelect)
            .toggleClass('explr-multiselection-actionable', isMultiSelect && $selectedLinks.hasClass('explr-item-actionable'))
            .toggleClass('explr-multiselection-entity', isMultiSelect && $selectedLinks.hasClass('explr-item-entity'))
            .toggleClass('explr-multiselection-folder', isMultiSelect && $selectedLinks.hasClass('explr-item-folder'));
    };

    const highlightExplrLink = function ($link) {
        $link.addClass('highlight-clicked');
        $link.parent().addClass('highlight-clicked');
    };

    const unhighlightExplrLink = function ($link) {
        $link.removeClass('highlight-clicked');
        $link.parent().removeClass('highlight-clicked');
    };

    const selectEpxlrLink = function ($link) {
        highlightExplrLink($link);
        updateBodyClasses();
    };

    const clearSelection = function () {
        unhighlightExplrLink($('a.explr-link'));
        $('body').removeClass('explr-selection explr-selection-actionable explr-selection-entity explr-selection-folder explr-multiselection explr-multiselection-actionable explr-multiselection-entity explr-multiselection-folder');
    };

    const handleShiftClick = function ($link) {
        const $links = $('li > a.explr-link');
        const start = $links.index(lastClicked);
        const end = $links.index($link);
        const [from, to] = start < end ? [start, end] : [end, start];
        $links.slice(from, to + 1).each(function () {
            selectEpxlrLink($(this));
        });
        updateBodyClasses();
    };

    const handleCmdCtrlClick = function ($link) {
        if ($link.hasClass('highlight-clicked')) {
            $link.removeClass('highlight-clicked');
            $link.parent().removeClass('highlight-clicked');
        } else {
            selectEpxlrLink($link);
        }
        updateBodyClasses();
    };

    const getExplrSelection = function () {
        return $('.explr-dirview li.highlight-clicked');
    };

    const renameExplrItem = function ($item) {
        $('.dirview .renaming').removeClass('renaming');
        $item.addClass('renaming');
        $item.find('input').focus().select();
    };

    const getSelectedElements = function () {
        return $('.explr-item-selectable.highlight-clicked');
    };

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
            route = $(this).attr('data-folder-route') + '&id=' + $item.attr('data-id');
        } else {
            route = $(this).attr('data-entity-route') + '&id=' + $item.attr('data-id');
        }

        if (confirm(l.js_common_are_you_sure)) {
            document.location.href = route;
        }
    });

    $(document).on('click', '.explr-items-delete', function () {
        const $items = getExplrSelection();
        const folder_ids = [], entity_ids = [];

        $items.each(function () {
            const is_folder = $(this).attr('data-folder') === '1';
            const id = $(this).attr('data-id');

            if (is_folder) {
                folder_ids.push(id);
            } else {
                entity_ids.push(id);
            }
        });

        if (confirm(l.js_common_are_you_sure)) {
            document.location.href = $(this).attr('data-route')
                + '&folder_ids=' + folder_ids.join(',')
                + '&entity_ids=' + entity_ids.join(',')
            ;
        }
    });

    $(document).keyup(function (e) {
        const $selectedLink = getSelectedElements();
        const $selectedLinkLast = getSelectedElements().last();
        const $selectedLi = $selectedLink.parents('li:eq(0)');
        const $selectedLiLast = $selectedLinkLast.parents('li:eq(0)');

        if (e.key === "Escape") {
            $('.dirview .new-folder').addClass('hidden');
            $('.dirview .renaming').removeClass('renaming');
            clearSelection();
        }

        if ($('.renaming input:focus').length > 0) {
            return;
        }

        if (e.code === "Space") {
            renameExplrItem($selectedLi);
        } else if ($selectedLink.length) {
            const $prevLi = $selectedLi.prev('li:visible');
            const $nextLi = $selectedLiLast.next('li:visible');
            const verticalNeighbors = getAboveBelowElement($selectedLi);
            const clearIfNoMeta = function () {
                if (!e.metaKey && !e.ctrlKey && !e.shiftKey) {
                    clearSelection()
                }
            };

            if (e.key === "Enter") {
                $selectedLink.trigger('dblclick');
            } else if (e.key === "ArrowLeft" && $prevLi.length) {
                clearIfNoMeta();
                selectEpxlrLink($prevLi.find('.explr-link'));
            } else if (e.key === "ArrowRight" && $nextLi.length) {
                clearIfNoMeta();
                selectEpxlrLink($nextLi.find('.explr-link'));
            } else if (e.key === "ArrowUp" && verticalNeighbors.above) {
                clearIfNoMeta();
                selectEpxlrLink(verticalNeighbors.above.find('.explr-link'));
            } else if (e.key === "ArrowDown" && verticalNeighbors.below) {
                clearIfNoMeta();
                selectEpxlrLink(verticalNeighbors.below.find('.explr-link'));
            } else if (e.key === "Backspace") {
                if ($('.explr-item-delete:visible').length) {
                    $('.explr-item-delete:visible').click();
                }
                if ($('.explr-items-delete:visible').length) {
                    $('.explr-items-delete:visible').click();
                }
            }
        } else if (e.key.indexOf('Arrow') === 0) {
            selectEpxlrLink($('.explr-dirview li:visible:eq(0)').find('.explr-link'));
        }
    });

    // Explorer item selection
    $(document).on('mousedown', '.selectable-zone', startSelection);

    $(document).on('click', 'a.explr-link', function (event) {
        event.preventDefault();
        const $link = $(this);

        if (event.shiftKey && lastClicked) {
            handleShiftClick($link);
        } else if (event.metaKey || event.ctrlKey) {
            handleCmdCtrlClick($link);
        } else {
            clearSelection();
            selectEpxlrLink($link);
        }
        lastClicked = $link;
    });

    $(document).on('click', 'a.explr-pick-element', function (event) {
        event.preventDefault();
        const callback = $(this).attr('data-callback');

        if (callback) {
            window[callback]($(this));
        }
    });

    $(document).on('dblclick', 'a.explr-link', function (event) {
        event.preventDefault();
        $(this).off('click');
        const href = $(this).attr('href');
        const callback = $(this).attr('data-callback');

        if (callback) {
            window[callback]($(this));
        } else if ($(this).attr('target') === '_blank') {
            window.open(href);
        } else {
            window.location.href = href;
        }
    });

    $(document).on('click', function (event) {
        const $parentClickable = $(event.target).parents('a, button');
        if ($parentClickable.length === 0 && !isMajorSelection()) {
            clearSelection();
        }
    });

    $(document).on('click', '.modal-explr-picker .explr-pick-folder', function () {
        $(this).parents('li:eq(0)').find('.explr-toggler').click();
    });

    $(document).on('click', '.modal-explr-picker .explr-pick-element', function () {
        onPickedElement(JSON.parse($(this).parents('li:eq(0)').attr('data-entity-json')));
        hidePicker();
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