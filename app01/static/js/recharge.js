const tb0 = document.getElementById('tb0');
const csrfmiddlewaretoken = $('.csrfmiddlewaretoken').val();

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

$('#search_recharge_button').click(function () {
    let uid = $('#search_recharge').val();

    if (!uid) {
        alert('请输入id进行查询！');
        return;
    }
    $.ajax({
        url: '/search_recharge/',
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
