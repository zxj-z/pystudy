var CrptoJS=require("crypto-js")

function md5_test(text){
    return CrptoJS.MD5(text).toString()
}
function  get_params(){

var r = Date.now().toString()
var code=md5_test(r + "9527" + r.substr(0, 6))
    return{
    time:r,
    code:code
    }
}


