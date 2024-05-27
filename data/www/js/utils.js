const validateCronDateTime = function(cronExpression) {
    const pattern = /^(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+\*\s+(\d+)$/;
    return pattern.test(cronExpression);
};

const cronToDateTimeObject = function(cronExpression) {
    const parts = cronExpression.split(' ');

    [minutes, hours, day, month, _, year] = expression.split(' ')
        return "{}-{}-{} at {}:{}".format(
            year,
            month.zfill(2),
            day.zfill(2),
            hours.zfill(2),
            minutes.zfill(2)
        )
}