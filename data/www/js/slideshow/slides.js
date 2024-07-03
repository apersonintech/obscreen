jQuery(document).ready(function ($) {
    const $tableActive = $('table.active-slides');
    const $tableInactive = $('table.inactive-slides');

    const loadDateTimePicker = function($els) {
        const d = new Date();

        $els.each(function() {
            var $el = $(this);
            $el.flatpickr({
                enableTime: true,
                time_24hr: true,
                allowInput: false,
                allowInvalidPreload: false,
                dateFormat: 'Y-m-d H:i',
                defaultHour: d.getHours(),
                defaultMinute: d.getMinutes(),
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
        const $modal = $('.modal-slide:visible');
        const $el = $('#slide-add-type');
        const value = $el.val();
        const inputType = $el.find('option').filter(function (i, el) {
            return $(el).val() === value;
        }).data('input');

        if ($modal.find('.picker').length === 0) {
            $modal.find('.upload').find('input, select').prop('disabled', false);
        }

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
        const $isNotificationGroup = $modal.find('.slide-notification-group');

        const $triggerStart = $scheduleStartGroup.find('.trigger');
        const $triggerEnd = $scheduleEndGroup.find('.trigger');
        const $targetCronFieldStart = $scheduleStartGroup.find('.target');
        const $targetCronFieldEnd = $scheduleEndGroup.find('.target');
        const $targetDuration = $durationGroup.find('input');

        const $datetimepickerStart = $scheduleStartGroup.find('.datetimepicker');
        const $datetimepickerEnd = $scheduleEndGroup.find('.datetimepicker');
        const $isNotification = $isNotificationGroup.find('.trigger');

        const isNotification = $isNotification.prop('checked');
        let isLoopStart = $triggerStart.val() === 'loop';
        let isCronStart = $triggerStart.val() === 'cron';

        function updateScheduleChoices(isNotification, isLoopStart, isCronStart) {
            let scheduleStartChoices = $.extend({}, schedule_start_choices);
            let scheduleEndChoices = $.extend({}, schedule_end_choices);

            if (!isNotification || isLoopStart) {
                delete scheduleStartChoices['cron'];
                delete scheduleEndChoices['duration'];
            }

            if (isNotification) {
                delete scheduleStartChoices['loop'];
                delete scheduleEndChoices['stayloop'];

                if (isCronStart) {
                    delete scheduleEndChoices['datetime'];
                }
            }

            return { scheduleStartChoices, scheduleEndChoices };
        }

        function applyChoices() {
            const { scheduleStartChoices, scheduleEndChoices } = updateScheduleChoices(isNotification, isLoopStart, isCronStart);
            recreateSelectOptions($triggerStart, scheduleStartChoices);
            recreateSelectOptions($triggerEnd, scheduleEndChoices);
        }

        applyChoices();

        isLoopStart = $triggerStart.val() === 'loop';
        isCronStart = $triggerStart.val() === 'cron';

        const isCronEnd = $triggerEnd.val() === 'cron';
        const isDatetimeStart = $triggerStart.val() === 'datetime';
        const isDatetimeEnd = $triggerEnd.val() === 'datetime';
        const isStayloopEnd = $triggerEnd.val() === 'stayloop';
        const isDurationEnd = $triggerEnd.val() === 'duration';

        const flushValueStart = isLoopStart;
        const flushValueEnd = isLoopStart || isStayloopEnd || isDurationEnd;
        const flushDuration = isNotification && isDatetimeEnd;

        function toggleVisibility() {
            $targetCronFieldStart.toggleClass('hidden', !isCronStart);
            $targetCronFieldEnd.toggleClass('hidden', !isCronEnd);
            $datetimepickerStart.toggleClass('hidden', !isDatetimeStart);
            $datetimepickerEnd.toggleClass('hidden', !isDatetimeEnd);

            $durationGroup.toggleClass('hidden', isNotification && isDatetimeEnd);
            $scheduleEndGroup.toggleClass('hidden', isLoopStart);

            $durationGroup.find('.widget input').prop('required', $durationGroup.is(':visible'));
        }

        function flushValues() {
            if (flushValueStart) {
                $targetCronFieldStart.val('');
                $datetimepickerStart.val('');
            }

            if (flushValueEnd) {
                $targetCronFieldEnd.val('');
                $datetimepickerEnd.val('');
            }

            if (flushDuration) {
                $targetDuration.val('1');
            }
        }

        toggleVisibility();
        flushValues();
        applyChoices();
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

    $(document).on('change', '.modal-slide select.trigger, .modal-slide input.trigger', function () {
        inputSchedulerUpdate();
    });

    $(document).on('change', '#slide-add-type', inputTypeUpdate);

    $(document).on('click', '.picker button', function () {
        const $parent = $(this).parents('.modal-slide-add');
        $parent.find('.picker').remove();
        $parent.find('.upload').removeClass('hidden');
        inputTypeUpdate();
    });

    $(document).on('click', '.slide-add', function () {
        showModal('modal-slide-add');
        loadDateTimePicker($('.modal-slide-add .datetimepicker'))
        inputTypeUpdate();
        inputSchedulerUpdate();
        inputContentUpdate();
        $('.modal-slide-add input:eq(0)').focus().select();
    });

    const inputContentUpdate = function(content_id) {
        const $modal = $('.modal-slide:visible');
        const $group = $modal.find('.slide-content-id-group');
        const $select = $group.find('select');
        recreateSelectOptions($select, contents);
        if (content_id) {
            $select.val(content_id);
        }
    };

    $(document).on('click', '.slide-edit', function () {
        const slide = JSON.parse($(this).parents('tr:eq(0)').attr('data-entity'));
        showModal('modal-slide-edit');

        const hasCron = slide.cron_schedule && slide.cron_schedule.length > 0;
        const hasDateTime = hasCron && validateCronDateTime(slide.cron_schedule);

        const hasCronEnd = slide.cron_schedule_end && slide.cron_schedule_end.length > 0;
        const hasDateTimeEnd = hasCronEnd && validateCronDateTime(slide.cron_schedule_end);
        const isNotification = slide.is_notification;

        inputContentUpdate(slide.content_id);

        $('.modal-slide-edit input:visible:eq(0)').focus().select();
        $('#slide-edit-duration').val(slide.duration);
        $('#slide-edit-is-notification').prop('checked', isNotification);

        $('#slide-edit-cron-schedule').val(slide.cron_schedule).toggleClass('hidden', !hasCron || hasDateTime);
        $('#slide-edit-cron-schedule-trigger').val(hasDateTime ? 'datetime' : (hasCron ? 'cron' : 'loop'));

        $('#slide-edit-cron-schedule-end').val(slide.cron_schedule_end).toggleClass('hidden', !hasCronEnd || hasDateTimeEnd);
        $('#slide-edit-cron-schedule-end-trigger').val(hasDateTimeEnd ? 'datetime' : (hasCronEnd ? 'cron' : (isNotification ? 'duration' : 'stayloop')));

        $('#slide-edit-cron-schedule-datetimepicker').toggleClass('hidden', !hasDateTime).val(
            hasDateTime ? getCronDateTime(slide.cron_schedule) : ''
        );

        $('#slide-edit-cron-schedule-end-datetimepicker').toggleClass('hidden', !hasDateTimeEnd).val(
            hasDateTimeEnd ? getCronDateTime(slide.cron_schedule_end) : ''
        );
        $('#slide-edit-id').val(slide.id);
        loadDateTimePicker($('.modal-slide-edit .datetimepicker'));

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

    $(document).on('submit', '.modal-slide-add form', function () {
        $(this).find('button[type=submit]').addClass('hidden');
        $(this).find('.btn-loading').removeClass('hidden');
    });

    main();
});
