jQuery(document).ready(function ($) {
    const getId = function ($el) {
        return $el.is('tr') ? $el.attr('data-level') : $el.parents('tr:eq(0)').attr('data-level');
    };

    const updateTable = function () {
        $('table').each(function () {
            if ($(this).find('tbody tr.content-item:visible').length === 0) {
                $(this).find('tr.empty-tr').removeClass('hidden');
            } else {
                $(this).find('tr.empty-tr').addClass('hidden');
            }
        });
    };

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
                 $(this).prop('disabled', !active);
                $(this).parents('label:eq(0)').toggleClass('hidden', !active);
            } else {
                $(this).prop('disabled', !active).toggleClass('hidden', !active);
            }
        });

        $('.object-label-add').html($selectedOption.get(0).attributes['data-object-label'].value);
        $('.object-icon-add').attr('class', 'object-icon-add fa ' + $selectedOption.get(0).attributes['data-icon'].value)
    };

    const initExplr = function () {
        $('.explr').explr({
            classesPlus: 'fa fa-plus',
            classesMinus: 'fa fa-minus',
            onLoadFinish: function ($tree) {
                $tree.removeClass('hidden');
            }
        });
    };

    const initDrags = function () {
        $(".draggable").draggable({
            revert: "invalid",
        });
        $(".droppable").droppable({
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
    };

    const main = function () {
        initExplr();
        initDrags();
    };

    $(document).on('change', '.modal input[type=file]', function() {
        const file = $(this).val().replace(/\\/g, '/').split('/').slice(-1);
        $(this).parents('label:eq(0)').find('input[type=text]').val(file);
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

        let location = content.location;

        if (content.type == 'youtube') {
            location = 'https://www.youtube.com/watch?v=' + content.location;
        }

        $('.modal-content-edit input:visible:eq(0)').focus().select();
        $('#content-edit-name').val(content.name);
        $('#content-edit-type').val(content.type);
        $('#content-edit-location').val(location).prop('disabled', !content.is_editable);
        $('#content-edit-id').val(content.id);
    });

    $(document).on('click', '.content-delete', function () {
        if (confirm(l.js_slideshow_content_delete_confirmation)) {
            const $tr = $(this).parents('tr:eq(0)');
            $tr.remove();
            updateTable();
            $.ajax({
                method: 'DELETE',
                url: '/slideshow/content/delete',
                headers: {'Content-Type': 'application/json'},
                data: JSON.stringify({id: getId($(this))}),
            });
        }
    });

    $(document).on('submit', '.modal-content-add form', function () {
        $(this).find('button[type=submit]').addClass('hidden');
        $(this).find('.btn-loading').removeClass('hidden');
    });

    main();
});
