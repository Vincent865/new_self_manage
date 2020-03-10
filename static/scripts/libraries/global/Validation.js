//Validation.js, for validate data
function Validation() {
}

Validation.formatString = function (input) {
    var re = /\${(.*?)}/g;
    var newStr = input.replace(re, function(match){
        var obj = re.exec(match);
        obj = obj[1].split('.');
        var value = this;
        obj.forEach(function(name){
            value = value[name];
        });
        return value == this ? '' : value;
    });
    return newStr;
}
Validation.validateIP = function (input) {
    try {
        var reg = /^(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)\.(25[0-5]|2[0-4]\d|[0-1]\d{2}|[1-9]?\d)$/;
        if (!input.match(reg)) {
            return false;
        } else {
            var lst = input.split('.');
            lst = lst.map(function (n) {
                return parseInt(n);
            });
            //A类地址范围:   1.0.0.1—126.255.255.254
            //B类地址范围：128.0.0.1—191.255.255.254
            //C类地址范围：192.0.0.1—223.255.255.254
            // --暂不考虑 D类地址范围：224.0.0.1—239.255.255.254
            // --暂不考虑 E类地址范围：240.0.0.1—255.255.255.254
            /*if (lst[0] === 0 || lst[0] === 127 || lst[0] > 223) {
                return false;
            }*/
            if (input === "126.255.255.255" || input === "128.0.0.0" || input === "191.255.255.255" || input === "192.0.0.0" || input === "223.255.255.255") {
                return false;
            }
        }
        return true;
    }
    catch (err) {
        console.error("ERROR - Validation.validateIP() - Unable to validate ip: " + err.message);
    }
}

Validation.validateSubnet = function (input) {
    try {
        var IPPattern = /^((254|252|248|240|224|192|128|0)\.0\.0\.0|255\.(254|252|248|240|224|192|128|0)\.0\.0|255\.255\.(254|252|248|240|224|192|128|0)\.0|255\.255\.255\.(254|252|248|240|224|192|128|0))|(^\d{1,2})$/
        if (!IPPattern.test(input)) return false;

        /* 检查域值 */
        var IPArray = input.split(".");
        var ip1 = parseInt(IPArray[0]);
        var ip2 = parseInt(IPArray[1]);
        var ip3 = parseInt(IPArray[2]);
        var ip4 = parseInt(IPArray[3]);
        //检查长度
        if (IPArray.length > 4) {
            return false;
        }
        /* 每个域值范围0-255 */
        if (ip1 < 0 || ip1 > 255
           || ip2 < 0 || ip2 > 255
           || ip3 < 0 || ip3 > 255
           || ip4 < 0 || ip4 > 255) {
            return false;
        }
        if (input.length < 3 && ip1 > 32) {
            return false;
        }
        return true;

        return true;
    }
    catch (err) {
        console.error("ERROR - Validation.validateSubnet() - Unable to validate subnet mask: " + err.message);
    }
}

Validation.validateIPV6 = function (str) {
    try {
        var perlipv6regex = "^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))\s*$";
        var aeronipv6regex = "^\s*((?=.*::.*)(::)?([0-9A-F]{1,4}(:(?=[0-9A-F])|(?!\2)(?!\5)(::)|\z)){0,7}|((?=.*::.*)(::)?([0-9A-F]{1,4}(:(?=[0-9A-F])|(?!\7)(?!\10)(::))){0,5}|([0-9A-F]{1,4}:){6})((25[0-5]|(2[0-4]|1[0-9]|[1-9]?)[0-9])(\.(?=.)|\z)){4}|([0-9A-F]{1,4}:){7}[0-9A-F]{1,4})\s*$";

        var regex = "/"+perlipv6regex+"/";
        return (/^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}(((:[0-9A-Fa-f]{1,4}){1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))\s*$/.test(str));
    }
    catch (err) {
        console.error("ERROR - Validation.validateSubnet() - Unable to validate subnet mask: " + err.message);
    }
};

Validation.validateMAC = function (input) {
    try {
        var reg = /^([a-fA-F\d]{2}:){5}[a-fA-F\d]{2}$/;
        if (reg.test(input)) {
            if(input.length>17){
                return false;
            }
            return true;
        }
        return false;
    }
    catch (err) {
        console.error("ERROR - Validation.validateIP() - Unable to validate ip: " + err.message);
    }
}

Validation.validateComplexIP = function (input) {
    try {
        var IPArray = input.split(",");
        for (var i = 0; i < IPArray.length; i++) {
            var tmpIPArray = IPArray[i].split("-");
            if (tmpIPArray.length == 2 && (!Validation.validateIP(tmpIPArray[0]) || !Validation.validateIP(tmpIPArray[1]))) {
                return false;
            }
            var tmpSubnet = IPArray[i].split("/");
            if (tmpSubnet.length == 2 && (!Validation.validateIP(tmpSubnet[0]) || !Validation.validateSubnet(tmpSubnet[1]))) {
                return false;
            }
            if (tmpIPArray.length != 2 && tmpSubnet.length != 2&& !Validation.validateIP(IPArray[i]))
            {
                return false;
            }
        }
        return true;
    }
    catch (err) {
        console.error("ERROR - Validation.validateComplexIP() - Unable to validate complex IP: " + err.message);
    }
}

Validation.validateRangeIP = function (input) {
    try {
        var IPArray = input.split("-");
        for (var i = 0; i < IPArray.length; i++) {
            if (!Validation.validateIP(IPArray[i])) {
                return false;
            }
        }

        return true;
    }
    catch (err) {
        console.error("ERROR - Validation.validateRangeIP() - Unable to validate IP range: " + err.message);
    }
}

