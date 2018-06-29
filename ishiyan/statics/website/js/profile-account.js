$(function () {
    /* 账号密码 */

    // 调用ajaxForm()
    $('#lw_account-form').ajaxForm({
        success: function (responseText) {
            if (responseText.success) {
                $('#lw_account-success').css('display','block');
                $('#lw_account-success > div').text(responseText.message);
            }
            else if (responseText.success === false) {
                $('#lw_account-error').css('display','block');
                $('#lw_account-error > div').text(responseText.message);
            }
            $('#account-submit').attr('disabled', false);
        },
        restForm: true
    });

    /* 基本信息 */

    // 调用ajaxForm()
    $('#lw_profile-form').ajaxForm({
        beforeSubmit: function (formArr) {
            for (let i = 0; i < formArr.length; i++) {
                if (formArr[i].name === 'name' && formArr[i].value === "") {
                    $('#lw_profile-error').css('display','block');
                    $('#lw_profile-error > div').text('昵称不能为空。');
                    return false;
                }
                else {
                    $('#lw_profile-error').css('display','none');
                }
            }
        },
        success: function (responseText) {
            if (responseText.success) {
                $('#lw_profile-success').css('display','block');
                $('#lw_profile-success > div').text(responseText.message);
            }
            else if (responseText.success === false) {
                $('#lw_profile-error').css('display','block');
                $('#lw_profile-error > div').text(responseText.message);
            }
            $('#profile-submit').attr('disabled', false);
        },
        restForm: true
    });
});