$(function () {
    //将头部引入其他页面

    $.ajax({
        type: "get",
        url: "header.html",
        success: function (res) {
            $(res).replaceAll("#globalHeader");
            var example2 = new Vue({
                el: "#globalHeader",
                data: {
                    studentName: '欢迎您，' + studentData.name
                },
                methods: {
                }
            })
        }
    })
})