Validation.validatePort = function (input) {
    try {

        var reg = /^[0-9]+$/;
        if (!reg.test(input)) {
            return false;
        }
        if (input < 1 || input > 65535)
        {
            return false
        }

        return true;
    }
    catch (err) {
        console.error("ERROR - Validation.validateIP() - Unable to validate ip: " + err.message);
    }
}

Validation.validateDateTime = function (input) {
    try {
        var reg = /^(\d{1,4})(-|\/)([0,1]\d{1})(-|\/)([0,1,2,3]\d{1}) (\d{1,2}):(\d{1,2}):(\d{1,2})$/;
        if (!reg.test(input)) {
            return false;
        }

        return true;
    }
    catch (err) {
        console.error("ERROR - Validation.validateDateTime() - Unable to validate datetime: " + err.message);
    }
}

Validation.validateUserName = function (input) {
    try {
        var reg = /^[a-zA-Z]{1}[\w]{3,24}$/;
        if (!reg.test(input)) {
            return false;
        }

        return true;
    }
    catch (err) {
        console.error("ERROR - Validation.validateDateTime() - Unable to validate datetime: " + err.message);
    }
}

Validation.validatePassword = function (input) {
    try {
        var reg = /^(?=.*?\d)(?=.*?[A-Za-z])(?=.*?[!@#])[0-9A-Za-z!@#]{6,18}$/;//^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#]).{6,16}$/;
        if (!reg.test(input)) {
            return false;
        }
        return true;
    }
    catch (err) {
        console.error("ERROR - Validation.validateDateTime() - Unable to validate datetime: " + err.message);
    }
}

Validation.validateProtocolName = function (input) {
    try {
        var reg = /^[\w]{1,16}$/;
        if (!reg.test(input)) {
            return false;
        }

        return true;
    }
    catch (err) {
        console.error("ERROR - Validation.validateDateTime() - Unable to validate datetime: " + err.message);
    }
}

Validation.validateNum = function (input) {
    try {

        var reg = /^[0-9]+$/;
        if (!reg.test(input)) {
            return false;
        }
        if (input < 1) {
            return false;
        }
        if (input > 102400000) {
            return false;
        }

        return true;
    }
    catch (err) {
        console.error("ERROR - Validation.validateNum() - Unable to validate num: " + err.message);
    }
}

Validation.validateNum1 = function (input) {
    try {

        var reg = /^[0-9]+$/;
        if (!reg.test(input)) {
            return 0;
        }
        if (input < 1) {
            return 0;
        }
        if (input > 102400000) {
            return 102400000;
        }

        return input;
    }
    catch (err) {
        console.error("ERROR - Validation.validateNum() - Unable to validate num: " + err.message);
    }
}

Validation.validateSpecialChart = function (input) {
    try {
        var pattern = new RegExp("[`~!@#$^&*()=|{}':;',\\[\\].<>/?~！@#￥……&*（）——|{}【】‘；：”“'。，、？]");
        if (pattern.test(input)) {
            return false;
        }
        return true;
    }
    catch (err) {
        console.error("ERROR - Validation.validateNum() - Unable to validate num: " + err.message);
    }
}
Validation.validatePin = function (input) {
    try {
        var reg = /^(?=.*?\d)(?=.*?[A-Za-z])(?=.*?[!@#])[0-9A-Za-z!@#]{8}$/;//^(?=.*[a-zA-Z])(?=.*\d)(?=.*[!@#]).{6,16}$/;
        if(!reg.test(input)){
            return false;
        }
        return true;
    }
    catch (err) {
        console.error("ERROR - Validation.validateDateTime() - Unable to validate datetime: " + err.message);
    }
}

Validation.validateMaskIP = function (input) {//ip+ip/掩码
    try {
        var reg = /^(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])(\.(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])){3}(\/([12][0-9]|3[0-2]|[0-9])){0,1}$/;
        if (!reg.test(input))
            return false;
        return true;
    }
    catch (err) {
        console.error("ERROR - Validation.validateMaskIP() - Unable to validate mask IP: " + err.message);
    }
}

Validation.validateComplexIPV6 = function (input) {
    try {
        var IPArray = input.split(",");
        for (var i = 0; i < IPArray.length; i++) {
            if (!Validation.validateIpv6Addr(IPArray[i],false)) {
                return false;
            }
        }
        return true;
    }
    catch (err) {
        console.error("ERROR - Validation.validateComplexIPV6() - Unable to validate complex IP: " + err.message);
    }
}

Validation.validateIpv6Addr=function(addrs,noRange){
    if(!noRange&&/-/.test(addrs)) {
        var ips = addrs.split('-');
        if (ips.length != 2) {
            return false;
        }
        if (ips[0] == ips[1]) {
            return false;
        }
        for (var i = 0; i < ips.length; i++) {
            if (!Validation.validateIPV6(ips[i])) {
                return false;
            }
        }
    }else if(/\//.test(addrs)){
        var ipmask=addrs.split('/');
        if(ipmask.length!=2){
            return false;
        }
        for(var i=0;i<ipmask.length;i++){
            if(!i){
                if(!Validation.validateIPV6(ipmask[i])){
                    return false;
                }
            }else{
                var subArr=ipmask[i].split('.');
                if(noRange&&subArr.length==4){
                    for(var j=0;j<subArr.length;j++){
                        if(!isNaN(Number(subArr[j]))){
                            if(!(Number(subArr[j])>=0 && Number(subArr[j])<256)){
                                return false;
                            }
                        }else{
                            return false;
                        }
                    }
                }else if(subArr.length==1){
                    if(!(Number(ipmask[i])>0&& Number(ipmask[i])<129)){
                        return false;
                    }
                }else{
                    return false;
                }
            }
        }
    }else{
        if(!Validation.validateIPV6(addrs)){
            return false;
        }
    }
    return addrs;
}

