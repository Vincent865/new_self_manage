function DefineDialogController(controller, viewHandle, elementId, id, src, dst, protocol, status, action) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.controller = controller;
    this.id = id;
    this.src = src;
    this.dst = dst;
    this.protocol = protocol;
    this.status = status;
    this.action = action;

    this.definedProtocol = [];

    this.pBtnAdd = "#" + this.elementId + "_btnAdd";
    this.pTxtSource = "#" + this.elementId + "_txtSource";
    this.pTxtDestionation = "#" + this.elementId + "_txtDestination";
    this.pDdlType = "#" + this.elementId + "_ddlType";
    this.pDdlProtocol = "#" + this.elementId + "_ddlProtocol";

    this.pDivProtocolDetail = "#" + this.elementId + "_divProtocolDetail";
    this.pDdlProtocolType = "#" + this.elementId + "_ddlProtocolType";
    this.pTxtProtocolName = "#" + this.elementId + "_txtProtocolName";
    this.pTxtProtocolPort = "#" + this.elementId + "_txtProtocolPort";
}

DefineDialogController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.RULE_WHITELIST_IPS_DEFINE_DIALOG), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - DefineDialogController.init() - Unable to initialize: " + err.message);
    }
}

DefineDialogController.prototype.initControls = function () {
    try {
        var parent = this;

        if (typeof (this.src) != "undefined" && this.src != "") {
            $(this.pTxtSource).val(this.src);
        }

        if (typeof (this.dst) != "undefined" && this.dst != "") {
            $(this.pTxtDestionation).val(this.dst);
        }

        if (typeof (this.action) != "undefined" && this.action != "") {
            $(this.pDdlType).val(this.action);
        }

        this.bindProtocol();
        if (typeof (this.protocol) != "undefined" && this.protocol != "") {
            $(this.pDdlProtocol).val(this.protocol);
        }

        $(this.pDivProtocolDetail).hide();

        $(this.pBtnAdd).on("click", function () {
            if (parent.id == 0) {
                parent.addDefineWhitelist();
            }
            else {
                parent.updateDefineWhitelist();
            }
        });

        $(this.pDdlProtocol).on("change", function () {
            $(parent.pTxtProtocolName).val("");
            $(parent.pTxtProtocolPort).val("");
            if ($(this).val() == "") {
                $(parent.pDivProtocolDetail).show();
            }
            else {
                $(parent.pDivProtocolDetail).hide();
            }
        });

        //$(this.pTxtSource).on("blur", function () { parent.validate(); });
        //$(this.pTxtDestionation).on("blur", function () { parent.validate(); });      

        $(".rule-single-select").ruleAdvanceSelect();
        $(this.pDdlProtocol).parents(".rule-single-select").find(".select-items>ul").height(150);
        $(this.pDdlProtocol).parents(".rule-single-select").find("ul>li>b").on("click", function (e) {
            e.stopPropagation();
            var obj = this;
            layer.confirm("您确认需要删除自定义协议吗？", {
                title: "提示",
                btn: ["确定", "取消"],
                btn1: function (index, layero) {
                    var parentLi = $(obj).parent();
                    parentLi.find("b").remove();
                    var protocolName = parentLi.text();
                    var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].DELETE_DEFINED_PROTOCOL_LIST + "?name=" + protocolName;
                    var promise = URLManager.getInstance().ajaxCall(link);
                    promise.fail(function (jqXHR, textStatus, err) {
                        console.log(textStatus + " - " + err.message);
                        layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
                    });
                    promise.done(function (result) {
                        if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                            switch (result.status) {
                                case 1:
                                    layer.close(index);
                                    parent.bindProtocol();
                                    $(".rule-single-select").ruleAdvanceSelect();
                                    $(parent.pDdlProtocol).parents(".rule-single-select").find(".select-items>ul").height(150);
                                    break;
                                default:
                                    layer.alert("删除自定义协议失败", { icon: 5 });
                                    break;
                            }
                        }
                        else {
                            layer.alert("删除自定义协议失败", { icon: 5 });
                        }
                    });
                }
            });
        })

    }
    catch (err) {
        console.error("ERROR - DefineDialogController.initControls() - Unable to initialize control: " + err.message);
    }
}

