$(function () {
    init_plugins();
    bind_functions();
});

/**
 * ============ 全局变量定义 ============
 */
var $sidebar = $('.sidebar'),
    $index = $('.index'),
    $list = $('.list'),
    $desc = $('.desc'),
    $calendar = $('#calendar'),
    $mask = $('.mask'),
    $index_greet = $('#index-greet'), // index中goodmorning部分
    $index_task = $('#tasks'), // indx中task磁贴
    $addtask_btn = $('.addtask-btn'), // add task button
    $list_ul = $list.find('ul'), // list中展示task的ul
    $desc_submit = $('#desc-submit'), // desc中提交按钮
    $modal_submit = $('#modal-submit'); // modal中提交按钮

var deviceType_var = deviceType(),
    tasks = []; // 用于存放tasks

/**
 * ============ 初始化插件 ============
 */
function init_plugins(){
	// 复选框样式美化插件初始化
	$(":checkbox").labelauty();
	var listScroll;
	listScroll = new IScroll('.list', {
	    mouseWheel: true
	});
	var descScroll;
	descScroll = new IScroll('.desc', {
	    mouseWheel: true
	});
	// 时间选择插件初始化
	mobiscroll_init();
	// fullcalendar
	$calendar.fullCalendar({
        //选择主题
        themeSystem: 'bootstrap3',
        // 默认视图
        defaultView: 'month',
        // 视图头部行布局
        header: ifsidebarBtn(),
        // 自定义按钮，用于唤出sidebar
        customButtons: {
            sidebarBtn: {
                text: 'sidebar',
                click: function () {
                    showSidebar();
                }
            }
        },
        // 高度父元素自适应
        height: "parent",
        // 显示当前时间指示器
        nowIndicator: true,
        eventSources: [
            // 普通日程
            {
                events: function (start, end, timezone, callback) {
                    zlajax.get({
                        'url': '/tasks/',
                        'success': function (data) {
                            var events = [];
                            if (data['code'] === 200) {
                                events = data['data']
                                callback(events);
                            } else {
                                zlalert.alertErrorToast('获取日程失败');
                            }
                        },
                        'fail': function (error) {
                            zlalert.alertNetworkError();
                        }
                    });
                }
            }
        ]
    });
	initSchedule(); // 默认为schedule，先隐藏calendar
}

// 日时间选择插件初始化函数
function mobiscroll_init() {
	var curr = new Date().getFullYear();
	var opt={};
	opt.date = {preset : 'date'};
	opt.datetime = {preset : 'datetime'};
	opt.time = {preset : 'time'};

	opt.default = {
		theme: 'android-holo light', //皮肤样式
		display: 'modal', //显示方式
		mode: 'scroller', //日期选择模式
		dateFormat: 'yyyy-mm-dd',
		lang: 'zh',
		showNow: true,
		nowText: "今天",
		stepMinute: 5,
		startYear: curr - 0, //开始年份
		endYear: curr + 3 //结束年份
	};
	$('.settings').bind('change', function() {
		var demo = 'datetime';
		if (!demo.match(/select/i)) {
			$('.demo-test-' + demo).val('');
		}
		$('.demo-test-' + demo).scroller('destroy').scroller($.extend(opt['datetime'], opt['default']));
		$('.demo').hide();
		$('.demo-' + demo).show();
	});
	$('#demo').trigger('change');
}


/**
 * ============ 绑定功能函数 ===================
 */
