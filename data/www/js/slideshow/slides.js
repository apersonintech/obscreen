jQuery(document).ready(function ($) {
    const loadDateTimePicker = function ($els, timeOnly) {
        const d = new Date();
        $els.each(function () {
            var $el = $(this);

            const options = {
                enableTime: true,
                time_24hr: true,
                allowInput: false,
                noCalendar: false,
                allowInvalidPreload: false,
                dateFormat: 'Y-m-d H:i',
                defaultHour: d.getHours(),
                defaultMinute: d.getMinutes(),
                onChange: function (selectedDates, dateStr, instance) {
                    const d = selectedDates[0];
                    const $target = $el.parents('.widget:eq(0)').find('.target');
                    $target.val(
                        d ? `${d.getMinutes()} ${d.getHours()} ${d.getDate()} ${(d.getMonth() + 1)} * ${d.getFullYear()}` : ''
                    );
                }
            };

            if (timeOnly) {
                // options['noCalendar'] = true;
            }

            $el.flatpickr(options);
            $el.addClass('hidden');
        });
    };

    const getId = function ($el) {
        return $el.hasClass('slide-item') ? $el.attr('data-level') : $el.parents('.slide-item:eq(0)').attr('data-level');
    };

    const updatePositions = function (table, row) {
        const positions = {};
        $('.slide-item').each(function (index) {
            positions[getId($(this))] = index;
        });

        $.ajax({
            method: 'POST',
            url: route_slide_position,
            headers: {'Content-Type': 'application/json'},
            data: JSON.stringify(positions),
        });
    };

    const inputSchedulerUpdate = function () {
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
        const $isNotification = $modal.find('#slide-edit-is-notification');

        const isNotification = $isNotification.val() === '1';
        let isLoopStart = $triggerStart.val() === 'loop';
        let isCronStart = $triggerStart.val() === 'cron';

        const choice_map = choices_map[isNotification ? 'notification' : 'normal']
        recreateSelectOptions($triggerStart, Object.keys(choice_map).reduce((obj, key) => {
            obj[key] = choices_translations[key];
            return obj;
        }, {}));
        recreateSelectOptions($triggerEnd, choice_map[$triggerStart.val()]);

        isLoopStart = $triggerStart.val() === 'loop';
        isCronStart = $triggerStart.val() === 'cron';

        const isCronEnd = $triggerEnd.val() === 'cron';
        const isInWeekMomentStart = $triggerStart.val() === 'inweek';
        const isDatetimeStart = $triggerStart.val() === 'datetime';
        const isDatetimeEnd = $triggerEnd.val() === 'datetime';
        const isStayloopEnd = $triggerEnd.val() === 'stayloop';
        const isDurationEnd = $triggerEnd.val() === 'duration';

        const flushValueStart = isLoopStart;
        const flushValueEnd = isLoopStart || isStayloopEnd || isDurationEnd;
        const flushDuration = isNotification && isDatetimeEnd;
        const datetimepickerWithCalendar = !isInWeekMomentStart;

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

        loadDateTimePicker($modal.find('.datetimepicker'), datetimepickerWithCalendar);
        toggleVisibility();
        flushValues();
    };


    const main = function () {
        $("ul.slides").sortable({
            handle: 'a.slide-sort',
            update: updatePositions
        });
    };

    $(document).on('change', '.modal-slide select.trigger, .modal-slide input.trigger', function () {
        inputSchedulerUpdate();
    });

    $(document).on('click', '.slide-add', function () {
        showModal($(this).attr('data-modal'));
        const $modal = $('.modal-slide:visible');
        inputSchedulerUpdate();
        inputContentUpdate();
        $modal.find('input[type=text]:visible:eq(0)').focus().select();
    });

    $(document).on('click', '.content-explr-picker', function () {
        showPickers('modal-content-explr-picker', function (content) {
            inputContentUpdate(content)
        });
    });

    const inputContentUpdate = function (content) {
        const $modal = $('.modal-slide:visible');
        const $group = $modal.find('.slide-content-id-group');
        const $inputLabel = $group.find('.target-label');
        const $inputId = $group.find('.target');
        const $actionShow = $group.find('.slide-content-show');

        if (content === undefined || !content.id) {
            $inputLabel.val('');
            $inputId.val('');
            $actionShow.addClass('hidden');
            return;
        }

        $inputLabel.val(content.name);
        $inputId.val(content.id);
        $actionShow.removeClass('hidden');
    };

    $(document).on('click', '.slide-content-show', function () {
        window.open($(this).attr('data-route').replace('__id__', $(this).parents('.widget:eq(0)').find('.target').val()));
    });

    $(document).on('click', '.slide-edit', function () {
        const slide = JSON.parse($(this).parents('.slide-item:eq(0)').attr('data-entity'));
        showModal($(this).attr('data-modal'));
        const $modal = $('.modal-slide:visible');

        const hasCron = slide.cron_schedule && slide.cron_schedule.length > 0;
        const hasDateTime = hasCron && validateCronDateTime(slide.cron_schedule);

        const hasCronEnd = slide.cron_schedule_end && slide.cron_schedule_end.length > 0;
        const hasDateTimeEnd = hasCronEnd && validateCronDateTime(slide.cron_schedule_end);
        const isNotification = slide.is_notification;

        inputContentUpdate(slide.content);

        $modal.find('input[type=text]:visible:eq(0)').focus().select();
        $modal.find('#slide-edit-duration').val(slide.duration);
        $modal.find('#slide-edit-enabled').prop('checked', slide.enabled);

        $modal.find('#slide-edit-cron-schedule').val(slide.cron_schedule).toggleClass('hidden', !hasCron || hasDateTime);
        $modal.find('#slide-edit-cron-schedule-trigger').val(hasDateTime ? 'datetime' : (hasCron ? 'cron' : 'loop'));

        $modal.find('#slide-edit-cron-schedule-end').val(slide.cron_schedule_end).toggleClass('hidden', !hasCronEnd || hasDateTimeEnd);
        $modal.find('#slide-edit-cron-schedule-end-trigger').val(hasDateTimeEnd ? 'datetime' : (hasCronEnd ? 'cron' : (isNotification ? 'duration' : 'stayloop')));

        $modal.find('#slide-edit-cron-schedule-datetimepicker').toggleClass('hidden', !hasDateTime).val(
            hasDateTime ? getCronDateTime(slide.cron_schedule) : ''
        );

        $modal.find('#slide-edit-cron-schedule-end-datetimepicker').toggleClass('hidden', !hasDateTimeEnd).val(
            hasDateTimeEnd ? getCronDateTime(slide.cron_schedule_end) : ''
        );
        $modal.find('#slide-edit-id').val(slide.id);
        loadDateTimePicker($modal.find('.datetimepicker'));

        inputSchedulerUpdate();
    });

    $(document).on('click', '.slide-delete', function () {
        if (confirm(l.js_slideshow_slide_delete_confirmation)) {
            const $item = $(this).parents('.slide-item:eq(0)');
            if ($item.parents('ul:eq(0)').find('.slide-item').length === 1) {
                document.location.href = $(this).attr('data-route').replace('__id__', getId($(this)));
            } else {
                $item.remove();
                $.ajax({
                    method: 'DELETE',
                    url: $(this).attr('data-route').replace('__id__', getId($(this))),
                    headers: {'Content-Type': 'application/json'},
                    success: function (response) {
                        $('.playlist-item-' + response.playlist_id + ' .playlist-duration').html(secondsToHHMMSS(response.duration));
                    }
                });
            }
        }
    });

    $(document).on('submit', '.modal-slide form', function () {
        $(this).find('button[type=submit]').addClass('hidden');
        $(this).find('.btn-loading').removeClass('hidden');
    });

    main();
});
