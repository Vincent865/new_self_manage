function ReportAssetController(viewHandle, elementId) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;

    this.pBtnSetting = "#" + this.elementId + "_btnSetting";
    this.pTdAssetReportList = "#" + this.elementId + "_tdAssetReportList";
    this.pDdlDurtion = "#" + this.elementId + "_ddlDurtion";
    this.pPagerContent = "#" + this.elementId + "_pagerContent";
    this.pBtnDelete = "#" + this.elementId + "_btnDelete";

    this.pBtnGenerate = "#" + this.elementId + "_btnGenerate";
    this.pTxtDevIP4 = "#" + this.elementId + "_txtDevIP4";
    this.pTxtDevIP6 = "#" + this.elementId + "_txtDevIP6";
    this.pLevel="[name=report_level]";

    this.pBtnFilter="#" + this.elementId + '_event_btnFilter';
    this.pAdvOpt='#' + this.elementId + "_advOpt";

    this.pAssetlistPager = null;
}

ReportAssetController.prototype.init = function () {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(Constants.TEMPLATES.REPORT_ASSET), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //init all controls and load data
        this.initControls();
        this.load();
    }
    catch (err) {
        console.error("ERROR - ReportAssetController.init() - Unable to initialize all templates: " + err.message);
    }
}

ReportAssetController.prototype.initControls = function () {
    try {
        var parent = this;
        $(this.pBtnSetting).on("click", function () {
            parent.setReportEventModel($(parent.pDdlDurtion).val());
        });
        $(this.pBtnFilter).bind({click:function(){
            parent.pViewHandle.find(parent.pTxtDevIP4).val("");
            parent.pViewHandle.find(parent.pTxtDevIP6).val("");
            parent.pViewHandle.find(parent.pLevel+"[value=1]").prop("checked",true);
            parent.pViewHandle.find(parent.pBtnFilter).toggleClass("active");
            $(parent.pAdvOpt).toggle();
        }});
        $(this.pBtnGenerate).on("click", function () {
            parent.setReportAlarmModel();
        });
        $(this.pBtnDelete).on("click", function () {
            parent.preDelete=[];
            $(parent.pTdAssetReportList).find('tbody input[type=checkbox]').filter('.selflag').each(function(i,d){
                if($(d).prop('checked')){
                    parent.preDelete.push($(d).data('id'));
                }
            });
            var delIds=parent.preDelete;
            if(parent.preDelete.length<=0){
                layer.alert('请选择需要删除的规则！',{icon:2});
                return;
            }
            layer.confirm('确定要删除么？',{icon:7,title:'注意：'}, function(index) {
                layer.close(index);
                parent.delReportList(delIds);
            })
        });
    }
    catch (err) {
        console.error("ERROR - ReportAssetController.initControls() - Unable to initialize control: " + err.message);
    }
}

ReportAssetController.prototype.load = function () {
    try {
        this.getReportAssetModel();
        this.selectAssetlists(1);
    }
    catch (err) {
        console.error("ERROR - ReportAssetController.load() - Unable to load: " + err.message);
    }
}

ReportAssetController.prototype.setReportAlarmModel = function (freq) {
    try {
        var parent = this;
        var layerLoad=layer.load(2, {content:'报告正在生成中...',shade: [0.4, '#fff'],success: function(layero) {
            layero.css('padding-left', '30px');
            layero.find('.layui-layer-content').css({
                'padding-left': '40px',
                'width': '170px',
                lineHeight:'32px',
                fontWeight:'bold'
            });
        }});
        var ip4 = $.trim($(this.pTxtDevIP4).val());
        var ip6 = $.trim($(this.pTxtDevIP6).val());
        var level = $.trim($(this.pLevel=":checked").val());
        if(ip4&&!Validation.validateComplexIP(ip4)) {
            layer.alert("请输入正确有效的IPV4地址", { icon: 5 });
            layer.close(layerLoad);
            return false;
        }
        if(ip6&&!Validation.validateComplexIPV6(ip6)) {
            layer.alert("请输入正确有效的IPV6地址", { icon: 5 });
            layer.close(layerLoad);
            return false;
        }
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].REPORT_ASSET_MANUAL;
        var data = {ipv4:ip4,ipv6:ip6,report_level:level};
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        layer.alert("操作成功", { icon: 6 });
                        parent.selectAssetlists();
                        break;
                    case 0:
                        layer.alert(result.msg, { icon: 5 });
                        layer.close(layerLoad);
                        break;
                }
            }
        });
    }
    catch (err) {
        console.error("ERROR - ReportEventController.getBlacklistDetails() - Unable to get safe event information: " + err.message);
    }
}