function bind_functions() {
    // 在平板、手机页面
    // 实现sidebar唤出和隐藏功能
    if (deviceType_var !== 'pc') {
        $index_greet.click(showSidebar);
        $mask.click(hideSidebar);
    }

    // pc页面
    // 禁用add task button唤出modal
    if (deviceType_var === 'pc') {
        $addtask_btn.attr('data-toggle', '');
    }

    // 手机页面
    if (deviceType_var === 'mobile') {
        // 实现list唤出和隐藏功能
        $index_task.click(showList);
        $list.find('#list-close').click(hideList);
        // 点击list中close按钮，隐藏list，返回index
        $list.find('.close').click(hideList);
    }


    // 点击addtask_btn,即新建日程前，清空desc中表单
    $addtask_btn.click(clearForm);


    // sidebar磁贴用于不同视图间切换
    // 变为schedule视图
    $sidebar.find('#sidebar-li-schedule').click(function (event) {
        event.preventDefault();
        initSchedule();
        // 如果设备为手机/平板，则自动收起sidebar和mask
        if (deviceType_var !== 'pc') {
            hideSidebar();
        }
    });
    // 变为day视图
    $sidebar.find('#sidebar-li-day').click(function (event) {
        event.preventDefault();
        initCalendar();
        $calendar.fullCalendar('changeView', 'agendaDay');
        if (deviceType_var !== 'pc') {
            hideSidebar();
        }
    });
    // 变为week视图
    $sidebar.find('#sidebar-li-week').click(function (event) {
        event.preventDefault();
        initCalendar();
        $calendar.fullCalendar('changeView', 'agendaWeek');
        if (deviceType_var !== 'pc') {
            hideSidebar();
        }
    });
    // 变为month视图
    $sidebar.find('#sidebar-li-month').click(function (event) {
        event.preventDefault();
        $calendar.fullCalendar('changeView', 'month');
        initCalendar();
        if (deviceType_var !== 'pc') {
            hideSidebar();
        }
    });

    // 点击submit按钮创建或修改日程
    $('#desc-submit').click(AjaxAddTask); // pc
    $('#modal-submit').click(AjaxAddTask); // 手机和平板

    // 点击delete按钮删除日程
    $('#desc-delete').click(AjaxDeleteTask); // pc
    $('#modal-delete').click(AjaxDeleteTask); // 手机或平板

}


/**
 * ============ 页面变化逻辑函数 ===================
 */

/**
 * deviceType()
 * 获取当前设备类型
 * 返回参数：
 * type [string]:
 *      1. 'mobile' 当前设备为手机，对应bootstrap中xs
 *      2. 'table'  当前设备为平板，对应bootstrap中sm
 *      3. 'pc'     当前设备为电脑，对应bootstrap中md/lg
 */
function deviceType() {
    var windowWidth = $(window).width();
    if (windowWidth < 768) { return 'mobile'; }
    else if (windowWidth < 992) { return 'table'; }
    else { return 'pc'; }
}

/**
 * showSidebr()
 * 在手机，平板页面唤出sidebar
 */
function showSidebar() {
    $mask.removeClass('hidden-xs hidden-sm');
    $sidebar.removeClass('hidden-xs hidden-sm');
}

/**
 * hideSidebar()
 * 手机，平板页面唤出sidebar后，隐藏sidebr
 */
function hideSidebar() {
    $mask.addClass('hidden-xs hidden-sm');
    $sidebar.addClass('hidden-xs hidden-sm');
}

/**
 * showList()
 * 手机页面唤出list
 */
function showList() {
    $index.addClass('hidden-xs');
    $list.removeClass('hidden-xs');
    // DOM改变后重新初始化滚动插件
    listScroll = new IScroll('.list', {
        mouseWheel: true
	});
}

/**
 * hideList()
 * 手机页面唤出list后，隐藏list
 */
function hideList() {
    $index.removeClass('hidden-xs');
    $list.addClass('hidden-xs');
}

/**
 * initCalendar()
 * 从schedule模式跳转到calendar模式时改变页面布局
 * 重新请求用户日程信息
 */
function initCalendar() {
    $index.hide();
    $list.hide();
    $desc.hide();
    $calendar.show();
    // 在平板/手机尺寸下，点击header->title跳转到today
    if (deviceType_var !== 'pc') {
        $calendar.find('.fc-right').click(function () {
            $calendar.fullCalendar('today');
        })
    }
}

/**
 * initSchedule()
 * 从calendar模式跳转到schedule模式时改变页面布局
 */
function initSchedule() {
    $index.show();
    $list.show();
    $desc.show();
    $calendar.hide();
    render_list();
    clearForm();
}

