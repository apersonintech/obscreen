jQuery(document).ready(function ($) {
    const $tableActive = $('table.active-slides');
    const $tableInactive = $('table.inactive-slides');
    const $modalsRoot = $('.modals');

    const getId = function ($el) {
        return $el.is('tr') ? $el.attr('data-level') : $el.parents('tr:eq(0)').attr('data-level');
    };

    const updateTable = function () {
        $('table').each(function () {
            if ($(this).find('tbody tr.slide-item:visible').length === 0) {
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
        $('.slide-item').each(function (index) {
            positions[getId($(this))] = index;
        });

        $.ajax({
            method: 'POST',
            url: '/slideshow/slide/position',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify(positions),
        });
    };

    const main = function () {
        $("table").tableDnD({
            dragHandle: 'td a.slide-sort',
            onDrop: updatePositions
        });
    };

    $(document).on('change', 'input[type=checkbox]', function () {
        $.ajax({
            url: '/slideshow/slide/toggle',
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

    $(document).on('change', '#slide-add-type', function () {
        const value = $(this).val();
        const inputType = $(this).find('option').filter(function (i, el) {
            return $(el).val() === value;
        }).data('input');

        $('.slide-add-object-input')
            .addClass('hidden')
            .prop('disabled', true)
            .filter('#slide-add-object-input-' + inputType)
            .removeClass('hidden')
            .prop('disabled', false)
        ;
    });

    $(document).on('click', '.modal-close', function () {
        hideModal();
    });

    $(document).on('click', '.slide-add', function () {
        showModal('modal-slide-add');
        $('.modal-slide-add input:eq(0)').focus().select();
    });

    $(document).on('click', '.slide-edit', function () {
        const slide = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-slide-edit');
        $('.modal-slide-edit input:visible:eq(0)').focus().select();
        $('#slide-edit-name').val(slide.name);
        $('#slide-edit-type').val(slide.type);
        $('#slide-edit-location').val(slide.location);
        $('#slide-edit-duration').val(slide.duration);
        $('#slide-edit-id').val(slide.id);
    });

    $(document).on('click', '.slide-delete', function () {
        if (confirm(l.slideshow_slide_delete_confirmation)) {
            const $tr = $(this).parents('tr:eq(0)');
            $tr.remove();
            updateTable();
            $.ajax({
                method: 'DELETE',
                url: '/slideshow/slide/delete',
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