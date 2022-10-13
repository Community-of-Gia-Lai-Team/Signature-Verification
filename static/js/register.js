let dragAreaHTML = $(".drag-area").html();
var userData = new FormData();

history.scrollRestoration = "manual";
$(document).ready(function(){
    $(this).scrollTop(0);
});

$(document).on("click", ".button", function () {
    var parentClass = $(this).parent().closest("div");
    parentClass.children(".file_upload").click();
});

$(document).on("change", ".file_upload", function () {
    var dropArea = $(this).parent().closest("div");
    var file = dropArea.children(".file_upload").prop("files")[0];
    dropArea.addClass("active");
    displayFile(dropArea, file);
});

$(".next__btn").on("click", function () {
    var name = $("#name").val();
    var email = $("#email").val();
    var pattern = /^\b[A-Z0-9._%-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b$/i;

    if (name.length > 0 && email.length > 0) {
        if (!pattern.test(email)) {
            Swal.fire({
                icon: "error",
                title: "Oops...",
                text: "Invalid email",
            });
        }
        userData.append("name", name);
        userData.append("email", email);
        $(".user-info").removeClass("current-item");
        $(".upload-sig").addClass("current-item");
        $("html").animate(
            {
                scrollTop: $(".container").offset().top,
            },
            1000
        );
    } else if (!name.length) {
        Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Please fill in your name",
        });
    } else if (!email.length) {
        Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Please fill in your email!",
        });
    }
});

$(document).on("dragover", ".drag-area", function (e) {
    e.preventDefault();
    $(this).addClass("active");
    $(this).children(".header").text("Release to Upload");
});

$(document).on("dragleave", ".drag-area", function () {
    $(this).removeClass("active");
    $(this).children(".header").text("Drag & Drop");
});

$(document).on("drop", ".drag-area", function (e) {
    e.preventDefault();
    var dropArea = $(this);
    var file = e.originalEvent.dataTransfer.files[0];
    $(this).children(".file_upload")[0].files = e.originalEvent.dataTransfer.files;
    displayFile(dropArea, file);
});

function displayFile(dropArea, file) {
    var dragText = dropArea.children(".header");
    let fileType = file.type;
    let validExtensions = ["image/jpeg", "image/jpg", "image/png"];

    if (validExtensions.includes(fileType)) {
        let fileReader = new FileReader();
        fileReader.onload = () => {
            let fileURL = fileReader.result;
            let imgTag = `<img src="${fileURL}" alt="">`;
            let uploadTag = dropArea.children(".file_upload");
            dropArea.html(imgTag);
            dropArea.append('<i class="fas fa-trash-alt"></i>');
            dropArea.append(uploadTag);
            // dropArea.append(uploadTag);
        };
        fileReader.readAsDataURL(file);
    } else {
        Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Not supported this file type!",
        });
        dropArea.children(".file_upload")[0].val("");
        dropArea.removeClass("active");
        dragText.text("Drag & Drop");
    }
}

$(".upload_form").on("submit", function (e) {
    e.preventDefault();
    var numFile = 0;

    $.each($(".file_upload"), function (index, tag) {
        if (tag.files.length){
            userData.append("images", tag.files[0]);
            numFile++;
        }
        
    });
    if (numFile == 5) {
        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'info',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes'
          }).then((result) => {
            if (result.isConfirmed) {
                Swal.fire({
                    title: "Processing...",
                    html: "Please wait a moment",
                    allowOutsideClick: false,
                });
                Swal.showLoading();

                $.ajax({
                    type: "POST",
                    url: "signature/register",
                    data: userData,
                    processData: false,
                    contentType: false,
                }).done((response) => {
                    Swal.close();
                    if (response.code == 200) {
                        Swal.fire({
                            icon: "success",
                            title: "Success",
                            text: "Registered signatures successfully!",
                            allowOutsideClick: false,
                        });
                        $(".upload-sig").removeClass("current-item");
                    } else if (response.code == 404) {
                        Swal.fire({
                            icon: "error",
                            title: "Oops...",
                            text: "???????",
                        });
                    }
                });
            }
          })
    } else {
        Swal.fire({
            icon: "error",
            title: "Oops...",
            text: "Please upload 5 images of your signature!",
        });
    }
});

$(document).on("click", ".fa-trash-alt", function () {
    var parentClass = $(this).parent().closest("div");
    parentClass.children(".file_upload").val("");
    parentClass.removeClass("active");
    parentClass.html(dragAreaHTML);
});
