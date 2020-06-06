
Toast = {
  success: function (msg) {
    Swal.fire({
      position: 'top-end',
      icon: 'success',
      title: msg,
      showConfirmButton: false,
      timer: 3000
    })
  },

  error: function (msg) {
    Swal.fire({
      position: 'top-end',
      icon: 'error',
      title: msg,
      showConfirmButton: false,
      timer: 3000
    })
  },

  warning: function (msg) {
    Swal.fire({
      position: 'top-end',
      icon: 'warning',
      title: msg,
      showConfirmButton: false,
      timer: 3000
    })
  },

  warning_with_time: function (msg, time) {
    Swal.fire({
      position: 'top-end',
      icon: 'warning',
      title: msg,
      showConfirmButton: false,
      timer: time
    })
  }
}