ReportAssetController.prototype.getReportAssetModel = function () {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_ASSET_MODEL;
        var promise = URLManager.getInstance().ajaxCall(link);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result.status) != "undefined" && typeof (result.freq) != "undefined") {
                switch (result.status) {
                    case 1:
                        $(parent.pDdlDurtion).val(result.freq);
                        break;
                }
            }
        });
    }
    catch (err) {
        console.error("ERROR - ReportAssetController.getBlacklistDetails() - Unable to get safe event information: " + err.message);
    }
}

ReportAssetController.prototype.setReportEventModel = function (freq) {
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].SET_ASSET_MODEL ;
        var data = { freq: freq };
        var promise = URLManager.getInstance().ajaxCallByURL(link, "POST", data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
        });
        promise.done(function (result) {
            if (typeof (result.status) != "undefined") {
                switch (result.status) {
                    case 1:
                        layer.alert("操作成功", { icon: 6 });
                        break;
                    case 0:
                        layer.alert("操作失败", { icon: 5 });
                        break;
                }
            }
        });
    }
    catch (err) {
        console.error("ERROR - ReportAssetController.getBlacklistDetails() - Unable to get safe event information: " + err.message);
    }
}

ReportAssetController.prototype.selectAssetlists = function (pageIndex) {
    var html = "";
    html += '<thead>';
    html += '<tr><th class="th-check" style="width:80px;"><input type="checkbox" class="chinput" id="selectAll"><label for="selectAll" ></label>全选</th>';
    html += '<th>报告日期</th><th>报告名称</th><th style="width:250px">操作</th></tr>';
    html += '</thead>';
    try {
        var parent = this;
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].GET_ASSET_REPORT_LIST;
        var data = {page:pageIndex};
        var loadIndex = layer.load(2);
        var promise = URLManager.getInstance().ajaxCall(link,data);
        promise.fail(function (jqXHR, textStatus, err) {
            console.log(textStatus + " - " + err.message);
            html += "<tbody><tr><td colspan='4'>暂无数据</td></tr></tbody>";
            $(parent.pTdAssetReportList).html(html);
            layer.close(loadIndex);
        });
        promise.done(function (result) {
            if (typeof (result) != "undefined" && typeof (result.rows) != "undefined") {
                if (result.rows.length > 0) {
                    for (var i = 0; i < result.rows.length; i++) {
                        html += "<tbody><tr>";
                        html += "<td>"+"<input type='checkbox' class='chinput selflag' data-idx='"+result.rows[i][1]+"' data-id=\""+result.rows[i][0]+"\" id=\""+result.rows[i][0]+"\" /><label for=\""+result.rows[i][0]+"\"></label></td>";
                        html += "<td>" + result.rows[i][2] + "</td>";
                        html += "<td><span class='tomodify'>" + result.rows[i][1]+ "</span>";
                        html += "<input type='text' style='display:none;' class='form-control'  value='"+result.rows[i][1]+"' title='"+result.rows[i][1]+"' placeholder='长度不超过128' maxlength='128'></td>";
                        html += "<td><button style='margin-right:5px;' class='btn btn-default btn-xs btn-color-details Editfile' data-key='" + result.rows[i][0] + "' data-file='" + result.rows[i][6] + "'><i class='fa fa-edit' style='margin-right:3px;'></i>编辑</button>";
                        html += '<span class="editform" style="display:none;"><button class="btn btn-primary btn-xs btn-primary-s" data-key="' + result.rows[i][0] + '">确认</button><button class="btn btn-danger btn-xs btn-danger-s">取消</button></span>';
                        html += "<button style='margin-right:5px;' class='btn btn-default btn-xs btn-color-details Detailfile' data-key='" + result.rows[i][0] + "' data-file='" + result.rows[i][6] + "'><i class='fa fa-level-down' style='margin-right:3px;'></i>详情下载</button>";
                        html += "<button class='btn btn-default btn-xs btn-color-details Reportfile' data-key='" + result.rows[i][0] + "' data-file='" + result.rows[i][6] + "' ><i class='fa fa-level-down' style='margin-right:3px;'></i>报表下载</button></td>";
                        html += "</tr></tbody>";
                    }
                }
                else {
                    html += "<tbody><tr><td colspan='4'>暂无数据</td></tr></tbody>";
                }
            }
            else {
                html += "<tbody><tr><td colspan='4'>暂无数据</td></tr></tbody>";
            }
            $(parent.pTdAssetReportList).html(html);
            layer.close(loadIndex);
            //详情下载及报告下载按钮
            $(parent.pTdAssetReportList).find("button.Detailfile").on("click", function (event) {
                var report_id=$(this).attr("data-key");
                window.open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].REPORT_ASSET_DETAIL_DOWNLOAD + report_id + '?loginuser='+JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']).username);
            });
            $(parent.pTdAssetReportList).find("button.Reportfile").on("click", function (event) {
                var report_id=$(this).attr("data-key");
                window.open(APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].REPORT_ASSET_DOWNLOAD + report_id + '?loginuser='+JSON.parse(LocalStorageManager.getInstance().pLocalStorage['loginResponse']).username);
            });
            //编辑按钮
            $(parent.pTdAssetReportList).find("button.Editfile").on("click", function (event) {
                $(this).parents('tr').find('.tomodify').hide().next().show();
                $(this).hide().next().show();
            });
            //取消
            $(parent.pTdAssetReportList).find(".editform button:nth-child(2n)").on("click", function (event) {
                $(this).parents('tr').find('.tomodify').show().next().hide();
                $(this).parent().hide().prev().show();
            });
            //确认
            $(parent.pTdAssetReportList).find(".editform button:nth-child(2n-1)").on("click", function (event) {
                var newName=$(this).parents('tr').find('.tomodify').next().val();
                if(newName==""){
                    layer.alert('报告名称不能为空',{icon:5});
                }else if(newName==$(this).parents('tr').find('.tomodify').text()){//名称相同不发请求
                    layer.alert('修改成功',{icon:6});
                    $(this).parents('tr').find('.tomodify').show().next().hide();
                    $(this).parent().hide().prev().show();
                }else{
                    var id=$(this).attr("data-key");
                    console.log($(this).attr("data-key"));
                    var loadIndex1 = layer.load(2),modpromise = URLManager.getInstance().ajaxCallByURL(link, "PUT", {id:id,assetsname:newName});
                    modpromise.fail(function (jqXHR, textStatus, err) {
                        console.log(textStatus + " - " + err.message);
                        layer.close(loadIndex1);
                    });
                    modpromise.done(function (result) {
                        if (result.status) {
                            layer.close(loadIndex1);layer.alert('修改成功',{icon:6});
                            parent.selectAssetlists();
                        }else{
                            layer.close(loadIndex1);layer.alert(result.msg,{icon:5});
                            parent.selectAssetlists();
                        }
                    });
                }
            });
            $("#selectAll").click(function(){
                parent.checkSwitch=!parent.checkSwitch;
                $(parent.pTdAssetReportList).find('input').filter('.selflag').prop('checked',parent.checkSwitch);
            });
            if (parent.pAssetlistPager == null) {
                parent.pAssetlistPager = new tdhx.base.utility.PagerController($(parent.pPagerContent), parent.elementId, 10, result.total, function (pageIndex) {
                    parent.selectAssetlists(pageIndex);
                });
                parent.pAssetlistPager.init(Constants.TEMPLATES.UTILITY_PAGER1);
            }
        });
    }
    catch (err) {
        html += "<tbody><tr><td colspan='4'>暂无数据</td></tr></tbody>";
        $(this.pTdAssetReportList).html(html);
        console.error("ERROR - ReportAssetController.selectAssetlists() - Unable to get all events: " + err.message);
    }
}
ReportAssetController.prototype.delReportList = function (delIds) {
    try {
        var parent = this;
        var loadIndex = layer.load(2, { shade: [0.4, '#fff'] });
        var link = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL+APPCONFIG[APPCONFIG.PRODUCT].GET_ASSET_REPORT_LIST;
        var promise = URLManager.getInstance().ajaxCallByURL(link,"DELETE",{id:delIds.join(',')});
        promise.fail(function (jqXHR, textStatus, err) {
            layer.alert("删除失败", { icon: 2 });
            console.log(textStatus + " - " + err.msg);
        });
        promise.done(function(res){
            if(res.status){
                layer.alert("删除成功", { icon: 6 });
                parent.selectAssetlists();
                if($(parent.pSelectAll).is(':checked')){
                    $(parent.pSelectAll).prop('checked',false);
                    parent.checkSwitch=false;
                    $(parent.pTdAssetReportList).find('input').prop('checked',parent.checkSwitch);
                }
            }else{
                layer.close(loadIndex);layer.alert("删除失败", { icon: 5 });
            }
        });
    }
    catch (err) {
        console.error("ERROR - ReportAssetController.delReportList() - Unable to delete auditReportList: " + err.message);
    }
}
ContentFactory.assignToPackage("tdhx.base.report.ReportAssetController", ReportAssetController);