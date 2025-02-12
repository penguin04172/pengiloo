const renewBreaks = (breaks) => {
    let breaksHTML;
    if (breaks.length === 0) {
        breaksHTML = "<p>There are no breaks set up until playoff.</p>";
    }else {
        breaksHTML = breaks.map((b, index) => {
            return `
                <div class="row mb-3">
                    <h5>Break #${index + 1}</h5>
                    <input type="hidden" id="id${b.id}" value="${b.id}" />
                    <label class="col-3 form-label" for="description${b.id}">Description</label>
                    <div class="col-6">
                        <input type="text" name="description" id="description${b.id}" class="form-control" value="${b.description}" />
                    </div>
                    <div class="col-3">
                        <button type="button" class="btn btn-primary">Save</button>
                    </div>
                </div>
            `
        })
    }

    $('#breaksContainer').innerHTML = breaksHTML;
}

const saveBreak = (id, description) => {
    const data = {
        id: id,
        description: description,
    }

    postData('/api/setup/breaks', data)
    .then(data => {
        renewBreaks(data);
    })
}

getData('/api/setup/breaks')
.then(data => {
    renewBreaks(data);
})