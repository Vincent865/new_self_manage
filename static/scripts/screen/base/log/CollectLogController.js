/**
 * Created by 刘写辉 on 2019/6/18.
 */
function CollectLogController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    //this.controller = controller;
    this.elementId = elementId;

    this.pBtnRefresh = "#" + this.elementId + "_btnRefresh";
    this.pBtnExport = "#" + this.elementId + "_btnExport";
    this.pBtnSearch = "#" + this.elementId + "_btnSearch";
    this.pBtnFilter = "#" + this.elementId + "_btnFilter";
    this.pDivFilter = "#" + this.elementId + "_divFilter";

    this.pTxtStartDateTime = "#" + this.elementId + "_txtStartDateTime";
    this.pTxtEndDateTime = "#" + this.elementId + "_txtEndDateTime";
    this.pDdlEventLvl = "#" + this.elementId + "_ddlEventLvl";
    this.pDdlDeviceType = "#" + this.elementId + "_ddlDeviceType";

    this.pTdLogList = "#" + this.elementId + "_tdLogList";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pLblTotalLog = "#" + this.elementId + "_lblTotalLog";

    this.pager = null;
    this.filter = {
        page: 1,
        devtype:'',
        level:'',
        starttime: "",
        endtime: ""
    };
}

CollectLogController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.COLLECT_LIST), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - OperationLogController.init() - Unable to initialize: " + err.message);
    }
}

CollectLogController.prototype.initControls = function () {
    try {
        var parent = this;

        this.pViewHandle.find(this.pBtnFilter).on("click", function () {
            parent.pViewHandle.find(parent.pTxtStartDateTime).val("");
            parent.pViewHandle.find(parent.pTxtEndDateTime).val("");
            parent.pViewHandle.find(parent.pBtnFilter).toggleClass("active");
            parent.pViewHandle.find(parent.pDivFilter).toggle();
            $(parent.pDdlDeviceType).multiselect('deselectAll',false);
            $(parent.pDdlEventLvl).multiselect('deselectAll',false);
            $(parent.pDdlEventLvl).multiselect('updateButtonText');
            $(parent.pDdlDeviceType).multiselect('updateButtonText');
        });

        this.pViewHandle.find(this.pBtnRefresh).on("click", function () {
            parent.filter.page = 1;
            parent.pager = null;
            parent.formatFilter();
            parent.selectLogs();
        });

        this.pViewHandle.find(this.pBtnSearch).on("click", function () {
            parent.filter.page = 1;
            parent.pager = null;
            parent.formatFilter();
            parent.selectLogs();
        });
    }
    catch (err) {
        console.error("ERROR - OperationLogController.initControls() - Unable to initialize control: " + err.message);
    }
}

CollectLogController.prototype.multishow = function (o,s,n) {
    var labels=[];
    if(!o.length){
        return '未选择';
    }
    if(o.length==s[0].length){
        return '全选';
    }
    if(o.length>n){
        o.each(function(i){
            if(i<=n){
                if ($(this).attr('label') !== undefined) {
                    labels.push($(this).attr('label'));
                }
                else {
                    labels.push($(this).html());
                }
            }
        });
        return labels.join(', ') + '...';
    }
    o.each(function(){
        if ($(this).attr('label') !== undefined) {
            labels.push($(this).attr('label'));
        }
        else {
            labels.push($(this).html());
        }
    });
    return labels.join(', ') + '';
};

CollectLogController.prototype.load = function () {
    try {
        var parent=this;
        this.selectLogs();
        $(this.pDdlEventLvl).multiselect({includeSelectAllOption: true,selectAllText:'全选',buttonText:(o,s)=>{
            return parent.multishow(o,s,3);
        }});
        $(this.pDdlDeviceType).multiselect({includeSelectAllOption: true,selectAllText:'全选',buttonText:(o,s)=>{
            return parent.multishow(o,s,2);
        }});
    }
    catch (err) {
        console.error("ERROR - OperationLogController.load() - Unable to load: " + err.message);
    }
}

CollectLogController.prototype.selectLogs = function () {
    var parent = this;
    var html = "";
    var loadIndex = layer.load(2);
    try {
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].COLLECT_LOG_LIST;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"GET",this.filter);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tr><td colspan='7'>暂无数据</td></tr>";
            parent.pViewHandle.find(parent.pTdLogList+">tbody").html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tr>";
                        html += "<td>" + ((parent.filter.page - 1) * 10 + (i + 1)) + "</td>";
                        html += "<td>" + new Date(result.rows[i][1]*1000).toISOString().replace(/(T)|([\.\w]{5}$)/g,' ').trim()+ "</td>";//FormatterManager.formatToLocaleDateTime(String(result.rows[i][1]))
                        html += "<td>" + result.rows[i][0] + "</td>";
                        html += "<td>" + result.rows[i][2] + "</td>";
                        html += "<td>" + result.rows[i][3] + "</td>";
                        html += "<td>" + parent.formatExecutetatus(result.rows[i][4]) + "</td>";
                        html += "<td>" + atob(result.rows[i][5]) + "</td>";
                        html += "</tr>";
                    }
                }
                else {
                    html += "<tr><td colspan='7'>暂无数据</td></tr>";
                }
            }
            else {
                html += "<tr><td colspan='7'>暂无数据</td></tr>";
            }
            parent.pViewHandle.find(parent.pTdLogList+">tbody").html(html);
            layer.close(loadIndex);

            if (parent.pager == null) {
                parent.pager = new tdhx.base.utility.PagerController(parent.pViewHandle.find(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.filter.page = pageIndex;
                    parent.selectLogs();
                });
                parent.pager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tr><td colspan='5'>暂无数据</td></tr>";
        this.pViewHandle.find(this.pTdLogList + ">tbody").html(html);
        layer.close(loadIndex);
        console.error("ERROR - OperationLogController.selectLogs() - Unable to get logs: " + err.message);
    }
}

CollectLogController.prototype.formatExecutetatus = function (status) {
    try {
        switch (status) {
            case 1: return "工作站类";
            case 2: return "数据库";
            case 3: return "网络设备";
            case 4: return "防火墙";
            case 5: return "横向正向隔离装置";
            case 6: return "横向反向隔离装置";
            case 7: return "纵向加密装置";
            case 8: return "防病毒系统";
            case 9: return "入侵检测系统";
            case 10: return "网络安全监测装置";
            default: return "";
        }
    }
    catch (err) {
        console.error("ERROR - OperationLogController.formatReadStatus() - Unable to format Executetatus: " + err.message);
    }
}

CollectLogController.prototype.formatFilter = function () {
    try {
        var sels={lev:[],dtype:[]};
        $(this.pDdlEventLvl+' option:selected').each(function(){
            sels.lev.push($(this).val());
        });
        $(this.pDdlDeviceType+' option:selected').each(function(){
            sels.dtype.push($(this).val());
        });
        var sdate=$.trim(this.pViewHandle.find(this.pTxtStartDateTime).val()),edate=$.trim(this.pViewHandle.find(this.pTxtEndDateTime).val());
        this.filter.level = sels.lev.join(',');
        this.filter.devtype = sels.dtype.join(',');
        this.filter.starttime = sdate?new Date(sdate).getTime()/1000:'';
        this.filter.endtime = edate?new Date(edate).getTime()/1000:'';
    }
    catch (err) {
        console.error("ERROR - OperationLogController.formatFilter() - Unable to get filter: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.collect.CollectLogController", CollectLogController);