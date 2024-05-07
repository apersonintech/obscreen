jQuery(document).ready(function ($) {
    const $modalsRoot = $('.modals');

    const showModal = function (modalClass) {
        $modalsRoot.removeClass('hidden').find('form').trigger('reset');
        $modalsRoot.find('.modal').addClass('hidden');
        $modalsRoot.find('.modal.' + modalClass).removeClass('hidden');
    };

    const hideModal = function () {
        $modalsRoot.addClass('hidden').find('form').trigger('reset');
    };

    const main = function () {

    };

    $(document).on('click', '.modal-close', function () {
        hideModal();
    });

    $(document).on('click', '.variable-edit', function () {
        const variable = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));

        if (variable['selectables']) {
            var $select = $('<select id="variable-edit-value" name="value" required="required"></select>');
            $.each(variable['selectables'], function(index, option) {
                $select.append($('<option></option>').val(option.key).html(option.label));
            });
            $('#variable-edit-value').replaceWith($select);
        } else {
            $('#variable-edit-value').replaceWith('<input type="text" name="value" id="variable-edit-value" required="required" />');
        }

        showModal('modal-variable-edit');
        $('.modal-variable-edit input:visible:eq(0)').focus().select();
        $('#variable-edit-name').val(variable.name);
        $('#variable-edit-description').html(variable.description);
        $('#variable-edit-value').val(variable.value);
        $('#variable-edit-id').val(variable.id);
    });

    $(document).keyup(function (e) {
        if (e.key === "Escape") {
            hideModal();
        }
    });

    main();
});