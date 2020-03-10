function SwitchinfoController(controller, viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.controller = controller;
    this.elementId = elementId;

    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pBtnEnable = "#" + this.elementId + "_btnEnable";
    this.pBtnDisable = "#" + this.elementId + "_btnDisable";

    this.pTxtIP = "#" + this.elementId + "_txtIP";
    this.pTxtMac = "#" + this.elementId + "_txtMac";
    this.pTxtDevice = "#" + this.elementId + "_txtDevice";
    this.pBtnAdd = "#" + this.elementId + "_btnAdd";

    this.pTdRuleList = "#" + this.elementId + "_tdRuleList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotal = "#" + this.elementId + "_pLblTotal";
    this.pBtnSearch='#' + this.elementId + "_btnSearch";
    this.pMacSearch = "#" + this.elementId + "_txtMacSearch";
    this.pager = null;
    this.filter = {
        page: 1
    };
}
SwitchinfoController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.SWITCH_INFO), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - SwitchinfoController.init() - Unable to initialize: " + err.message);
    }
}

SwitchinfoController.prototype.initControls = function () {
    try {
        var parent = this;
        $(this.pBtnSearch).on("click", function () {
            var val=$(parent.pMacSearch).val(),s=/^[0-9a-zA-Z:]{0,17}$/;
            if(!s.test(val)){
                layer.alert("请输入合法字符", { icon: 5 });$(parent.pMacSearch).val("");
            }else{
                parent.pager = null;
                parent.filter.page = 1;
                parent.selectRules();
            }
        });
    }
    catch (err) {
        console.error("ERROR - SwitchinfoController.initControls() - Unable to initialize control: " + err.message);
    }
}

SwitchinfoController.prototype.load = function () {
    try {
        this.selectRules();
        //this.getInitEventAction();
    }
    catch (err) {
        console.error("ERROR - SwitchinfoController.load() - Unable to load: " + err.message);
    }
}

SwitchinfoController.prototype.selectRules = function () {
    var html = "";
    var loadIndex = layer.load(2);
    try {
        var parent = this;
        this.filter.mac=$(this.pMacSearch).val();
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_SWITCH_MAC_INFO;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"POST", this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='5'>暂无数据</td></tr>";
            $(parent.pTdRuleList+">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td>" + ((parent.filter.page - 1) * 10 + 1 + i) + "</td>";
                        html += "<td>" + result.rows[i][0] + "</td>";
                        html += "<td>" + result.rows[i][2] + "</td>";
                        html += "<td>" + result.rows[i][1] + "</td>";
                        html += "<td>" + result.rows[i][3].toUpperCase() + "</td></tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='5'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='5'>暂无数据</td></tr>";
            }
            $(parent.pTdRuleList + ">tbody").html(html);
            layer.close(loadIndex);
            if (parent.pager == null) {
                parent.pager = new tdhx.base.utility.PagerController(parent.pViewHandle.find(parent.pPagerContent), parent.elementId, 10, result.num, function (pageIndex) {
                    parent.filter.page = pageIndex;
                    parent.selectRules();
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='5'>暂无数据</td></tr>";
        $(this.pTdRuleList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - SwitchinfoController.selectRules() - Unable to get all events: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.topo.SwitchinfoController", SwitchinfoController);