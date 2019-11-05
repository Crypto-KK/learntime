$(function () {

  function getQueryVariable(variable)
    {
        var query = window.location.search.substring(1);
        var vars = query.split("&");
        for (var i=0;i<vars.length;i++) {
               var pair = vars[i].split("=");
               if(pair[0] == variable){return pair[1];}
        }
        return false;
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
  var uid = getQueryVariable("uid");
  var name = getQueryVariable("name");
  var grade = getQueryVariable("grade");
  var clazz = getQueryVariable("clazz");
  var academy = getQueryVariable("academy");
  if (uid) {
      concatQuery = "uid=" + uid;
  } else if (name) {
      concatQuery = "name=" + name;
  } else if (grade) {
      concatQuery = "grade=" + grade;
  } else if (clazz) {
      concatQuery = "clazz=" + clazz;
  } else if (academy) {
      concatQuery = "academy=" + academy;
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
