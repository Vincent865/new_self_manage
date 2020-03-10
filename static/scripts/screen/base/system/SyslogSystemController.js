/**
 * Created by 刘写辉 on 2018/7/31.
 */
/**
 * Created by inchling on 2017/11/6.
 */
function SyslogSystemController(controller,viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.isRedirect = true;
    this.isTestSuccess = false;
    //this.isResetSuccess = true;
    this.regStatus="#" + this.elementId +'_connectStatus';
    this.serverIp="#" + this.elementId +'_syslogIp';
    this.serverPort="#" + this.elementId +'_syslogPort';

    //this.pBtnTestStatus = "#" + this.elementId + "_btnTestStatus";
    this.pBtnConnectDevice = "#" + this.elementId + "_btnSyslogSave";

    this.pTip='#'+this.elementId+'_syslogTip';
    this.pDeviceController = controller;
}

SyslogSystemController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SYSTEM_SYSLOG), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        //this.load();
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.init() - Unable to initialize: " + err.message);
    }
}

SyslogSystemController.prototype.initControls = function () {
    try {
        var parent = this;

        this.getConnectStatus();
        /*$(this.pBtnTestStatus).on("click", function (event) {
            parent.testStatus();
        });
*/
        $(this.pBtnConnectDevice).on("click", function (e) {
            //if(e.target.innerText=='连接'){
            parent.connectDevice();
            /*}else{
             parent.disconnectDevice();
             }*/
        });
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.initControls() - Unable to initialize control: " + err.message);
    }
}

SyslogSystemController.prototype.load = function (info) {
    try {
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.load() - Unable to load: " + err.message);
    }
}

SyslogSystemController.prototype.commonExt = function (info,link,layerIndex,promise,spec) {
    try {
        //var sibNodes=$(this.pBtnTestStatus).siblings('input'),serverIp =sibNodes.eq(0).val(),serverPort=sibNodes.eq(1).val();
        var serverIp=$(this.serverIp).val(),serverPort=$(this.serverPort).val(),enabledStatus=Number($('#enable_switch').prop('checked'));
        if((serverIp&&serverPort)&&(Validation.validateIP(serverIp)&&Validation.validatePort(serverPort))){
            layerIndex = layer.msg(info, {
                time: 120000,
                shade: [0.5, '#fff']
            }, function () {
                if (parent.isTestSuccess==true) {
                    console.log('success');
                }
            });
            promise = !spec?URLManager.getInstance().ajaxCallByURL(link,'POST',{ip:serverIp,port:serverPort,status:enabledStatus}):URLManager.getInstance().ajaxCallByURL(link,'POST');
            return promise;
        }else{
            layer.alert('请输入正常的IP地址和端口',{icon:5});
            return false;
        }
    }
    catch (err) {
        console.error("ERROR - ResetSystemController.load() - Unable to load: " + err.message);
    }
}

SyslogSystemController.prototype.testStatus = function () {
    try {
        var parent = this,layerIndex,promise;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].TEST_SERVER_STATUS;

        /*var sibNodes=$(this.pBtnTestStatus).siblings('input'),serverIp =sibNodes.eq(0).val(),serverPort=sibNodes.eq(1).val();
         if((serverIp&&serverPort)&&(Validation.validateIP(serverIp)&&Validation.validatePort(serverPort))){
         var layerIndex = layer.msg("正在测试连接，请稍后...", {
         time: 120000,
         shade: [0.5, '#fff']
         }, function () {
         if (parent.isTestSuccess==true) {
         console.log('success');
         }
         });
         var promise = URLManager.getInstance().ajaxCallByURL(link,'POST',{ip:serverIp,port:serverPort});
         }else{
         layer.alert('请输入正常的IP地址和端口',{icon:5});
         return false;
         }*/
        promise=parent.commonExt("正在测试连接，请稍后...",link,layerIndex,promise);
        if(promise){
            promise.fail(function (jqXHR, textStatus, err) {
                console.log(textStatus + " - " + err.message);
                parent.isRebootSuccess = false;
                layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            });
            promise.done(function (result) {
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                    switch (result.status) {
                        case 1:
                            parent.isTestSuccess = true;
                            layer.alert("连接正常", { icon: 6 });
                            break;
                        default:
                            parent.isTestSuccess = false;
                            layer.alert("连接失败", { icon: 5 });
                            break;
                    }
                }
                else {
                    parent.isRebootSuccess = false;
                    layer.alert("连接失败", { icon: 5 });
                }
            });
        }else{
            return false;
        }
    }
    catch (err) {
        this.isRebootSuccess = false;
        console.error("ERROR - ResetSystemController.getDeviceRemote() - Unable to get the device remote status: " + err.message);
    }
}