DefineDialogController.prototype.load = function () {
    try {
    }
    catch (err) {
        console.error("ERROR - DefineDialogController.load() - Unable to load: " + err.message);
    }
}

DefineDialogController.prototype.bindProtocol = function () {
    try {
        var parent = this;
        $(this.pDdlProtocol).empty();

        this.controller.protocol.forEach(function (item, index) {
            parent.definedProtocol.push(item);
            $(parent.pDdlProtocol).append("<option value='" + item + "'>" + item + "</option>");
        });

        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_DEFINED_PROTOCOL_LIST;
        var promise = URLManager.getInstance().ajaxSyncCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined" && result.rows.length != 0) {
                result.rows.forEach(function (item, index) {
                    parent.definedProtocol.push(item[1]);
                    $(parent.pDdlProtocol).append("<option value='" + item[1] + "' isRemoved>" + item[1] + "</option>");
                });
            }
        });

        $(this.pDdlProtocol).append("<option value=''>自定义</option>");
    }
    catch (err) {
        console.error("ERROR - DefineDialogController.bindProtocol() - Unable to init protocol list: " + err.message);
    }
}

DefineDialogController.prototype.addDefineWhitelist = function () {
    try {
        var parent = this;
        var source = $.trim($(this.pTxtSource).val().toLowerCase());
        var destionation = $.trim($(this.pTxtDestionation).val().toLowerCase());
        var type = $(this.pDdlType + " option:selected").val();
        var protocol = $(this.pDdlProtocol + " option:selected").val();
        var protocolType = $(this.pDdlProtocolType + " option:selected").val();
        var protocolName = $(this.pTxtProtocolName).val();
        var protocolPort = $(this.pTxtProtocolPort).val();
        if (!this.validate(source, destionation, protocol, protocolName, protocolPort)) {
            return false;
        }
        var user_defined = 0;
        if (this.controller.protocol.indexOf(protocol) < 0) {
            if (protocol == "") {
                user_defined = 1;
                protocol = protocolType;
            }
            else {
                user_defined = 2;
                protocolType = "";
                protocolName = "";
                protocolPort = "";
            }
        }
        else {
            protocolType = "";
            protocolName = "";
            protocolPort = "";
        }

        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].ADD_DEFINE_WHITELIST
                + "?srcaddr=" + source + "&dstaddr=" + destionation
                + "&action=" + type + "&user_defined=" + user_defined
                + "&protocol=" + protocol + "&port=" + protocolPort + "&name=" + protocolName;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        parent.controller.pWhitelistPager = null;
                        layer.closeAll();
                        break;
                    case 2:
                        layer.alert("白名单正在学习中，无法新增规则...", { icon: 5 });
                        break;
                    case 3:
                        layer.alert("规则数量超过最大限制50000条，无法新增规则...", { icon: 5 });
                        break;
                    case 4:
                        layer.alert("服务名重复，无法新增...", { icon: 5 });
                        break;
                    default: layer.alert("添加规则失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("添加规则失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - DefineDialogController.addDefineWhitelist() - added whitelist failed: " + err.message);
    }
}

