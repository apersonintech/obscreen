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