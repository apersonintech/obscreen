jQuery(document).ready(function ($) {
    const $tableActive = $('table.active-users');
    const $tableInactive = $('table.inactive-users');

    const getId = function ($el) {
        return $el.is('tr') ? $el.attr('data-level') : $el.parents('tr:eq(0)').attr('data-level');
    };

    const updateTable = function () {
        $('table').each(function () {
            if ($(this).find('tbody tr.user-item:visible').length === 0) {
                $(this).find('tr.empty-tr').removeClass('hidden');
            } else {
                $(this).find('tr.empty-tr').addClass('hidden');
            }
        });
    };

    const main = function () {

    };

    $(document).on('change', 'input[type=checkbox]', function () {
        var $input = $(this);

        $.ajax({
            url: '/auth/user/toggle',
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify({id: getId($(this)), enabled: $(this).is(':checked')}),
            method: 'POST',
            success: function(data) {
                const $tr = $input.parents('tr:eq(0)').remove().clone();

                if ($input.is(':checked')) {
                    $tableActive.append($tr);
                } else {
                    $tableInactive.append($tr);
                }

                updateTable();
            },
            error: function(data) {
                $input.prop('checked', true);
                $('.alert-error').html(data.responseJSON.message).removeClass('hidden');
            }
        });
    });

    $(document).on('change', '#user-add-type', function () {
        const value = $(this).val();
        const inputType = $(this).find('option').filter(function (i, el) {
            return $(el).val() === value;
        }).data('input');

        $('.user-add-object-input')
            .addClass('hidden')
            .prop('disabled', true)
            .filter('#user-add-object-input-' + inputType)
            .removeClass('hidden')
            .prop('disabled', false)
        ;
    });

    $(document).on('click', '.user-add', function () {
        showModal('modal-user-add');
        $('.modal-user-add input:eq(0)').focus().select();
    });

    $(document).on('click', '.user-edit', function () {
        const user = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-user-edit');
        $('.modal-user-edit input:visible:eq(0)').focus().select();
        $('#user-edit-username').val(user.username);
        $('#user-edit-id').val(user.id);
    });

    $(document).on('click', '.user-delete', function () {
        if (confirm(l.js_auth_user_delete_confirmation)) {
            const $tr = $(this).parents('tr:eq(0)');
            $.ajax({
                method: 'DELETE',
                url: '/auth/user/delete',
                headers: {'Content-Type': 'application/json'},
                data: JSON.stringify({id: getId($(this))}),
                success: function(data) {
                    $tr.remove();
                    updateTable();
                },
                error: function(data) {
                    $('.alert-error').html(data.responseJSON.message).removeClass('hidden');
                }
            });
        }
    });

    main();
});