const dropArea = $(".drag-area");
const dragText = $(".header");
let dragAreaHTML = $(".drag-area").html();
let file;

$(document).on("click", ".button", function () {
    $(".file_upload").click();
});

$(document).on("change", ".file_upload", function () {
    file = this.files[0];
    dropArea.addClass("active");
    displayFile();
});

dropArea.on("dragover", (event) => {
    event.preventDefault();
    dropArea.addClass("active");
    dragText.text("Release to Upload");
});

dropArea.on("dragleave", () => {
    dropArea.removeClass("active");
    dragText.text("Drag & Drop");
});

dropArea.on("drop", (event) => {
    event.preventDefault();
    file = event.originalEvent.dataTransfer.files[0];
    displayFile();
});

function displayFile() {
    let fileType = file.type;

    let validExtensions = ["image/jpeg", "image/jpg", "image/png"];

    if (validExtensions.includes(fileType)) {
        let fileReader = new FileReader();
        fileReader.onload = () => {
            let fileURL = fileReader.result;
            let imgTag = `<img src="${fileURL}" alt="">`;
            dropArea.html(imgTag);
        };
        fileReader.readAsDataURL(file);
        $("#clear_btn").css({ display: "inline-block" });
        $("#clear_btn").hover(
            function () {
                $(this).css("background-color", "#CD5C5C");
            },
            function () {
                $(this).css("background-color", "#1683ff");
            }
        );
    } else {
        Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Not supported this file type!",
        });
        file = null;
        dropArea.removeCLASS("active");
        dragText.text("Drag & Drop");
    }
}

$(".upload_form").on("submit", function (e) {
    e.preventDefault();
    Swal.fire({
        title: "Processing...",
        html: "Please wait a moment",
    });
    Swal.showLoading();

    if (file) {
        var formData = new FormData();
        formData.append("image", file);
        $.ajax({
            type: "POST",
            url: "/recognize",
            data: formData,
            processData: false,
            contentType: false,
        }).done((response) => {
            Swal.close();
            if (response.code == 200) {
                Swal.fire({
                    icon: "success",
                    title: "Success",
                    text: "Signature recognized successfully!",
                });
                $(".show_results").css({ 'display': 'table', 'margin-top': '150px'});
                $('.signature_detected').html('');
                $.each(response.data, function (index, val) {
                    $(".signature_detected").append(`<div class="signature_prop" id="signature_prop_${index}"></div>`);
                    $(".signature_detected").append(`<div class="signature_img" id="signature_img_${index}"></div>`);
                    $(`#signature_img_${index}`).append(`<img src="${val[0]}?v=${$.now()}" width="224px" height="112px">`);
                    $(".signature_detected").append(`<div class="predict_info" id="info_${index}"></div>`);
                    $(`#info_${index}`).append(`<span>Signer: ${val[1]}</span>`);
                    if (val[1].toString() != "New class") {
                        $(`#info_${index}`).append(`</br>`);
                        $(`#info_${index}`).append(`<span>Confident: ${val[2]}%</span>`);
                    }
                    $(`#signature_prop_${index}`).append($(`#signature_img_${index}`));
                    $(`#signature_prop_${index}`).append($(`#info_${index}`));
                });
                $('html').animate({
                  scrollTop: $('.show_results').offset().top,
                },1000);
            } else if (response.code == 404) {
                Swal.fire({
                    icon: "error",
                    title: "Oops...",
                    text: "Not found signature!",
                });
            }
        });
    } else {
        Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Please upload your image first!",
        });
    }
});

$("#clear_btn").on("click", function () {
    file = null;
    $(".drag-area").removeClass("active");
    $(".drag-area").html(dragAreaHTML);
    $(this).css({ display: "none" });
});
