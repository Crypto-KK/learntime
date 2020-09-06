Loading = {
  show: function () {
    $.blockUI({
      message: '<img src="https://learningtime.oss-cn-shenzhen.aliyuncs.com/media/file/loading.gif" /><br><span>正在导入中，请稍等......若超过10秒没有反应，说明表格填写有误</span>',
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
