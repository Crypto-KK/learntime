Loading = {
  show: function () {
    $.blockUI({
      message: '<img src="https://learningtime.oss-cn-shenzhen.aliyuncs.com/media/file/loading.gif" /><br><span>正在导入中，请稍等......如果长时间没有反应，说明表格填写确有错误，导致系统异常，建议重新填写表格</span>',
      css: {
        zIndex: "10011",
        padding: "10px",
        left: "50%",
        width: "220px",
        marginLeft: "-40px",
      }
    });
  },
  show_export: function () {
    $.blockUI({
      message: '<img src="https://learningtime.oss-cn-shenzhen.aliyuncs.com/media/file/loading.gif" /><br><span>正在导出中...可能需要几分钟，若长时间无反应，请刷新页面并重新导出</span>',
      css: {
        zIndex: "10011",
        padding: "10px",
        left: "50%",
        width: "220px",
        marginLeft: "-40px",
      }
    });
  },
  hide: function () {
    // 本地查询速度太快，loading显示一瞬间，故意做个延迟
    $.unblockUI();
  }
};
