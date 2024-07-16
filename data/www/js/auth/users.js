jQuery(document).ready(function ($) {
    const main = function () {

    };

    $(document).on('click', '.user-add', function () {
        showModal('modal-user-add');
        $('.modal-user-add input[type=text]:eq(0)').focus().select();
    });

    $(document).on('click', '.user-edit', function () {
        const user = JSON.parse($(this).parents('.user-item:eq(0)').attr('data-entity'));
        showModal('modal-user-edit');
        $('.modal-user-edit input:visible:eq(0)').focus().select();
        $('#user-edit-enabled').prop('checked', user.enabled);
        $('#user-edit-username').val(user.username);
        $('#user-edit-id').val(user.id);
    });

    main();
});