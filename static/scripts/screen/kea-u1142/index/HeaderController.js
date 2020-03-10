function HeaderController(viewHandle) {
    this.pViewHandle = viewHandle;
    /*this.timer = {
     sysTimer: null,
     settingTimer: null,
     dbTimer: null
     };*/
}

HeaderController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES[APPCONFIG.PRODUCT].INDEX_HEADER), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);
        this.initControls();
        this.download_file();
        this.load();
    }
    catch (err) {
        console.error("ERROR - HeaderController.init() - Unable to initialize: " + err.message);
    }
}

HeaderController.prototype.load = function () {
    try {
        var parent = this,localInfo=JSON.parse(LocalStorageManager.getInstance()['pLocalStorage']['loginResponse']);
        //display user name
        var userInfo={
            auth:(function(){
                switch(localInfo['authority']){
                    case mstat:
                        return '系统管理员';
                    case astat:
                        return '安全审计员';
                    case ostat:
                        return '安全管理员';
                }
            })(),
            name:localInfo['username']
        };
        this.getSystemTime();
        clearInterval(checkonline);
        var checkonline=setInterval(function(){parent.getSystemTime(1)},30000);
        this.getSystemversion();
        var ws=io.connect(location.protocol+'//'+location.host+':443');
        ws.on('data_update',function(data){
            console.log(data.data);
            var date=new Date(data.data);
            clearInterval(gloTimer.sysTimer);
            parent.displaySysTime(date);
        });
        this.pViewHandle.find("#main_lblUserName").text(userInfo.auth+'：'+userInfo.name);
        //bind event for exiting system
        this.pViewHandle.find(".out-system").on("click", function () {
            AuthManager.getInstance().logOut();
        });
        //获取系统时间
        if (gloTimer.sysTimer != null) {
            clearInterval(gloTimer.sysTimer);
        }
        //获取配置保存状态
        if (gloTimer.settingTimer != null) {
            clearInterval(gloTimer.settingTimer);
        }
        this.getSettingStatus();
        gloTimer.settingTimer = setInterval(function () {
            parent.getSettingStatus();
        }, 20000);
        //获取数据库连接状态
        if (gloTimer.dbTimer != null) {
            clearInterval(gloTimer.dbTimer);
        }
        this.getDbStatus();
        gloTimer.dbTimer = setInterval(function () {
            parent.getDbStatus();
        }, 5000);
    }
    catch (err) {
        console.error("ERROR - HeaderController.load() - Unable to load: " + err.message);
    }
}

HeaderController.prototype.initControls = function () {
    try {
        var parent = this;
        $('.licensebtn').bind({click:function(e){
            e.stopPropagation();
            $('.license_info').toggle();
        }});
        $('.license_info').on({click:function(e){e.stopPropagation();}});
        $(window).bind({click:function(){$('.license_info').hide();}})
    }
    catch (err) {
        console.error("ERROR - HeaderController.initControls() - Unable to initialize control: " + err.message);
    }
}

HeaderController.prototype.download_file = function () {
    try {
        var parent = this;
        $('.downloadbtn').bind({click:function(e){
            open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].DOWNLOAD_FILE+'?loginuser='+JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']).username);
        }});
    }
    catch (err) {
        console.error("ERROR - HeaderController.download_file() - Unable to initialize control: " + err.message);
    }
}
HeaderController.prototype.getSystemversion = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEVICE_INFO;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            $("#sysSoftware").html(result.dpiInfo.version)
        });
    }
    catch (err) {
        console.error("ERROR - HeaderController.getSystemversion() - Unable to get device inforamtion: " + err.message);
    }
}

HeaderController.prototype.getSystemTime = function (more) {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_SYS_TIME;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            parent.displaySysTime(new Date());
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined") {
                if(!more){
                    var myDate = new Date(result.systime.replace(/-/g, '/'));
                    clearInterval(gloTimer.sysTimer);
                    parent.displaySysTime(myDate);
                }
            }
        });
    }
    catch (err) {
        console.error("ERROR - HeaderController.getSystemTime() - Unable to get system datetime: " + err.message);
    }
}

