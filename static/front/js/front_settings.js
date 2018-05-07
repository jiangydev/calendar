$(function () {
    // 课表设置部分提交AJAX
    $('#classSubmit').click(function (event) {
        event.preventDefault();
        var startDate = $('#start-date').val();
        var studentID = $('#studentID').val();
        var password = $('#classPwd').val();
        var classCaptcha = $('#classCaptcha').val();

        zlajax.post({
            'url': '/classSchedule/',
            'data': {
                'startDate': startDate,
                'studentID': studentID,
                'password': password,
                'classCaptcha': classCaptcha
            },
            'success': function (data) {
                if (data['code'] === 200) {
                    zlalert.alertSuccessToast('课表添加成功');
                } else {
                    zlalert.alertInfo(data['message']);
                }
            },
            'fail': function (error) {
                zlalert.alertNetworkError();
            }
        })
    });

    // 更新验证码
    function refreshCaptcha(event) {
        var $self = $('#classCaptchaImg');
        var src = $self.attr('src');
        var newsrc = zlparam.setParam(src, 'xx', Math.ceil(Math.random()*10000));
        $self.attr('src', newsrc);
    }
    $('#refreshCaptcha').click(refreshCaptcha);
    refreshCaptcha();


});