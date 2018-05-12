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
                'startDate': moment(startDate, 'YYYY-MM-DD').format('w'),
                'studentID': studentID,
                'password': password,
                'classCaptcha': classCaptcha
            },
            'success': function (data) {
                if (data['code'] === 200) {
                    zlalert.alertSuccess('课表添加成功');
                } else {
                    zlalert.alertInfo(data['message']);
                }
            },
            'fail': function (error) {
                zlalert.alertNetworkError();
            }
        })
    });

   // 邮箱添加部分提交AJAX
    $('#emailSubmit').click(function (event) {
        event.preventDefault();
        var email = $('#new-email').val();

        zlajax.post({
            'url': '/emailSetting/',
            'data': {
                'email': email
            },
            'success': function (data) {
                if (data['code'] === 200) {
                    zlalert.alertSuccess('邮箱添加成功');
                } else {
                    zlalert.alertInfo(data['message'])
                }
            },
            'fail': function (error) {
                zlalert.alertNetworkError();
            }
        });
    })


});