HeaderController.prototype.getSettingStatus = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_SETTING;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined" && result.status == 1) {
                if (result.flag == 1) {
                    parent.pViewHandle.find("#configStatus").removeClass("color-problem");
                    parent.pViewHandle.find("#configStatus").attr("title", "配置已保存");
                }
                else {
                    parent.pViewHandle.find("#configStatus").addClass("color-problem");
                    parent.pViewHandle.find("#configStatus").attr("title", "存在未保存的配置项");
                    parent.pViewHandle.find("#configStatus").unbind("click");
                    parent.pViewHandle.find("#configStatus").on("click", function () {
                        parent.saveSettingStatus();
                    });
                }
            }
        });
    }
    catch (err) {
        console.error("ERROR - HeaderController.getSettingStatus() - Unable to setting status: " + err.message);
    }
}

HeaderController.prototype.saveSettingStatus = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].UPDATE_SETTING;
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", {});
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("保存配置失败", { icon: 5 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined" && result.status == 1) {
                parent.pViewHandle.find("#configStatus").unbind("click");
                parent.pViewHandle.find("#configStatus").removeClass("color-problem");
            }
            else {
                layer.alert("保存配置失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - HeaderController.saveSettingStatus() - Unable to save new setting data: " + err.message);
    }
}

HeaderController.prototype.getDbStatus = function () {
    try {
        var parent = this;

        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_DB_STATUS;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 2:
                        parent.pViewHandle.find("#dbStatus").addClass("color-problem");
                        parent.pViewHandle.find("#dbStatus").attr("title", "数据库异常");
                        break;
                    case 3:
                        parent.pViewHandle.find("#dbStatus").addClass("color-problem");
                        parent.pViewHandle.find("#dbStatus").attr("title", "磁盘异常");
                        break;
                    default:
                        parent.pViewHandle.find("#dbStatus").removeClass("color-problem");
                        parent.pViewHandle.find("#dbStatus").attr("title", "数据库正常");
                        break;
                }
            }
            else {
                parent.pViewHandle.find("#dbStatus").attr("title", "数据库异常");
                parent.pViewHandle.find("#dbStatus").addClass("color-problem");
            }
        });
    }
    catch (err) {
        console.error("ERROR - HeaderController.getDbStatus() - Unable to get database connection status: " + err.message);
    }
}

HeaderController.prototype.displaySysTime = function (systime) {
    try {
        var parent = this;
        systime.setSeconds(systime.getSeconds() + 1);
        var year = systime.getFullYear();
        var month = systime.getMonth() + 1;
        var date = systime.getDate();
        var hours = systime.getHours();
        var minutes = systime.getMinutes();
        var seconds = systime.getSeconds();
        //月份的显示为两位数字如09月  
        if (month < 10) {
            month = "0" + month;
        }
        if (date < 10) {
            date = "0" + date;
        }
        if (hours < 10) {
            hours = "0" + hours;
        }
        if (minutes < 10) {
            minutes = "0" + minutes;
        }
        if (seconds < 10) {
            seconds = "0" + seconds;
        }
        //时间拼接  
        var displayTime = year + "-" + month + "-" + date + " " + hours + ":" + minutes + ":" + seconds;
        this.pViewHandle.find("#spanSystemTime").text(displayTime);
        gloTimer.sysTimer = setInterval(function () {
            var myDate = new Date($("#spanSystemTime").text().replace(/-/g, '/'));
            myDate.setSeconds(myDate.getSeconds() + 1);
            var year = myDate.getFullYear();
            var month = myDate.getMonth() + 1;
            var date = myDate.getDate();
            var hours = myDate.getHours();
            var minutes = myDate.getMinutes();
            var seconds = myDate.getSeconds();
            //月份的显示为两位数字如09月  
            if (month < 10) {
                month = "0" + month;
            }
            if (date < 10) {
                date = "0" + date;
            }
            if (hours < 10) {
                hours = "0" + hours;
            }
            if (minutes < 10) {
                minutes = "0" + minutes;
            }
            if (seconds < 10) {
                seconds = "0" + seconds;
            }
            //时间拼接  
            var displayTime = year + "-" + month + "-" + date + " " + hours + ":" + minutes + ":" + seconds;
            parent.pViewHandle.find("#spanSystemTime").text(displayTime);
        }, 1000);
    }
    catch (err) {
        console.error("ERROR - HeaderController.displaySysTime() - Unable to incorrect display system datatime: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.index.HeaderController", HeaderController);
