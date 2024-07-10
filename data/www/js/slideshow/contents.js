jQuery(document).ready(function ($) {
    const inputTypeUpdate = function () {
        const $el = $('#content-add-type');
        const value = $el.val();
        const $selectedOption = $('#content-add-type option[value='+value+']');
        const inputType = $el.find('option').filter(function (i, el) {
            return $(el).val() === value;
        }).data('input');

        $('.content-add-object-input').each(function() {
            const active = $(this).attr('id') === 'content-add-object-input-' + inputType;

            if ($(this).is('input[type=file]')) {
                $(this).prop('disabled', !active).prop('required', active);
                $(this).parents('label:eq(0)').toggleClass('hidden', !active);
            } else {
                $(this).prop('disabled', !active).prop('required', active).toggleClass('hidden', !active);
            }
        });

        const optionAttributes = $selectedOption.get(0).attributes;
        const color = optionAttributes['data-color'].value;
        $('.object-label-add').html(optionAttributes['data-object-label'].value);
        $('.object-icon-add').attr('class', 'object-icon-add fa ' + optionAttributes['data-icon'].value);
        $('.tab-select .widget').attr('class', 'widget ' + ('border-' + color) + ' ' + color);
        $('.modal:visible button[type=submit]').attr('class', 'btn ' + ('btn-' + color));
    };

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

    $(document).on('click', '.explr-item-edit', function () {
        const $item = $('.explr-dirview .highlight-clicked');
        const is_folder = $item.attr('data-folder') === '1';

        if (is_folder) {
            $item.addClass('renaming');
            $item.find('input').focus().select();
        } else {
            document.location.href = $(this).attr('data-content-route').replace('!c!', $item.attr('data-id'));
        }
    });

    $(document).on('click', '.explr-item-delete', function () {
        const $item = $('.explr-dirview .highlight-clicked');
        const is_folder = $item.attr('data-folder') === '1';
        let route = document.location.href;

        if (is_folder) {
            route = $(this).attr('data-folder-route') + '?id=' + $item.attr('data-id');
        } else {
            route = $(this).attr('data-content-route') + '?id=' + $item.attr('data-id');
        }

        if (confirm(l.js_slideshow_content_delete_confirmation)) {
            document.location.href = route;
        }
    });

    $(document).on('click', '.content-edit', function () {
        const content = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-content-edit');



        $('.modal-content-edit input:visible:eq(0)').focus().select();
        $('#content-edit-id').val(content.id);
    });

    $(document).on('submit', '.modal-content-add form', function () {
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
