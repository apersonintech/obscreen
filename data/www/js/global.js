const $modalsRoot = $('.modals');

const showModal = function (modalClass) {
    $modalsRoot.removeClass('hidden').find('form').trigger('reset');
    $modalsRoot.find('.modal').addClass('hidden');
    $modalsRoot.find('.modal.' + modalClass).removeClass('hidden');
};

const hideModal = function () {
    $modalsRoot.addClass('hidden').find('form').trigger('reset');
};

jQuery(document).ready(function ($) {
    $(document).on('click', '.modal-close', function () {
        hideModal();
    });

    $(document).keyup(function (e) {
        if (e.key === "Escape") {
            hideModal();
        }
    });

    $(document).on('click', '.protected', function(e) {
        e.preventDefault();
        e.stopPropagation();

        if (confirm(l.js_common_are_you_sure)) {
            if ($(this).is('a')) {
                if ($(this).attr('target') == '_blank') {
                    window.open($(this).attr('href'));
                } else {
                    document.location.href = $(this).attr('href');
                }
            }
        }

        return false;
    });

    $(document).on('click', '.item-utrack', function () {
        const entity = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-entity-utrack');
        $('#entity-utrack-created-by').val(entity.created_by);
        $('#entity-utrack-updated-by').val(entity.updated_by);
        $('#entity-utrack-created-at').val(prettyTimestamp(entity.created_at * 1000));
        $('#entity-utrack-updated-at').val(prettyTimestamp(entity.updated_at * 1000));
    });

});