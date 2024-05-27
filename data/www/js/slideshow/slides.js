jQuery(document).ready(function ($) {
    const $tableActive = $('table.active-slides');
    const $tableInactive = $('table.inactive-slides');
    const $modalsRoot = $('.modals');

    const validateCronDateTime = function(cronExpression) {
        const pattern = /^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\*\s+(\d+)$/;
        return pattern.test(cronExpression);
    };

    const getCronDateTime = function(cronExpression) {
        const [minutes, hours, day, month, _, year] = cronExpression.split(' ');
        return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')} ${hours.padStart(2, '0')}:${minutes.padStart(2, '0')}`;
    };

    const prettyTimestamp = function(timestamp) {
        const d = new Date(timestamp);
        return `${d.getFullYear()}-${String(d.getMonth()).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')} `
    }

    const loadDateTimePicker = function($els) {
        $els.each(function() {
            var $el = $(this);
            $el.val('');
            const pickr = $el.flatpickr({
                enableTime: true,
                time_24hr: true,
                allowInput: false,
                allowInvalidPreload: false,
                dateFormat: 'Y-m-d H:i',
                onChange: function(selectedDates, dateStr, instance) {
                    const d = selectedDates[0];
                    const $target = $el.parents('.widget:eq(0)').find('.target');
                    $target.val(
                        d ? `${d.getMinutes()} ${d.getHours()} ${d.getDate()} ${(d.getMonth() + 1)} * ${d.getFullYear()}` : ''
                    );
                }
            });
            $el.addClass('hidden');
        })
    };

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

    const inputTypeUpdate = function () {
        const $el = $('#slide-add-type');
        const value = $el.val();
        const inputType = $el.find('option').filter(function (i, el) {
            return $(el).val() === value;
        }).data('input');

        $('.slide-add-object-input')
            .addClass('hidden')
            .prop('disabled', true)
            .filter('#slide-add-object-input-' + inputType)
            .removeClass('hidden')
            .prop('disabled', false)
        ;
    };

    const inputSchedulerUpdate = function() {
        const $modal = $('.modal-slide:visible');
        const $scheduleStartGroup = $modal.find('.slide-schedule-group');
        const $scheduleEndGroup = $modal.find('.slide-schedule-end-group');
        const $durationGroup = $modal.find('.slide-duration-group');

        const $triggerStart = $scheduleStartGroup.find('.trigger');
        const $triggerEnd = $scheduleEndGroup.find('.trigger');
        const $targetCronFieldStart = $scheduleStartGroup.find('.target');
        const $targetCronFieldEnd = $scheduleEndGroup.find('.target');

        const $datetimepickerStart = $scheduleStartGroup.find('.datetimepicker');
        const $datetimepickerEnd = $scheduleEndGroup.find('.datetimepicker');

        const isCronStart = $triggerStart.val() === 'cron';
        const isCronEnd = $triggerEnd.val() === 'cron';
        const isDatetimeStart = $triggerStart.val() === 'datetime';
        const isDatetimeEnd = $triggerEnd.val() === 'datetime';
        const isLoopStart = $triggerStart.val() === 'loop';
        const isDurationEnd = $triggerEnd.val() === 'duration';
        const flushValueStart = isLoopStart;
        const flushValueEnd = isDurationEnd;

        $targetCronFieldStart.toggleClass('hidden', !isCronStart);
        $targetCronFieldEnd.toggleClass('hidden', !isCronEnd);
        $datetimepickerStart.toggleClass('hidden', !isDatetimeStart);
        $datetimepickerEnd.toggleClass('hidden', !isDatetimeEnd);

        $durationGroup.toggleClass('hidden', !isLoopStart && !isDurationEnd);
        $scheduleEndGroup.toggleClass('hidden', isLoopStart);

        $durationGroup.find('.widget input').prop('required', $durationGroup.is(':visible'));

        if (flushValueStart) {
            $targetCronFieldStart.val('');
            $datetimepickerStart.val('');
        }

        if (flushValueEnd) {
            $targetCronFieldEnd.val('');
            $datetimepickerEnd.val('');
        }
    };

    const main = function () {
        $("table").tableDnD({
            dragHandle: 'td a.slide-sort',
            onDrop: updatePositions
        });
    };

    $(document).on('change', 'select.playlist-picker', function () {
        document.location.href = $(this).val();
    });

    $(document).on('change', '.slide-item input[type=checkbox]', function () {
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

    $(document).on('change', '.modal-slide select.trigger', function () {
        inputSchedulerUpdate();
    });

    $(document).on('change', '#slide-add-type', inputTypeUpdate);

    $(document).on('click', '.modal-close', function () {
        hideModal();
    });

    $(document).on('click', '.slide-add', function () {
        showModal('modal-slide-add');
        loadDateTimePicker($('.modal-slide-add .datetimepicker'))
        inputTypeUpdate();
        inputSchedulerUpdate();
        $('.modal-slide-add input:eq(0)').focus().select();
    });

    $(document).on('click', '.slide-utrack', function () {
        const slide = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-slide-utrack');
        $('#slide-utrack-created-by').val(slide.created_by);
        $('#slide-utrack-updated-by').val(slide.updated_by);
        $('#slide-utrack-created-at').val(prettyTimestamp(slide.created_at * 1000));
        $('#slide-utrack-updated-at').val(prettyTimestamp(slide.updated_at * 1000));
    });

    $(document).on('click', '.slide-edit', function () {
        const slide = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-slide-edit');
        loadDateTimePicker($('.modal-slide-edit .datetimepicker'))

        const hasCron = slide.cron_schedule && slide.cron_schedule.length > 0;
        const hasDateTime = hasCron && validateCronDateTime(slide.cron_schedule);

        const hasCronEnd = slide.cron_schedule_end && slide.cron_schedule_end.length > 0;
        const hasDateTimeEnd = hasCronEnd && validateCronDateTime(slide.cron_schedule_end);

        let location = slide.location;

        if (slide.type == 'youtube') {
            location = 'https://www.youtube.com/watch?v=' + slide.location;
        }

        $('.modal-slide-edit input:visible:eq(0)').focus().select();
        $('#slide-edit-name').val(slide.name);
        $('#slide-edit-type').val(slide.type);
        $('#slide-edit-location').val(location).prop('disabled', !slide.is_editable);
        $('#slide-edit-duration').val(slide.duration);

        $('#slide-edit-cron-schedule').val(slide.cron_schedule).toggleClass('hidden', !hasCron || hasDateTime);
        $('#slide-edit-cron-schedule-trigger').val(hasDateTime ? 'datetime' : (hasCron ? 'cron' : 'loop'));

        $('#slide-edit-cron-schedule-end').val(slide.cron_schedule_end).toggleClass('hidden', !hasCronEnd || hasDateTimeEnd);
        $('#slide-edit-cron-schedule-end-trigger').val(hasDateTimeEnd ? 'datetime' : (hasCronEnd ? 'cron' : 'duration'));

        $('#slide-edit-cron-schedule-datetimepicker').toggleClass('hidden', !hasDateTime).val(
            hasDateTime ? getCronDateTime(slide.cron_schedule) : ''
        );

        $('#slide-edit-cron-schedule-end-datetimepicker').toggleClass('hidden', !hasDateTimeEnd).val(
            hasDateTimeEnd ? getCronDateTime(slide.cron_schedule_end) : ''
        );
        $('#slide-edit-id').val(slide.id);
        inputSchedulerUpdate();
    });

    $(document).on('click', '.slide-delete', function () {
        if (confirm(l.js_slideshow_slide_delete_confirmation)) {
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
