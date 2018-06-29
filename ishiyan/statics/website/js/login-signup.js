$(function () {
    /* 登录 */
    var options = {
        beforeSubmit: showLoginRequest,
        success: showLoginResponse,
        restForm: true
    };

    // 调用ajaxForm()
    $('#lw_login-form').ajaxForm(options);

    // 提交前
    function showLoginRequest(formData, jqForm, options) {
        for (let i = 0; i < formData.length; i++) {
            if (formData[i].name === 'usr' && formData[i].value === ""
             || formData[i].name === 'pwd' && formData[i].value === "") {
                $('#lw_error').css('display','block');
                $('#lw_error > div').text('用户名或密码不能为空。');
                return false;
            }
        }
        $('#submit').attr('disabled', true);
    }

    // 提交后
    function showLoginResponse(responseText, statusText) {
        if (responseText.success) {
            window.location.href = '/';
        } else {
            $('#lw_error').css('display','block');
            $('#lw_error > div').text(responseText.message);
        }
        $('#submit').attr('disabled', false);
    }

    /* 注册 */
    var opts = {
        beforeSubmit: showSignupRequest,
        success: showSignupResponse,
        restForm: true
    };

    var reg = /^(((13[0-9]{1})|(14[0-9]{1})|(17[0-9]{1})|(15[0-3]{1})|(15[4-9]{1})|(18[0-9]{1})|(199))+\d{8})$/;

    $('#lw_signup-form').ajaxForm(opts);

    // 提交前
    function showSignupRequest(formData, jqForm, opts) {
        for (let i = 0; i < formData.length; i++) {
            if (formData[i].name === 'usr' && formData[i].value === "") {
                $('#lw_signup-error').css('display','block');
                $('#lw_signup-error > div').text('用户名不能为空。');
                return false;
            }
            if (formData[i].name === 'pwd') {
                if (formData[i].value === "") {
                    $('#lw_signup-error').css('display','block');
                    $('#lw_signup-error > div').text('密码不能为空。');
                    return false;
                }
                else if (formData[i].value.length < 6) {
                    $('#lw_signup-error').css('display','block');
                    $('#lw_signup-error > div').text('密码至少为6位。');
                    return false;
                }
            }
            if (formData[i].name === 'email' && formData[i].value === "") {
                $('#lw_signup-error').css('display','block');
                $('#lw_signup-error > div').text('邮箱不能为空。');
                return false;
            }
            if (formData[i].name === 'verify' && formData[i].value === "") {
                $('#lw_signup-error').css('display','block');
                $('#lw_signup-error > div').text('请先验证邮箱。');
                return false;
            }
            if (formData[i].name === 'phone') {
                if (formData[i].value === "") {
                    $('#lw_signup-error').css('display','block');
                    $('#lw_signup-error > div').text('手机号码不能为空。');
                    return false;
                }
                else if (formData[i].value.length < 11) {
                    $('#lw_signup-error').css('display','block');
                    $('#lw_signup-error > div').text('请输入11位手机号码。');
                    return false;
                }
                else if (!reg.test(formData[i].value)) {
                    $('#lw_signup-error').css('display','block');
                    $('#lw_signup-error > div').text('请输入有效的手机号码。');
                    return false;
                }
            }
        }
        if ($('input[type="checkbox"]').is(':checked') === false) {
            $('#lw_signup-error').css('display','block');
            $('#lw_signup-error > div').text('请同意爱实验隐私协议。');
            return false;
        }
        else if ($('input[type="checkbox"]').is(':checked') === true) {
            $('#lw_signup-error').css('display','none');
        }
        $('#signup-submit').attr('disabled', true);
    }

    // 提交后
    function showSignupResponse(responseText, statusText) {
        if (responseText.success) {
            window.location.href = '/';
        } else {
            $('#lw_signup-error').css('display','block');
            $('#lw_signup-error > div').text(responseText.message);
        }
        $('#signup-submit').attr('disabled', false);
    }

    // 获取焦点
    inputFocus($('#usr'),$('#lw_usr'),$('#lw_usr-point'));
    inputBlur($('#usr'),$('#lw_usr'),$('#lw_usr-point'));

    inputFocus($('#pwd'),$('#lw_pwd'),$('#lw_pwd-point'));
    inputBlur($('#pwd'),$('#lw_pwd'),$('#lw_pwd-point'));

    inputFocus($('#email'),$('#lw_email'),$('#lw_email-point'));
    inputBlur($('#email'),$('#lw_email'),$('#lw_email-point'));

    inputFocus($('#phone'),$('#lw_phone'),$('#lw_tel-point'));
    inputBlur($('#phone'),$('#lw_phone'),$('#lw_tel-point'));

    function inputFocus(inputDom1,inputDom2,inputDom3) {
    	inputDom1.focus(function () {
    	    inputDom2.css('margin-bottom','0');
            inputDom3.css('display','block');
        });
    }
    function inputBlur(inputDom1,inputDom2,inputDom3) {
    	inputDom1.blur(function () {
    	    inputDom2.css('margin-bottom','20px');
            inputDom3.css('display','none');
        });
    }
});