function PagerController(viewHandle, elementId, pageSize, total, changePageClickEvent) {
    this.pViewHandle = viewHandle;
    this.elementId = elementId;
    this.pageSize = (typeof (pageSize) == "undefined" ? 0 : pageSize);
    this.pageIndex = 1;
    this.total = (typeof (total) == "undefined" ? 0 : total);
    this.pageCount = 1;
    this.changePageClickEvent = changePageClickEvent;

    this.pLblTotal = "#" + this.elementId + "_lblTotal";
    this.pBtnNextPage = "#" + this.elementId + "_btnNextPage";
    this.pBtnPrevPage = "#" + this.elementId + "_btnPrevPage";
    this.pLblCurrentPage = "#" + this.elementId + "_lblCurrentPage";
    this.pTxtPageNO = "#" + this.elementId + "_txtPageNO";
    this.pBtnGoPage = "#" + this.elementId + "_btnGoPage";
}

PagerController.prototype.init = function (templateId) {
    try {
        var parent = this;
        var tabTemplate = TemplateManager.getInstance().updateTemplate(TemplateManager.getInstance().getTemplate(templateId), {
            elementId: parent.elementId
        });
        this.pViewHandle.html(tabTemplate);

        //render pager UI
        this.renderUI();
        //init all controls and load data
        this.initControls();
    }
    catch (err) {
        console.error("ERROR - PagerController.init() - Unable to initialize: " + err.message);
    }
}

PagerController.prototype.initControls = function () {
    try {
        var parent = this;
        $(this.pBtnNextPage).on("click", function () {
            $(parent.pTxtPageNO).val("");
            var index = parent.pageIndex + 1;
            if (index <= parent.pageCount) {
                parent.pageIndex = index;
                $(parent.pLblCurrentPage).html(parent.pageIndex);
                $(parent.pTxtPageNO).attr("placeholder", parent.pageIndex + "/" + parent.pageCount);
                $(parent.pTxtPageNO).attr("title", parent.pageIndex + "/" + parent.pageCount);
                parent.changePageClickEvent(parent.pageIndex);
            }
            else {
                layer.alert("已经是最后一页", { icon: 5 });
            }
        });
        $(this.pBtnPrevPage).on("click", function () {
            $(parent.pTxtPageNO).val("");
            var index = parent.pageIndex - 1;
            if (index >= 1) {
                parent.pageIndex = index;
                $(parent.pLblCurrentPage).html(parent.pageIndex);
                $(parent.pTxtPageNO).attr("placeholder", parent.pageIndex + "/" + parent.pageCount);
                $(parent.pTxtPageNO).attr("title", parent.pageIndex + "/" + parent.pageCount);
                parent.changePageClickEvent(parent.pageIndex);
            }
            else {
                layer.alert("已经是第一页", { icon: 5 });
            }
        });
        $(this.pBtnGoPage).on("click", function () {
            var index = parseInt($(parent.pTxtPageNO).val());
            var reg = /^[0-9]*[1-9][0-9]*$/;
            if (!reg.test(index) || index <= 0 || index > parent.pageCount) {
                layer.alert("请输入正确的页数", { icon: 5 });
            }
            else {
                parent.pageIndex = index;
                $(parent.pLblCurrentPage).html(parent.pageIndex);
                $(parent.pTxtPageNO).attr("placeholder", parent.pageIndex + "/" + parent.pageCount);
                $(parent.pTxtPageNO).attr("title", parent.pageIndex + "/" + parent.pageCount);
                parent.changePageClickEvent(parent.pageIndex);
            }
        });

        $(this.pTxtPageNO).attr("placeholder", "1/" + this.pageCount);
        $(this.pTxtPageNO).attr("title", "1/" + this.pageCount);
    }
    catch (err) {
        console.error("ERROR - PagerController.initControls() - Unable to initialize control: " + err.message);
    }
}

PagerController.prototype.renderUI = function () {
    try {
        var parent = this;
        if (typeof (this.pageSize) == "undefined" && typeof (this.total) == "undefined") {
            this.pageSize = 10;
            this.total = 0;
        }
        if (this.total == 0) {
            this.pViewHandle.html("");
            return;
        }
        if (typeof (this.pageIndex) == "undefined") {
            this.pageIndex = 1;
        }
        if (this.total % this.pageSize == 0) {
            this.pageCount = this.total / this.pageSize;
        }
        else {
            this.pageCount = parseInt(this.total / this.pageSize) + 1;
        }
        $(this.pLblTotal).html(this.total);
    }
    catch (err) {
        console.error("ERROR - PagerController.renderUI() - Unable to render page control: " + err.message);
    }
}

ContentFactory.assignToPackage("tdhx.base.utility.PagerController", PagerController);
