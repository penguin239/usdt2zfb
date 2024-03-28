const delete_all_user = $('.delete_all_user');
const csrfmiddlewaretoken = $('#csrf_token').val();

delete_all_user.click(function () {
    const selects = $('.select');
    let selected = [];

    selects.each((index) => {
        if (selects[index].checked === true) {
            selected.push(parseInt(selects[index].value));
        }
    });
    if (selected.length === 0) {
        alert('未选择任何记录');
        return;
    }
    // selected数组中存放的是选中的id，
    // 对这些id执行删除操作
    $.ajax({
        url: '/user_mul_del/', type: 'POST', traditional: true, dataType: 'json', data: {
            'csrfmiddlewaretoken': csrfmiddlewaretoken, 'selected': JSON.stringify(selected),
        },

        success: () => {
            alert('删除成功！');
            window.location.href = window.location.href;
        }, error: (error) => {
            alert('删除失败，详情请看控制台输出。')
            console.error(error);
        }
    });

});

$('.delete_personal').click(function () {
    let user_id = $(this).val();

    $.ajax({
        url: '/personal_delete/',
        type: 'POST',

        data: {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'user_id': user_id,
        },
        success: () => {
            alert('删除成功！');
            window.location.href = window.location.href;
        },
        error: (error) => {
            alert('删除失败，详情请看控制台输出！');
            console.error(error);
        }
    });
});

$('.etc').click(function () {
    $('.info_box').css('display', 'block');
    let value = $(this).val().split(',');

    $('#username')[0].innerText = value[0];
    $('#uid')[0].innerText = value[1];
    $('#balance')[0].innerText = value[2];
});

$('.de').click(function () {
    $('.info_box_del').css('display', 'block');
    let value = $(this).val().split(',');

    $('#username0')[0].innerText = value[0];
    $('#uid0')[0].innerText = value[1];
    $('#balance0')[0].innerText = value[2];
});

$('#sbm_de').click(function () {
    let uid = $('#uid0')[0].innerText;
    let balance = $('#balance0')[0].innerText;
    let de_num = $('.de_num').val();
    de_num = parseInt(de_num);

    if (isNaN(de_num)) {
        alert('请输入扣款金额！');
        return;
    } else if (de_num === 0) {
        alert('扣款金额不可为0！');
        return;
    } else if (de_num < 0) {
        alert('扣款金额不可为负数！');
        return;
    } else if (balance - de_num < 0) {
        alert('该用户余额不足以扣款，请检查扣款金额。');
        return;
    }

    // 提交扣款请求
    $.ajax({
        url: '/de_amount/',
        type: 'POST',

        data: {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'uid': uid,
            'de_num': de_num
        },
        success: (info) => {
            alert(`用户${uid}成功扣款${de_num}元`);
            window.location.href = window.location.href;
        },
        error: (error) => {
            console.log(error);
            alert('扣款失败，详情请看控制台输出！');
        }
    });
});

$('#sbm_etc').click(function () {
    let uid = $('#uid')[0].innerText;
    let balance = $('#balance')[0].innerText;
    let etc_num = $('.etc_num').val();
    etc_num = parseInt(etc_num);

    if (isNaN(etc_num)) {
        alert('请输入充值数量！');
        return;
    } else if (etc_num === 0) {
        alert('充值数量不可为0！');
        return;
    } else if (etc_num < 0) {
        alert('充值数量不可为负数！');
        return;
    }

    // 提交充值
    $.ajax({
        url: '/etc/',
        type: 'POST',

        data: {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'uid': uid,
            'balance': balance,
            'etc_num': etc_num
        },
        success: () => {
            alert(`账号${uid}充值成功${etc_num}元。`);
            window.location.href = window.location.href;
        },
        error: (error) => {
            alert('充值失败，详情请看控制台输出！');
            console.error(error);
        }
    });
});

$('.close').click(function () {
    $('.info_box').css('display', 'none');
    $('.info_box_del').css('display', 'none');
})

$('#search_button').click(function () {
    const uid = $('#search_bar').val();

    if (!uid) {
        alert('请输入id进行查询！');
        return;
    }
    $.ajax({
        url: '/searchPersonal/',
        type: 'POST',

        data: {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'uid': uid,
        },
        success: (info) => {
            let status_ = parseInt(info);

            if (status_ === 0) {
                alert('未查询到此用户信息！');
                return;
            }
            let data = JSON.parse(info);
            $('#personal_id')[0].innerText = data.id;
            $('#personal_username')[0].innerText = data.username;
            $('#personal_uid')[0].innerText = data.uid;
            $('#personal_balance')[0].innerText = data.balance;
            $('#register_date')[0].innerText = data.register_date;

            $('.personal_etc').val(`${data.username},${data.uid},${data.balance}`)
            $('.search_one_del').val(data.uid);

            $('.user_info_display').css('display', 'block');
        },
        error: (error) => {
            console.error(error);
        }
    });
});
