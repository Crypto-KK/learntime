$(function () {

    function getQueryString(name) {
        var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
        var r = window.location.search.substr(1).match(reg);//search,查询？后面的参数，并匹配正则
        if(r!=null)
         return  decodeURIComponent(r[2])
        return null;
    }


  $('#student-import-form').ajaxForm(function (data) {
    if (data.status === "fail") {
        alert(data.reason)
    } else {
        alert("导入学生数据成功！");
        window.location.reload()
    }
  });

  //$('#bulk-delete-btn').css("display", "none");
  $('#checkAll').click(function () {
      $("input[name='student-checkbox']").prop("checked", this.checked);

      if (this.checked === true) {
          //$('#bulk-delete-btn').css("display", 'true')
      } else {
          //$('#bulk-delete-btn').css("display", 'none')
      }
  });

  $('#bulk-delete-btn').click(function () {
      if (confirm("确定删除所选学生吗？")) {
          var checks = $('input[name="student-checkbox"]:checked');
          if (checks.length === 0 ) {
              alert("未选中任何学生");
              return false;
          }
          var checkData = [];
          checks.each(function () {
              checkData.push($(this).val());
          });
          $.ajax({
              url: "/students/student-bulk-delete/",
              cache: false,
              method: "POST",
              data: {
                  student_list: checkData.join("-")
              },
              success: res => {
                  if (res.status === "fail") {
                      alert("批量删除失败！")

                  } else {
                      alert("批量删除成功！")
                      window.location.reload();
                  }
              }
          })
      }
  });

  $('#delete-all-btn').click(function () {
      if (confirm("确认删除所有学生吗？")) {
          $.ajax({
              url: '/students/student-all-delete/',
              cache: false,
              method: "POST",
              success: res => {
                  if (res.status === "fail") {
                      alert("删除所有学生失败！")

                  } else {
                      alert("删除所有学生成功！")
                      window.location.reload();
                  }
              }
          })
      }
  });

  $('#select-uid').click(function () {
      $('#select-btn').text("学号");
      $('#inlineFormInput').attr({
          "placeholder": "搜索学号",
          "name": "uid"
      });
  });

  $('#select-name').click(function () {
      $('#select-btn').text("姓名");
      $('#inlineFormInput').attr({
          "placeholder": "搜索姓名",
          "name": "name"
      });
  });

  $('#select-academy').click(function () {
      $('#select-btn').text("学院");
      $('#inlineFormInput').attr({
          "placeholder": "搜索学院",
          "name": "academy"
      });
  });
  $('#select-grade').click(function () {
      $('#select-btn').text("年级");
      $('#inlineFormInput').attr({
          "placeholder": "搜索年级",
          "name": "grade"
      });
  });
  $('#select-clazz').click(function () {
      $('#select-btn').text("班级");
      $('#inlineFormInput').attr({
          "placeholder": "搜索班级",
          "name": "clazz"
      });
  });

  var concatQuery = "";
  var uid = getQueryString("uid");
  var name = getQueryString("name");
  var grade = getQueryString("grade");
  var clazz = getQueryString("clazz");
  var academy = getQueryString("academy");
  if (!uid && !name && !grade && !clazz && !academy) {
      $('#delete-all-btn').show()
  } else {
      $('#delete-all-btn').hide()
  }
  if (uid) {
      concatQuery = "uid=" + uid;
      $('#select-uid').click();
      $('#inlineFormInput').attr('value', uid)
  } else if (name) {
      concatQuery = "name=" + name;
      $('#select-name').click();
      $('#inlineFormInput').attr('value', name)
  } else if (grade) {
      concatQuery = "grade=" + grade;
      $('#select-grade').click();
      $('#inlineFormInput').attr('value', grade)
  } else if (clazz) {
      concatQuery = "clazz=" + clazz;
      $('#select-clazz').click();
      $('#inlineFormInput').attr('value', clazz)
  } else if (academy) {
      concatQuery = "academy=" + academy;
      $('#select-academy').click();
      $('#inlineFormInput').attr('value', academy)
  }

  $('.page-link').each(function () {
      // 分页时携带参数
      var oldHref = $(this).attr("href");
      newHref = oldHref + "&" + concatQuery;
      $(this).attr("href", newHref);
  });


  $('#reset-select').click(function () {
      window.location.href = "/students/"
  });




});
