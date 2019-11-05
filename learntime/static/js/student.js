$(function () {
  $('#student-import-form').ajaxForm(function (data) {
    if (data.status === "fail") {
        alert(data.reason)
    } else {
        alert("导入学生数据成功！");
        window.location.reload()
    }
  });

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
  })
})
