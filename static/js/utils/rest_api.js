const $ = selector => document.querySelector(selector);
const $$ = selector => document.querySelectorAll(selector);

function getData(url) {
    return fetch(url)
        .then(response => response.json())
        .then(data => data)
}

function postData(url, data) {
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
        .then(response => response.json())
        .then(data => data)
}

function deleteData(url) {
    return fetch(url, {
        method: 'DELETE',
    })
        .then(response => response.json())
        .then(data => data)
}