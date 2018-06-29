$(function () {
    /* 保存实验报告 */
    var options = {
        success: showSaveResponse,
        restForm: false
    };

    // 调用ajaxForm()
    $('#lw_save-form').ajaxForm(options);

    // 保存后
    function showSaveResponse(responseText, statusText) {
        if (responseText.success) {
            $('#autosave-time').text(responseText.message);
        } else {
            $('#autosave-time').text(responseText.message);
        }
        $('#submit').attr('disabled', false);
    }
});