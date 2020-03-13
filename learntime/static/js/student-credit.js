$(function () {
    function getQueryString(name) {
        var reg = new RegExp("(^|&)"+ name +"=([^&]*)(&|$)");
        var r = window.location.search.substr(1).match(reg);//search,查询？后面的参数，并匹配正则
        if(r!=null)
         return  decodeURIComponent(r[2])
        return null;
    }

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
        window.location.href = "/students/credit/"
    });


    let student_uid = '';
    if (window.location.search.indexOf("clazz=") !== -1) {
        $('#bulk-add-btn').show()
    } else {
        $('#bulk-add-btn').hide()
    }
    // 将学生的学时信息显示到模态框中
    $('.edit-credit-btn').click(function () {
        student_uid = $(this).attr("data-uid");
        $.ajax({
            url: "/students/edit-credit/",
            cache: false,
            method: "GET",
            data: {
                uid: student_uid
            },
            success: res => {
              if (res.status === "ok") {
                  $('#wt-credit').val(res.wt_credit);
                  $('#fl-credit').val(res.fl_credit);
                  $('#xl-credit').val(res.xl_credit);
                  $('#cxcy-credit').val(res.cxcy_credit);
                  $('#sxdd-credit').val(res.sxdd_credit);
                  $('#edit-credit-label').text(`修改${res.name}的学时`);
              } else {
                  alert("获取学生信息失败！");
                  return;
              }
            }
        })
    });
    // 提交修改
    $('#confirm-edit-credit').click(function () {
        $.ajax({
            url: '/students/edit-credit/',
            cache: false,
            method: "POST",
            data: {
                uid: student_uid,
                wt_credit: $('#wt-credit').val(),
                fl_credit: $('#fl-credit').val(),
                xl_credit: $('#xl-credit').val(),
                cxcy_credit: $('#cxcy-credit').val(),
                sxdd_credit: $('#sxdd-credit').val(),
            },
            success: res => {
              if (res.status === "ok") {
                  alert("修改学时成功！")
                  window.location.reload()
              } else {
                  alert("修改学时失败！");
                  return;
              }
            }
        })
    });

    // 点击批量增加学时按钮
    $('#bulk-add-btn').click(function () {
        $('#bulk-add-modal-title').text(`增加"${getQueryString("clazz")}"所有学生的学时`)
    });

    // 批量增加学时
    $('#confirm-bulk-add').click(function () {
        var _type = $('#select-type').val();
        var amount = $('#credit-amount-input').val();
        if(isNaN(parseFloat(amount))) {
            alert("请输入数字！")
        }
        $.ajax({
            url: '/students/bulk-add-credit/',
            cache: false,
            method: 'POST',
            data: {
                _type,
                amount,
                clazz: getQueryString("clazz")
            },
            success: res => {
                if (res.status === "ok") {
                  alert("操作成功！");
                  window.location.reload()
                } else {
                  alert("操作失败，请稍候重试！");
                }
            }
        })
    })
});