/**
 * ifsidebarBtn()
 * 根据设备尺寸判断calendar视图header部分左侧是否需要用于唤出sidebar的按钮
 * 返回一个header对象用于fullcalendar插件初始化
 * header: {
            left: '[sidebarBtn] prev, next, today',
            center: 'title',
            right: 'month, agendaWeek, agendaDay'
        }
 */
function ifsidebarBtn() {
    if (deviceType_var === 'pc') {
        return {
            left: 'prev, next, today',
            right: 'title'
        }
    } else {
        return {
            left: 'sidebarBtn prev, next',
            right: 'title'
        }
    }
}




/**
 * ============ 数据功能部分 ===================
 */

// desc中表单元素
var $desc_nameE = $('#desc_name'),
    $desc_starttimeE = $('#desc_starttime'),
    $desc_endtimeE = $('#desc_endtime'),
    $desc_alerttimeE = $('#desc_alerttime'),
    $desc_emailE = $('#desc_email'),
    $desc_smsE = $('#desc_sms'),
    $desc_alldayE = $('#desc_allday'),
    $desc_finishE = $('#desc_finish'),
    $desc_contentE = $('#desc_content');

var $modal_nameE = $('#modal_name'),
    $modal_starttimeE = $('#modal_starttime'),
    $modal_endtimeE = $('#modal_endtime'),
    $modal_alerttimeE = $('#modal_alerttime'),
    $modal_emailE = $('#modal_email'),
    $modal_smsE = $('#modal_sms'),
    $modal_alldayE = $('#modal_allday'),
    $modal_finishE = $('#modal_finish'),
    $modal_contentE = $('#modal_content');

/**
 * clearFrom()
 * 清空desc里表单部分，将input标签值设置为空
 * 注意：模态框不需要清空，bootstrap会自动初始化状态
 */
function clearForm() {
    if (deviceType_var === 'pc'){
        // 清空表单内容
        $desc_nameE.val('');
        $desc_starttimeE.val('');
        $desc_endtimeE.val('');
        $desc_alerttimeE.val('');
        $desc_emailE.prop('checked', true);
        $desc_smsE.prop('checked', false);
        $desc_alldayE.prop('checked', false);
        $desc_finishE.prop('checked', false);
        $desc_contentE.val('');
        // 清除提交按钮上绑定的data-id, data-type
        $desc_submit.attr('data-id', '').attr('data-type', '');
    } else {
        $modal_nameE.val('');
        $modal_starttimeE.val('');
        $modal_endtimeE.val('');
        $modal_alerttimeE.val('');
        $modal_emailE.prop('checked', true);
        $modal_smsE.prop('checked', false);
        $modal_alldayE.prop('checked', false);
        $modal_finishE.prop('checked', false);
        $modal_contentE.val('');
        $modal_submit.attr('data-id', '').attr('data-type', '');
    }
}

/**
 * AjaxAddTask()
 * 向后台请求新建task或者修改task
 * 绑定在desc/modal提交按钮的点击事件，获取desc表单/模态框中内容，通过AJAX发送给后台
 * 首先判断设备类型，通过submit($this)的id为‘desc-submit'/'modal-submit'来确定是pc或者手机/平板
 * 然后通过submit($this)上属性'data-type'是否为'modify'来确定是新建还是修改，两者对应不同url，但AJAX传送的内容相同
 *  新建task url: /newtask/
 *  修改task url: /modtask/
 * 注意：submit还有属性data-id用于存放task id,后面表单验证时需要加上这一条
 */
