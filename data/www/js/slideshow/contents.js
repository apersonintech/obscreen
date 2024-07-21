jQuery(document).ready(function ($) {
    const inputTypeUpdate = function () {
        const $el = $('form:visible .type-select');
        const $form = $el.parents('form:eq(0)');
        const value = $el.val();
        const $selectedOption = $el.find('option[value='+value+']');
        const inputType = $el.find('option').filter(function (i, el) {
            return $(el).val() === value;
        }).data('input');

        $form.find('.content-object-input').each(function() {
            const $input = $(this);
            const active = $input.attr('data-input-type') === inputType;
            const $holder = $input.parents('.from-group-condition:eq(0)');
            $holder.find('input, select, textarea').prop('disabled', !active).prop('required', active).toggleClass('hidden', !active);
            $holder.toggleClass('hidden', !active);
        });

        const optionAttributes = $selectedOption.get(0).attributes;
        const color = optionAttributes['data-color'].value;
        $form.find('.object-label:visible').html(optionAttributes['data-object-label'].value);
        $('.type-icon').attr('class', 'type-icon fa ' + optionAttributes['data-icon'].value);
        $('.tab-select .widget').attr('class', 'widget ' + ('border-' + color) + ' ' + color);
        $form.find('button[type=submit]').attr('class', 'btn ' + ('btn-' + color));
    };

    const main = function () {

    };

    $(document).on('change', '.modal input[type=file]', function() {
        const file = $(this).val().replace(/\\/g, '/').split('/').slice(-1)[0];
        $(this).parents('label:eq(0)').find('input[type=text]').val(file);

        if ($('#content-add-name').val().trim().length === 0) {
            const fileWithoutExt = file.split('.').slice(0, -1).join('.');
            $('#content-add-name').val(fileWithoutExt);
        }
    });

    $(document).on('change', '#content-add-type', inputTypeUpdate);

    $(document).on('click', '.folder-add', function () {
        $('.dirview .new-folder').removeClass('hidden');
        $('.page-content').animate({scrollTop: 0}, 0);
        $('.dirview input').focus();
    });

    $(document).on('click', '.content-add', function () {
        showModal('modal-content-add');
        inputTypeUpdate();
        $('.modal-content-add input:eq(0)').focus().select();
    });

    $(document).on('submit', '.modal-content-add form', function () {
        const $modal = $(this).parents('.modal:eq(0)');
        $modal.find('button[type=submit]').addClass('hidden');
        $modal.find('.btn-loading').removeClass('hidden');
    });

    main();
});