DefineDialogController.prototype.updateDefineWhitelist = function () {
    try {
        var parent = this;
        var source = $.trim($(this.pTxtSource).val().toLowerCase());
        var destionation = $.trim($(this.pTxtDestionation).val().toLowerCase());
        var type = $(this.pDdlType + " option:selected").val();
        var protocol = $(this.pDdlProtocol + " option:selected").val();
        var protocolType = $(this.pDdlProtocolType + " option:selected").val();
        var protocolName = $(this.pTxtProtocolName).val();
        var protocolPort = $(this.pTxtProtocolPort).val();
        if (!this.validate(source, destionation, protocol, protocolName, protocolPort)) {
            return false;
        }
        var user_defined = 0;
        if (this.controller.protocol.indexOf(protocol) < 0) {
            if (protocol == "") {
                user_defined = 1;
                protocol = protocolType;
            }
            else {
                user_defined = 2;
                protocolType = "";
                protocolName = "";
                protocolPort = "";
            }
        }
        else {
            protocolType = "";
            protocolName = "";
            protocolPort = "";
        }

        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].UPDATE_DEFINE_WHITELIST
                + "?srcaddr=" + source + "&dstaddr=" + destionation
                + "&action=" + type + "&user_defined=" + user_defined
                + "&protocol=" + protocol + "&port=" + protocolPort + "&name=" + protocolName + "&sid=" + this.id;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            layer.close(loadIndex);
            layer.alert("系统服务忙，请稍后重试！", { icon: 2 });
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        parent.controller.pWhitelistPager = null;
                        layer.closeAll();
                        break;
                    case 2:
                        layer.alert("白名单正在学习中，无修改规则...", { icon: 5 });
                        break;
                    case 3:
                        layer.alert("规则数量超过最大限制50000条，无法修改规则...", { icon: 5 });
                        break;
                    case 4:
                        layer.alert("服务名重复，无法修改...", { icon: 5 });
                        break;
                    default: layer.alert("修改规则失败", { icon: 5 }); break;
                }
            }
            else {
                layer.alert("修改规则失败", { icon: 5 });
            }
            layer.close(loadIndex);
        });
    }
    catch (err) {
        console.error("ERROR - DefineDialogController.updateDefineWhitelist() - updated whitelist failed: " + err.message);
    }
}

DefineDialogController.prototype.validate = function (source, destionation, protocol, protocolName, protocolPort) {
    try {
        var parent = this;
        switch (protocol) {
            case "":
                if (!Validation.validateProtocolName(protocolName)) {
                    layer.alert("请输入有效的自定义服务名称", { icon: 5 });
                    return false;
                }
                if (protocolPort == "" || !Validation.validatePort(protocolPort)) {
                    layer.alert("请输入自定义服务端口", { icon: 5 });
                    return false;
                }
                if (source != "" && source != "any" && !Validation.validateRangeIP(source)) {
                    layer.alert("请输入正确有效的起源IP", { icon: 5 });
                    return false;
                }
                if (destionation != "" && destionation != "any" && !Validation.validateRangeIP(destionation)) {
                    layer.alert("请输入正确有效的目的IP", { icon: 5 });
                    return false;
                }
                break;
            case "goose":
            case "sv":
            case "pnrtdcp":
                if (source != ""&&source !="any" && !Validation.validateMAC(source)) {
                    layer.alert("请输入正确有效的起源MAC", { icon: 5 });
                    return false;
                }
                if (destionation != "" && destionation != "any" && !Validation.validateMAC(destionation)) {
                    layer.alert("请输入正确有效的目的MAC", { icon: 5 });
                    return false;
                }
                break;
            default:
                if (source != "" && source != "any" && !Validation.validateRangeIP(source)) {
                    layer.alert("请输入正确有效的起源IP", { icon: 5 });
                    return false;
                }
                if (destionation != "" && destionation != "any" && !Validation.validateRangeIP(destionation)) {
                    layer.alert("请输入正确有效的目的IP", { icon: 5 });
                    return false;
                }
                break;
        }

        return true;

    }
    catch (err) {
        console.error("ERROR - DefineDialogController.updateDefineWhitelist() - updated whitelist failed: " + err.message);
        return false;
    }
}

ContentFactory.assignToPackage("tdhx.base.rule.DefineDialogController", DefineDialogController);