let studentData = JSON.parse(sessionStorage.getItem('studenti'));
if (studentData == null) {
    window.location.replace("login.html");
}

let type_method = function (actType) {
    let actRecord = JSON.parse(sessionStorage.getItem('activation_record'));
    if ('全部参加记录' == actType) {
        return actRecord
    } else {
        let L = actRecord.length;
        let arr = new Array();
        for (let i = 0; i < L; i++) {

            if (actRecord[i].credit_type == actType) {
                arr.push(actRecord[i]);
            }
        }
        return arr
    }
}