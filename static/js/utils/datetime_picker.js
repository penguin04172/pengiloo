const newDateTimePicker = function(id, defaultTime) {
    new tempusDominus.TempusDominus(document.getElementById(id), {
        defaultDate: defaultTime,
        display: {
            components: {
                seconds: true,
            },
            icons: {
                type: "icons",
                time: "bi bi-clock",
                date: "bi bi-calendar-week",
                up: "bi bi-arrow-up",
                down: "bi bi-arrow-down",
                previous: "bi bi-chevron-left",
                next: "bi bi-chevron-right",
                today: "bi bi-calendar-check",
                clear: "bi bi-trash",
                close: "bi bi-x",
            },
            },
            localization: {
            format: "yyyy-MM-dd hh:mm:ss T",
            locale: "en",
        },
    });
}