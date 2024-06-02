const prettyTimestamp = function(timestamp) {
    const d = new Date(timestamp);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}:${String(d.getSeconds()).padStart(2, '0')} `
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