const cron = (() => {
    const DAY_NAMES = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'];
    const DAY_ABBRS = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'];
    const MINUTE_CHOICES = Array.from({length: 60}, (_, i) => [`${i}`, `${i}`]);
    const HOUR_CHOICES = Array.from({length: 24}, (_, i) => [`${i}`, `${i}`]);
    const DOM_CHOICES = Array.from({length: 31}, (_, i) => [`${i + 1}`, `${i + 1}`]);
    const MONTH_CHOICES = Array.from({length: 12}, (_, i) => [`${i + 1}`, new Date(0, i).toLocaleString('en', { month: 'long' })]);
    const DOW_CHOICES = DAY_NAMES.map((day, index) => [`${index}`, day]);

    function toInt(value, allowDaynames = false) {
        if (typeof value === 'number' || (typeof value === 'string' && !isNaN(value))) {
            return parseInt(value, 10);
        } else if (allowDaynames && typeof value === 'string') {
            value = value.toLowerCase();
            const dayIndex = DAY_NAMES.indexOf(value);
            if (dayIndex !== -1) return dayIndex;
            const abbrIndex = DAY_ABBRS.indexOf(value);
            if (abbrIndex !== -1) return abbrIndex;
        }
        throw new Error('Failed to parse string to integer');
    }

    function parseArg(value, target, allowDaynames = false) {
        value = value.trim();
        if (value === '*') return true;
        let values = value.split(',').map(v => v.trim()).filter(v => v);

        for (let val of values) {
            try {
                if (toInt(val, allowDaynames) === target) {
                    return true;
                }
            } catch (error) {}

            if (val.includes('-')) {
                let step = 1;
                let start, end;
                if (val.includes('/')) {
                    [start, end] = val.split('-').map(part => part.trim());
                    [end, step] = end.split('/').map(part => toInt(part.trim(), allowDaynames));
                    start = toInt(start, allowDaynames);
                } else {
                    [start, end] = val.split('-').map(part => toInt(part.trim(), allowDaynames));
                }

                for (let i = start; i <= end; i += step) {
                    if (i === target) return true;
                }
                if (allowDaynames && start > end) {
                    for (let i = start; i < start + 7; i += step) {
                        if (i % 7 === target) return true;
                    }
                }
            }

            if (val.includes('/')) {
                let [v, interval] = val.split('/').map(part => part.trim());
                if (v !== '*') continue;
                if (target % toInt(interval, allowDaynames) === 0) {
                    return true;
                }
            }
        }

        return false;
    }

    function hasBeen(s, since, dt = new Date()) {
        since = new Date(since);
        dt = new Date(dt);

        if (dt < since) {
            throw new Error("The 'since' datetime must be before the current datetime.");
        }

        while (since <= dt) {
            if (isActive(s, since)) {
                return true;
            }
            since = new Date(since.getTime() + 60000);
        }

        return false;
    }

    function isActive(s, dt = new Date()) {
        let [minute, hour, dom, month, dow, year] = s.split(' ');
        let weekday = dt.getDay();

        return parseArg(minute, dt.getMinutes()) &&
               parseArg(hour, dt.getHours()) &&
               parseArg(dom, dt.getDate()) &&
               parseArg(month, dt.getMonth() + 1) &&
               parseArg(dow, weekday === 0 ? 6 : weekday - 1, true) &&
               (!year || (year && parseArg(year, dt.getFullYear())));
    }

    return {
        isActive
    };
})();