function AjaxAddTask(event) {
    event.preventDefault();

    $this = $(this);
    var title = '';
    var start = '';
    var end = '';
    var remindtime = '';
    var email_remind = '';
    var message_remind = '';
    var all_day = '';
    var status = 0;
    var content = '';
    var url = ($this.attr('data-type') === 'modify') ? '/modtask/' : '/newtask/';
    var task_id = $this.attr('data-id');


    // task信息字段赋值
    // 对pc 和 手机/平板分别做了适配
    if ($this.attr('id') === 'desc-submit') {
        // desc中表单部分
        title = $desc_nameE.val();
        start = $desc_starttimeE.val();
        end = $desc_endtimeE.val();
        remindtime = $desc_alerttimeE.val();
        email_remind = $desc_emailE.is(':checked');
        message_remind = $desc_smsE.is(':checked');
        all_day = $desc_alldayE.is(':checked');
        status = $desc_finishE.is(':checked') ? 1 : 0;
        content = $desc_contentE.val();
    } else if ($this.attr('id') === 'modal-submit') {
        // modal中表单部分
        title = $modal_nameE.val();
        start = $modal_starttimeE.val();
        end = $modal_endtimeE.val();
        remindtime = $modal_alerttimeE.val();
        email_remind = $modal_emailE.is(':checked');
        message_remind = $modal_smsE.is(':checked');
        all_day = $modal_alldayE.is(':checked');
        status = $modal_finishE.is(':checked') ? 1 : 0;
        content = $modal_contentE.val();
    }

    // ajax发送
    zlajax.post({
        'url': url,
        'data': {
            'title': title,
            'content': content,
            'all_day': all_day,
            'start': start,
            'end': end,
            'email_remind': email_remind,
            'message_remind': message_remind,
            'remindtime': remindtime,
            'status': status,
            'task_id': task_id
        },
        'success': function (data) {
            if (data['code'] === 200) {
                zlalert.alertSuccessToast('save successfully');
                // 重新渲染list
                render_list();
            } else {
                zlalert.alertInfo(data['message']);
            }
        },
        'fail': function (error) {
            zlalert.alertNetworkError();
        }
    })
}

/**
 * AjaxGetTasks()
 * 获取当前用户的所有日程，并存放到全局变量taks中
 */
function AjaxGetTasks(callback) {
    zlajax.get({
        'url': '/tasks/',
        'success': function (data) {
            if (data['code'] === 200) {
                tasks = data['data'];
                callback(data['data']);
            } else {
                console.log('内部错误，无法获取日程');
            }
        },
        'fail': function (error) {
            // zlalert.alertNetworkError();
            console.log('网络错误，无法到达');
        }
    })
}

function AjaxDeleteTask(event) {
    event.preventDefault();

    var task_id =  deviceType_var==='pc' ? $desc_submit.attr('data-id') : $modal_submit.attr('data-id');
    if (!(task_id==="")) {
        // 当前处在某一一日程的信息展示页，需要删除数据库中对应项
        zlajax.post({
            'url': '/deltask/',
            'data': { 'task_id': task_id },
            'success': function (data) {
                if (data['code'] === 200) {
                    zlalert.alertSuccessToast(msg='日程已经删除。');
                    clearForm();
                    render_list();
                } else {
                    zlalert.alertErrorToast(msg=data['message']);
                }
            },
            'fail': function (error) {
                zlalert.alertNetworkError();
            }
        })
    } else{
        // 当前正在添加日程，放弃新建时直接清空即可
        clearForm();
    }
}


/**
 *  生成list部分close按钮的jquery对象
 */
var listClose_str = '<li id="list-close" class="hidden-sm hidden-md hidden-lg">' +
' <button type="button" class="close" aria-label="Close">' +
'<span aria-hidden="true">&times;</span>' +
'</button>' + '</li>';
var $listClose = $(listClose_str);

/**
 * factory_listLi()
 *  将task对象填充到一个li标签中，并转换成jQuery对象返回，task.content作为<li>中内容，其余字段以'data-task_index'的形式作为属性加入
 * @param task_obj :: 从后端获取的task对象
 * @returns {*|jQuery|HTMLElement} :: 转换完成的对象
 */
function factory_listLi(task_obj) {
    var $listLi = $('<li></li>');
    $listLi.text(task_obj.title);
    $listLi.attr('data-all_day', task_obj.all_day);
    $listLi.attr('data-content', task_obj.content);
    $listLi.attr('data-email_remind', task_obj.email_remind);
    $listLi.attr('data-end', task_obj.end);
    $listLi.attr('data-id', task_obj.id);
    $listLi.attr('data-message_remind', task_obj.message_remind);
    $listLi.attr('data-remindtime', task_obj.remindtime);
    $listLi.attr('data-start', task_obj.start);
    $listLi.attr('data-status', task_obj.status);
    return $listLi;
}

