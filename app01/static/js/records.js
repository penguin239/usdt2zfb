let date = $('#record_date');
let time = new Date();
let day = ("0" + time.getDate()).slice(-2);
let month = ("0" + (time.getMonth() + 1)).slice(-2);
let today = time.getFullYear() + "-" + (month) + "-" + (day);
let save_info = null;
let save_date = null;

let csrfmiddlewaretoken = $('.csrfmiddlewaretoken').val();

// 设置日期选择器默认日期为今日
date.val(today);
search_record_by_date(today, 0);
$('#date_sbm').click(function () {
    let date = $('#record_date').val();
    if (!date) {
        alert('请选择日期！');
        return;
    }
    search_record_by_date(date, 1);
});

function generate_table(tb, info) {
    // 首先删除table所有子节点，为下面生成表格做铺垫
    let childs = tb.childNodes;
    for (let i = childs.length - 1; i >= 0; i--) {
        tb.removeChild(childs[i]);
    }

    // 动态生成表格
    for (let i = 0; i < info.length; i++) {
        let tr = document.createElement('tr');
        for (let k in info[i]) {
            let td = document.createElement('td');
            td.appendChild(document.createTextNode(info[i][k]));
            tr.appendChild(td);
        }
        tb.appendChild(tr);
    }
}

const tb = document.getElementById('tb');

function search_record_by_date(date_time, flag) {
    // 这里的flag用于判断是网页加载时调用的此函数还是其他方法调用的此函数，否则会在加载时直接弹窗
    $.ajax({
        url: '/search_record_by_date/', type: 'POST',

        data: {
            'csrfmiddlewaretoken': csrfmiddlewaretoken, 'date': date_time
        }, success: (info) => {
            // 这里的info是某一天的兑换记录
            // 全局info，当点击保存当页时调用，每次查询页码时覆盖，达到导出当前页面的效果
            save_info = info;
            save_date = date_time;
            if (!info.length && flag) {
                alert(`${date_time}日无交易记录！`);
                return;
            }
            generate_table(tb, info);

            $('#wc-l')[0].innerHTML = `${date_time}日共<b>${info.length}</b>条交易记录`;
        }, error: (error) => {
            console.error(error);
        }
    });
}

// 弃用，对应django views中save_to_csv方法。
$('#export1').click(function () {
    // 点击导出本页时，把save_info变量请求给django，由django进行格式化保存
    let csrfmiddlewaretoken = $('.csrfmiddlewaretoken').val();

    $.ajax({
        url: '/save_to_csv/', type: 'POST', traditional: true,

        data: {
            'csrfmiddlewaretoken': csrfmiddlewaretoken, // 序列化传输，否则后端无法接收
            'info': JSON.stringify(save_info)
        }, success: (feedback) => {
            console.log(feedback);
        }, error: (error) => {
            console.error(error);
        }
    });
});

$('#export').click(function () {
    // 使用Blob对象直接在前端进行文件下载。
    let filename = save_date + '.csv';
    let content = '编号,用户名,永久ID,口令,金额,兑换时间\n';
    for (let i = 0; i < save_info.length; i++) {
        let line = `${save_info[i].id},${save_info[i].username},${save_info[i].uid},${save_info[i].passport},${save_info[i].amount},${save_info[i].exchange_time}`
        content += line + '\n';
    }
    let blob = new Blob(['\ufeff', content], {type: 'text/plain'});
    let url = URL.createObjectURL(blob);

    let a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click()

    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
});

const tb0 = document.getElementById('tb0');
$('#search_record_button').click(function () {
    let uid = $('#search_record').val();

    if (!uid) {
        alert('请输入id进行查询！');
        return;
    }
    $.ajax({
        url: '/search_record/',
        type: 'POST',

        data: {
            'csrfmiddlewaretoken': csrfmiddlewaretoken,
            'uid': uid,
        },
        success: (info) => {
            // info为搜索的用户信息，数组
            if (!info.length) {
                alert(`未搜索到用户${uid}的交易记录`);
                $('.search_back').css('display', 'none');
                return;
            }
            // 生成表格
            generate_table(tb0, info);
            $('.search_back').css('display', 'block');
        },
        error: (error) => {
            console.error(error);
        }
    });
});
