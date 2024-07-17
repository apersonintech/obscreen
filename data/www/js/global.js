const $modalsRoot = $('.modals');
const $pickersRoot = $('.pickers');

const isset = function (obj){
	return obj !== undefined && obj !== null;
};

const showModal = function (modalClass) {
    $modalsRoot.removeClass('hidden').find('form').trigger('reset');
    $modalsRoot.find('.modal').addClass('hidden');
    $modalsRoot.find('.modal.' + modalClass).removeClass('hidden');
};

const showPickers = function (modalClass, callback) {
    $pickersRoot.removeClass('hidden').find('form').trigger('reset');
    $pickersRoot.find('.modal').addClass('hidden');
    $pickersRoot.find('.modal.' + modalClass).removeClass('hidden');
    onPickedElement = callback;
};

const hideModal = function () {
    $modalsRoot.addClass('hidden').find('form').trigger('reset');
};

const hidePicker = function () {
    $pickersRoot.addClass('hidden').find('form').trigger('reset');
};

const hideDropdowns = function () {
    $('.dropdown').removeClass('dropdown-show');
};

const showToast = function (text) {
    const $toast = $(".toast");
    $toast.addClass('show');
    $toast.text(text);
    setTimeout(function() {
        $toast.removeClass('show');
    }, 3000);
};

jQuery(document).ready(function ($) {
    $('.dropdown .trigger').on('click', function (event) {
        event.stopPropagation();
        var $dropdown = $(this).closest('.dropdown');
        var $menu = $dropdown.find('ul.dropdown-menu');

        $('.dropdown').not($dropdown).removeClass('dropdown-show');
        $dropdown.toggleClass('dropdown-show');

        // Adjust dropdown position to prevent overflow
        var triggerHeight = $(this).outerHeight() + 20;
        var triggerOffset = $(this).offset();
        var menuWidth = $menu.outerWidth();
        var windowWidth = $(window).width();
        var menuHeight = $menu.outerHeight();
        var windowHeight = $(window).height();

        // Set the top position
        $menu.css('top', triggerHeight + 'px');

        // Adjust the left position to prevent overflow
        if (triggerOffset.left + menuWidth > windowWidth) {
            $menu.css('left', 'auto');
            $menu.css('right', 0);
        } else {
            $menu.css('left', 0);
            $menu.css('right', 'auto');
        }

        // Adjust the top position to prevent bottom overflow
        var menuOffset = $menu.offset();
        if (menuOffset.top + menuHeight > windowHeight) {
            $menu.css('top', -menuHeight + 'px');
        } else {
            $menu.css('top', triggerHeight + 'px');
        }
    });

    $(document).on('click', function () {
        $('.dropdown').removeClass('dropdown-show');
    });

    $(window).on('resize', function () {
        $('.dropdown.dropdown-show .trigger').trigger('click');
    });

    $(document).on('click', '.modal-close', function () {
        hideModal();
    });

    $(document).on('click', '.picker-close', function () {
        hidePicker();
    });

    $(document).on('focus', 'input.disabled', function () {
        $(this).blur();
    });

    $(document).keyup(function (e) {
        if (e.key === "Escape") {
            hideDropdowns();

            if ($('.pickers .modal:visible').length) {
                hidePicker();
                return;
            }

            hideModal();
        }
    });

    // Link protection
    $(document).on('click', '.protected', function (e) {
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

    // Datetime and owner tracking
    $(document).on('click', '.item-utrack', function () {
        const entity = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-entity-utrack');
        $('#entity-utrack-created-by').val(entity.created_by);
        $('#entity-utrack-updated-by').val(entity.updated_by);
        $('#entity-utrack-created-at').val(prettyTimestamp(entity.created_at * 1000));
        $('#entity-utrack-updated-at').val(prettyTimestamp(entity.updated_at * 1000));
    });

    setTimeout(function () {
        $('.alert-timeout').remove();
    }, 3000);

    if ($('.edit-page').length) {
        const $firstInputText = $('input[type=text]:eq(0)');
        if ($firstInputText.length) {
            $firstInputText.focus();
        }
    }

    $(document).on('click', '.copy-link', function (e) {
        e.preventDefault();
        const $input = $('#' + $(this).attr('data-target-id'));
        $input.select();
        $input[0].setSelectionRange(0, 99999);
        document.execCommand("copy");

        if (navigator.clipboard) {
            navigator.clipboard.writeText($input.val());
        }

        showToast(l.js_common_copied);
    });
});