/**
 * render_listItems()
 * 作为AjaxGetTasks的回调函数，在成功取得数据后，遍历task数组，将单条task转换成<li>的jQuery对象，插入list部分的<ul>列表
 * @param tasks :: 存放task对象的Array，请求返回信息中'data'部分
 */
function render_listItems(tasks) {
    for (var i=0; i<tasks.length; i++) {
        $list_ul.append(factory_listLi(tasks[i]));
    }
    bind_render_desc();
}

/**
 * render_list()
 * 包含渲染task列表的所有工作，包括：
 *  1. 清空当前task列表
 *  2. 插入在手机界面使用的'关闭list'按钮
 *  3. 请求task数据，经渲染后插入列表
 */
function render_list() {
    $list_ul.text('');
    $list_ul.append($listClose);
    AjaxGetTasks(render_listItems);
}

/**
 * iso2timeStr()
 * 将符合ISO8601格式的字符串转换成时间选择器生成的格式
 * @param isoStr :: ISO 8601标准时间字符串，格式形如'2018-04-11T22:05:00'
 * @returns {*} :: 如果传入的字符串符合标准，则解析成形如'2018-04-08 21:00'格式；否则返回空字符串
 */
function iso2timeStr(isoStr) {
    var re = /(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}):\d\d/;
    if (re.test(isoStr)) {
        return isoStr.replace(re, "$1 $2")
    } else {
        return ''
    }
}

/**
 * str2bool()
 * 将字符/字符串('0', '1', 'true', 'false')转换成对应bool值
 * @param raw_value 需要转换的字符(串)，推荐范围为上述4个
 * @returns {boolean} 如果输入为'1' 或 'true'，则返回true，否则返回false
 */
function str2bool(raw_value) {
    return (raw_value === '1') || (raw_value === 'true')
}

/**
 * render_desc()
 * 渲染desc部分，将task信息从list对应item中取出，填入desc/modal表单中
 * 如果该item为list最上方close按钮，则跳过
 */
function render_desc() {
    $this = $(this);
    if ($this.attr('id') === 'list-close') { return; }


    if (deviceType_var === 'pc') {
        $desc_nameE.val($this.text());
        $desc_starttimeE.val(iso2timeStr($this.attr('data-start')));
        $desc_endtimeE.val(iso2timeStr($this.attr('data-end')));
        $desc_alerttimeE.val(iso2timeStr($this.attr('data-remindtime')));
        $desc_emailE.prop('checked', str2bool($this.attr('data-email_remind')));
        $desc_smsE.prop('checked', str2bool($this.attr('data-message_remind')));
        $desc_alldayE.prop('checked', str2bool($this.attr('data-all_day')));
        $desc_finishE.prop('checked', str2bool($this.attr('data-status')));
        $desc_contentE.val($this.attr('data-content'));
        $('#desc-submit').attr('data-id', $this.attr('data-id')).attr('data-type', 'modify');
    } else {
        // 显示模态框
        $('#myModal').modal('show');
        $modal_nameE.val($this.text());
        $modal_starttimeE.val(iso2timeStr($this.attr('data-start')));
        $modal_endtimeE.val(iso2timeStr($this.attr('data-end')));
        $modal_alerttimeE.val(iso2timeStr($this.attr('data-remindtime')));
        $modal_emailE.prop('checked', str2bool($this.attr('data-email_remind')));
        $modal_smsE.prop('checked', str2bool($this.attr('data-message_remind')));
        $modal_alldayE.prop('checked', str2bool($this.attr('data-all_day')));
        $modal_finishE.prop('checked', str2bool($this.attr('data-status')));
        $modal_contentE.val($this.attr('data-content'));
        $('#modal-submit').attr('data-id', $this.attr('data-id')).attr('data-type', 'modify');
    }
}

/**
 * bind_render_desc()
 * 用于在list部分DOM改变后重新绑定点击事件
 */
function bind_render_desc() {
    var $list_li = $list.find('li');
    $list_li.click(render_desc);
}









