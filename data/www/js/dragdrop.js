jQuery(function ($) {

    const main = function () {
        fileUpload();
    };

    const fileUpload = function () {
        $('.btn-super-upload').each(function () {
            const $button = $(this);
            const $input = $(this).find('input[type=file]');
            $input.fileupload({
                url: $(this).attr('data-route'),
                dropZone: $('body'),
                formData: {},
                dataType: 'json',
                add: function (e, data) {
                    const $alert = $('.alert-danger');
                    const $bar = $button.find('.progress-bar');
                    $bar.css('width', '0%');
                    $button.addClass('uploading').removeClass('btn-info btn-super-upload').addClass('btn-naked btn-super-upload-busy');
                    $alert.addClass('hidden').text('');
                    data.submit();
                },
                progressall: function (e, data) {
                    const progress = parseInt(data.loaded / data.total * 100, 10);
                    const $bar = $button.find('.progress-bar');
                    const $percent = $button.find('.percent');
                    $bar.css('width', progress + '%');
                    $percent.text(progress + '%');
                },
                always: function (e, data) {
                    const response = data._response.jqXHR;
                    $button.removeClass('uploading').removeClass('btn-naked btn-super-upload-busy').addClass('btn-info btn-super-upload');
                    if (response.status != 200) {
                        const $alert = $('.alert-danger').removeClass('hidden');
                        if (response.status == 413) {
                            $alert.text(l.js_common_http_error_413);
                        } else {
                            $alert.text(l.js_common_http_error_occured.replace('%code%', response.status));
                        }
                    } else {
                        document.location.reload();
                    }
                }
            });
        });
    };

    main();

    $(document).on('click', '.btn-super-upload', function (e) {
        $(this).find('input[type=file]')[0].click();
    });

    $(document).on('dragenter', 'body', function () {
        $(this).addClass('dragenter');
        return false;
    });

    $(document).on('dragover', 'body', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).addClass('dragover');
        return false;
    });

    $(document).on('dragleave', 'body', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('dragenter dragover');
        return false;
    });

    $(document).on('drop', 'body', function (e) {
        e.preventDefault();
        e.stopPropagation();
        $(this).removeClass('dragenter dragover');

        const $dz = $('.dropzone:visible');

        if (isset($dz.attr('data-handle-drop') && $dz.attr('data-handle-drop') === '1')) {
            const $inputTarget = $("#" + $dz.attr('data-related-input'));
            const droppedFiles = e.originalEvent.dataTransfer.files;
            $inputTarget.prop("files", droppedFiles).trigger('change');
        }

        return false;
    });
});

