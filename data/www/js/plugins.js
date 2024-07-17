jQuery(document).ready(function ($) {
    const main = function () {

    };

    $(document).on('click', '.variable-edit', function () {
        const $dataHolder = $(this).is('tr') ? $(this) : $(this).parents('tr:eq(0)');
        const variable = JSON.parse($dataHolder.attr('data-entity'));

        if (variable['selectables']) {
            var $select = $('<select id="variable-edit-value" name="value" required="required"></select>');
            $.each(variable['selectables'], function(index, option) {
                $select.append($('<option></option>').val(option.key).html(option.label));
            });
            $('#variable-edit-value').replaceWith($select);
        } else {
            var type = variable.type === 'int' ? 'number' : 'text';
            $('#variable-edit-value').replaceWith('<input type="'+type+'" name="value" id="variable-edit-value" required="required" />');
        }

        showModal('modal-variable-edit');
        $('.modal-variable-edit input:visible:eq(0)').focus().select();
        $('#variable-edit-name').val(variable.name);
        $('#variable-edit-description').html(variable.description);
        $('#variable-edit-description-edition').html(variable.description_edition).toggleClass('hidden', variable.description_edition === '');
        $('#variable-edit-value').val(variable.value);
        $('#variable-edit-id').val(variable.id);
    });

    main();
});