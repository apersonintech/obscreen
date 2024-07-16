const prettyTimestamp = function(timestamp) {
    const d = new Date(timestamp);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')} `
};

const getCronDateTime = function(cronExpression) {
    const [minutes, hours, day, month, _, year] = cronExpression.split(' ');
    return `${year}-${month.padStart(2, '0')}-${day.padStart(2, '0')} ${hours.padStart(2, '0')}:${minutes.padStart(2, '0')}`;
};

const validateCronDateTime = function(cronExpression) {
    const pattern = /^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\*\s+(\d+)$/;
    return pattern.test(cronExpression);
};

const cronToDateTimeObject = function(cronExpression) {
    if (!validateCronDateTime(cronExpression)) {
        return null;
    }

    let [minutes, hours, day, month, _, year] = cronExpression.split(' ');

    minutes = parseInt(minutes, 10);
    hours = parseInt(hours, 10);
    day = parseInt(day, 10);
    month = parseInt(month, 10) - 1;
    year = parseInt(year, 10);

    return new Date(year, month, day, hours, minutes);
};

const modifyDate = function(date, seconds) {
    const clone = new Date(date.getTime());
    clone.setSeconds(clone.getSeconds() + seconds);
    return clone;
};

const recreateSelectOptions = function($selectElement, options) {
    if (!$selectElement.is('select')) {
        throw new Error("Element is not a <select>");
    }

    const selectedValue = $selectElement.val();
    $selectElement.empty();

    $.each(options, function(key, label) {
        $selectElement.append($('<option>', {
            value: key,
            html: label
        }));
    });

    if ($selectElement.find(`option[value="${selectedValue}"]`).length > 0) {
        $selectElement.val(selectedValue);
    } else {
        $selectElement.prop('selectedIndex', 0);
    }
};

const secondsToHHMMSS = function (seconds) {
    if (!seconds) {
        return "";
    }
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
};