SyslogSystemController.prototype.getConnectStatus = function () {
    try {
        var parent = this,layerIndex;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_SYSLOG_CONF;

        //var sibNodes=$(this.pBtnTestStatus).siblings('input'),serverIp =sibNodes.eq(0).val(),serverPort=sibNodes.eq(1).val();
        /*var layerIndex = layer.msg("正在获取配置状态，请稍后...", {
         time: 120000,
         shade: [0.5, '#fff']
         }, function () {
         if (parent.isTestSuccess == true) {
         console.log('success');
         }
         });*/
        var promise = URLManager.getInstance().ajaxCall(link);
        //promise=parent.commonExt("正在获取配置状态，请稍后...",link,layerIndex,promise,true);
        if(promise){
            promise.fail(function (jqXHR, textStatus, err) {
                console.log(textStatus + " - " + err.message);
                parent.isRebootSuccess = false;
                layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
            });
            promise.done(function (result) {
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                    switch (result.status) {
                        case 1:
                            //parent.isTestSuccess = true;
                            //layer.alert("连接正常", { icon: 5 });
                            //$(parent.regStatus).text(result.res.status?'已连接':'未连接');
                            $(parent.serverIp).val(result.res.ip);
                            $(parent.serverPort).val(result.res.port);
                            //result.res.status?$(parent.pBtnConnectDevice).addClass('btn-danger').text('断开连接'):$(parent.pBtnConnectDevice).removeClass('btn-danger').text('连接');
                            result.res.switch?$('#enable_switch').prop({checked:true}):$('#enable_switch').prop({checked:false});

                            break;
                        default:
                            parent.isTestSuccess = false;
                            layer.alert("获取配置失败", { icon: 5 });
                            break;
                    }
                }
                else {
                    parent.isRebootSuccess = false;
                    layer.alert("获取配置出错", { icon: 5 });
                }
            });
        }else{
            return false;
        }
    }
    catch (err) {
        this.isRebootSuccess = false;
        console.error("ERROR - ResetSystemController.getDeviceRemote() - Unable to get the device remote status: " + err.message);
    }
}

SyslogSystemController.prototype.connectDevice = function () {
    try {
        var parent = this,layerIndex,promise;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].PUT_SYSLOG_CONF;
        /*var layerIndex = layer.msg("正在连接服务器...", {
         time: 180000,
         shade: [0.5, '#fff']
         }/!*, function () {
         if (parent.isResetSuccess == true) {
         window.location.replace(APPCONFIG[APPCONFIG.PRODUCT].LOGIN_URL);
         }
         }*!/);
         var promise = URLManager.getInstance().ajaxCallByURL(link,'POST');*/

        promise=parent.commonExt("正在连接服务器，请稍后...",link,layerIndex,promise);
        if(promise) {
            promise.fail(function (jqXHR, textStatus, err) {
                console.log(textStatus + " - " + err.message);
                parent.isResetSuccess = false;
                layer.alert("系统服务忙，请稍后重试！", {icon: 2});
            });
            promise.done(function (result) {
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                    switch (result.status) {
                        case 1:
                            layer.alert('保存成功', {icon: 6});
                            parent.getConnectStatus();
                            //$(parent.pBtnConnectDevice).addClass('btn-danger').text('断开连接');
                            break;
                        /*case 2:
                         layer.alert('重复连接', {icon: 5});
                         break;
                         default:
                         //parent.isResetSuccess = false;
                         layer.alert("连接失败", {icon: 5});
                         break;*/
                        default:
                            layer.alert('保存失败', {icon: 5});
                    }
                }
                else {
                    parent.isResetSuccess = false;
                    layer.alert("连接服务器出错", {icon: 5});
                }
            });
        }
    }
    catch (err) {
        this.isResetSuccess = false;
        console.error("ERROR - ResetSystemController.getDeviceRemote() - Unable to get the device remote status: " + err.message);
    }
}

SyslogSystemController.prototype.disconnectDevice = function () {
    try {
        var parent = this,layerIndex,promise;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].DISCONNECT_DEVICE;
        /*var layerIndex = layer.msg("正在连接服务器...", {
         time: 180000,
         shade: [0.5, '#fff']
         }/!*, function () {
         if (parent.isResetSuccess == true) {
         window.location.replace(APPCONFIG[APPCONFIG.PRODUCT].LOGIN_URL);
         }
         }*!/);
         var promise = URLManager.getInstance().ajaxCallByURL(link,'POST');*/

        promise=parent.commonExt("正在断开服务器，请稍后...",link,layerIndex,promise,true);
        if(promise) {
            promise.fail(function (jqXHR, textStatus, err) {
                console.log(textStatus + " - " + err.message);
                parent.isResetSuccess = false;
                layer.alert("系统服务忙，请稍后重试！", {icon: 2});
            });
            promise.done(function (result) {
                if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                    switch (result.status) {
                        case 1:
                            layer.alert('断开接连成功', {icon: 5});
                            $(parent.pBtnConnectDevice).removeClass('btn-danger').text('点击连接');
                            break;
                        default:
                            //parent.isResetSuccess = false;
                            layer.alert("断开连接失败", {icon: 5});
                            break;
                    }
                }
                else {
                    parent.isResetSuccess = false;
                    layer.alert("断开连接服务器出错", {icon: 5});
                }
            });
        }
    }
    catch (err) {
        this.isResetSuccess = false;
        console.error("ERROR - ResetSystemController.getDeviceRemote() - Unable to get the device remote status: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.system.SyslogSystemController", SyslogSystemController);
