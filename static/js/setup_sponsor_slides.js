const renewSponsorSlides = (sponsorSlides) => {
    let endHTML = `
            <div class="row mb-3">
                <div class="col-7">
                    <input type="hidden" id="Id0" value="" />
                    <div class="row mb-1" name="imagetoggle0">
                        <label for="image0" class="col-5 form-label">Image File Name</label>
                        <div class="col-7">
                            <input type="text" name="image" id="image0" placeholder="image.svg" class="form-control" />
                        </div>
                    </div>
                    <div class="row mb-1 d-none" name="imagetoggle0">
                        <label for="line10" class="col-5 form-label">Line 1 Text</label>
                        <div class="col-7">
                            <input type="text" name="line1" id="line10" placeholder="Really" class="form-control" />
                        </div>
                    </div>
                    <div class="row mb-1 d-none" name="imagetoggle0">
                        <label for="line20" class="col-5 form-label">Line 2 Text</label>
                        <div class="col-7">
                            <input type="text" name="line2" id="line20" placeholder="Tech" class="form-control" />
                        </div>
                    </div>
                    <div class="row mb-1">
                        <label for="subtitle0" class="col-5 form-label">Subtitle Text</label>
                        <div class="col-7">
                            <input type="text" name="subtitle" id="subtitle0" placeholder="Sponsor" class="form-control" />
                        </div>
                    </div>
                    <div class="row mb-1">
                        <label for="displayTimeSec0" class="col-5 form-label">Display Time (s)</label>
                        <div class="col-7">
                            <input type="number" name="displayTimeSec" id="displayTimeSec0" value="10" class="form-control" />
                        </div>
                    </div>
                </div>
                <div class="col-5">
                    <button type="button" class="btn btn-primary mb-1" onclick="saveSponsorSlide('0')">Save</button>
                    <br />
                    <button type="button" class="btn btn-secondary" onclick="toggleImageText('0')">Toggle image/text</button>
                </div>
            </div>
        `;

    let sponsorSlidesHTML = sponsorSlides.map(sponsorSlide => {
        return `
            <div class="row mb-3">
                <div class="col-7">
                    <input type="hidden" id="Id${sponsorSlide.id}" value="${sponsorSlide.id}" />
                    <div class="row mb-1 ${sponsorSlide.line1 == '' && sponsorSlide.line2 == '' ?'':'d-none'}" name="imagetoggle${sponsorSlide.id}">
                        <label for="image${sponsorSlide.id}" class="col-5 form-label">Image File Name</label>
                        <div class="col-7">
                            <input type="text" name="image" id="image${sponsorSlide.id}" placeholder="image.svg" class="form-control" value="${sponsorSlide.image}" />
                        </div>
                    </div>
                    <div class="row mb-1 ${sponsorSlide.line1 == '' && sponsorSlide.line2 == '' ?'d-none':''}" name="imagetoggle${sponsorSlide.id}">
                        <label for="line1${sponsorSlide.id}" class="col-5 form-label">Line 1 Text</label>
                        <div class="col-7">
                            <input type="text" name="line1" id="line1${sponsorSlide.id}" placeholder="Really" class="form-control" value="${sponsorSlide.line1}" />
                        </div>
                    </div>
                    <div class="row mb-1 ${sponsorSlide.line1 == '' && sponsorSlide.line2 == '' ?'d-none':''}" name="imagetoggle${sponsorSlide.id}">
                        <label for="line2${sponsorSlide.id}" class="col-5 form-label">Line 2 Text</label>
                        <div class="col-7">
                            <input type="text" name="line2" id="line2${sponsorSlide.id}" placeholder="Tech" class="form-control" value="${sponsorSlide.line2}" />
                        </div>
                    </div>
                    <div class="row mb-1">
                        <label for="subtitle${sponsorSlide.id}" class="col-5 form-label">Subtitle Text</label>
                        <div class="col-7">
                            <input type="text" name="subtitle" id="subtitle${sponsorSlide.id}" placeholder="Sponsor" class="form-control" value="${sponsorSlide.subtitle}" />
                        </div>
                    </div>
                    <div class="row mb-1">
                        <label for="displayTimeSec${sponsorSlide.id}" class="col-5 form-label">Display Time (s)</label>
                        <div class="col-7">
                            <input type="number" name="displayTimeSec" id="displayTimeSec${sponsorSlide.id}" placeholder="10" class="form-control" value="${sponsorSlide.display_time_sec}" />
                        </div>
                    </div>
                </div>
                <div class="col-5">
                    <button type="button" class="btn btn-primary mb-1" onclick="saveSponsorSlide('${sponsorSlide.id}')">Save</button>
                    <button type="button" class="btn btn-primary mb-1" onclick="reorderSponsorSlide('${sponsorSlide.id}', true)"><i class="bi-arrow-up")></i></button>
                    <br />
                    <button type="button" class="btn btn-danger mb-1" onclick="deleteSponsorSlide('${sponsorSlide.id}')">Delete</button>
                    <button type="button" class="btn btn-primary mb-1" onclick="reorderSponsorSlide('${sponsorSlide.id}', false)"><i class="bi-arrow-down"></i></button>
                    <br />
                    <button type="button" class="btn btn-secondary" onclick="toggleImageText('${sponsorSlide.id}')">Toggle image/text</button>
                </div>
            </div>
        `
    }).join("\n");

    $('#sponsorSlidesContainer').innerHTML = sponsorSlidesHTML + endHTML;
}

const constructData = (sponsorSlideId, moveup) => {
    return {
        data:{
            id: parseInt($(`#Id${sponsorSlideId}`).value),
            image: $(`#image${sponsorSlideId}`).value,
            line1: $(`#line1${sponsorSlideId}`).value,
            line2: $(`#line2${sponsorSlideId}`).value,
            subtitle: $(`#subtitle${sponsorSlideId}`).value,
            display_time_sec: parseInt($(`#displayTimeSec${sponsorSlideId}`).value),
        },
        action: "save",
    }
}

const saveSponsorSlide = (sponsorSlideId) => {
    postData("/api/setup/sponsor_slides", constructData(sponsorSlideId))
    .then((data) => {
        renewSponsorSlides(data);
    });
}

const reorderSponsorSlide = (sponsorSlideId, moveup) => {
    postData("/api/setup/sponsor_slides", {data: {id: parseInt($(`#Id${sponsorSlideId}`).value)}, action: moveup?"reorder_up":"reorder_down"})
    .then((data) => {
        renewSponsorSlides(data);
    });
}

const toggleImageText = (sponsorSlideId) => {
    $$(`[name=imagetoggle${sponsorSlideId}]`).forEach(element => {
        element.classList.toggle("d-none");
    });
}

const deleteSponsorSlide = (sponsorSlideId) => {
    deleteData("/api/setup/sponsor_slides/" + sponsorSlideId)
    .then((data) => {
        renewSponsorSlides(data);
    });
}

getData("/api/setup/sponsor_slides")
.then((data) => {
    renewSponsorSlides(data);
});