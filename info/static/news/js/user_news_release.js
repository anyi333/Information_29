function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

/*
* $.ajax({}):get  post  一般用于传输纯文本的字符串
* (this).ajaxSubmit({})  一般用于传输不是纯文本的数据,
* 比如一个表单中input type=text/file,会自动的以表单的行为读取表单中带有name的input标签属性,不需要手动读取
* */

$(function () {

    $(".release_form").submit(function (e) {
        e.preventDefault()
        // TODO 发布完毕之后需要选中我的发布新闻
        $(this).ajaxSubmit({
            // 读取富文本编辑器里买男的文本信息
            beforeSubmit: function (request) {
                // 在提交之前，对参数进行处理
                for(var i=0; i<request.length; i++) {
                    var item = request[i]
                    if (item["name"] == "content") {
                        item["value"] = tinyMCE.activeEditor.getContent()
                    }
                }
            },
            url: "/user/news_release",
            type: "POST",
            headers: {
                "X-CSRFToken": getCookie('csrf_token')
            },
            success: function (resp) {
                if (resp.errno == "0") {
                    // 选中索引为6的左边单菜单
                    window.parent.fnChangeMenu(6)
                    // 滚动到顶部
                    window.parent.scrollTo(0, 0)
                }else {
                    alert(resp.errmsg)
                }
            }
        })
    })
})