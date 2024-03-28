const close = $('.close');
const edit = $('.edt');
const del = $('.del');

close.click(function () {
    $('.window').css('display', 'none');
});

edit.click(function () {
    $('.window').css('display', 'block');
    const data = JSON.parse($(this).val());

    $('#id').val(data['id']);
    $('#passport').val(data['passport']);
    $('#amount').val(data['amount']);
    $('#status').val(data['status']);
});

const status_ = $('.status');
for (let i = 0; i < status_.length; i++) {
    let content = status_[i].innerText;
    if (content === '可用') {
        status_[i].style.color = 'green';
    } else {
        status_[i].style.color = 'red';
    }
}

const select_all = $('#select_all');
const selects = $('.select');

select_all.click(function () {
    if (select_all[0].checked) {
        for (let i = 0; i < selects.length; i++) {
            selects[i].checked = true;
        }
    } else {
        for (let i = 0; i < selects.length; i++) {
            selects[i].checked = false;
        }
    }
});

const delete_all_button = $('.delete_all_button');

delete_all_button.click(function () {
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
    const csrfmiddlewaretoken = $('#csrf_token').val();
    $.ajax({
        url: '/mul_del/',
        type: 'POST',
        traditional: true,
        dataType: 'json',
        data: {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'selected': JSON.stringify(selected),
        },

        success: () => {
            alert('删除成功！');
            window.location.href = window.location.href;
        },
        error: (error) => {
            alert('删除失败，详情请看控制台输出。')
            console.error(error);
        }
    });
});

