// URLManager.js, for post/get/ajax
function URLManager() {
    this.pInstance = null;
}

URLManager.getInstance = function () {
    if (!this.pInstance) {
        this.pInstance = new URLManager();
    }
    return this.pInstance;
};

URLManager.prototype.init = function (data) {
    if (typeof (data) == "object")
        this.id2Url = data;
    else
        this.id2Url = APPCONFIG[APPCONFIG.PRODUCT].HTTP_URL + APPCONFIG[APPCONFIG.PRODUCT].ID2URL;
};

/**
 * this method will create ajax by env using default method and default async mode
 */
URLManager.prototype.ajaxCall = function (link, data) {
    try {
        var method = APPCONFIG[APPCONFIG.PRODUCT].HTTP_METHOD;
        return this.ajaxCallByURL(link, method, data);
    }
    catch (err) {
        console.error("ERROR - URLManager.ajaxCall() - Can not make ajax post call: " + err.message);
    }
};
/**
* this method will create ajax by env using default method and default async mode
*/
URLManager.prototype.ajaxSyncCall = function (link, data) {
    try {
        var method = APPCONFIG[APPCONFIG.PRODUCT].HTTP_METHOD;
        return this.ajaxCallByURL(link, method, data, false);
    }
    catch (err) {
        console.error("ERROR - URLManager.ajaxCall() - Can not make ajax post call: " + err.message);
    }
};
/**
 * @param data: json object or string, allowing json object accommodates backward compatibility, it will be converted to string
 * @param async: sync or async jax call
 * @param method: POST or GET
 * set processData  = false will prevent jquery to send data as query type string
 */
URLManager.prototype.ajaxCallByURL = function (link, method, data, async) {
    jQuery.support.cors = true;
    //if(link.indexOf("data") == 0 || link.indexOf("/data") == 0){
    //    method = "POST";
    //}
    //else if (APPCONFIG.ENV != "localhost" && (link.indexOf(".json") > 0 || link.indexOf(".txt") > 0)) {
    //    method = "GET"; // Override for DEV/Test development, for your local env, we have freedom to do POST
    //}

    var way = true;
    if (typeof (async) == "boolean") {
        way = async;
    }

    if (typeof (method) == "undefined" || method.toLowerCase() == "get") {
        link += "?loginuser=" + AuthManager.getInstance().getUserName();
        if (typeof (data) == "object") {
            for (var key in data) {
                link += "&" + key + "=" + data[key];
            }
        }
        data = null;
    }
    else {
        if (typeof (data) == "undefined") {
            data = {};
        }
        data["loginuser"] = AuthManager.getInstance().getUserName();
        data = JSON.stringify(data);
    }

    try {
        if (link) {
            var promise = $.ajax({
                url: link,
                dataType: "json",
                data: data,
                type: method,
                async: way,
                cache: false,
                contentType: "application/json; charset=utf-8",
                processData: false,
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    console.error("ERROR - URLManager.ajaxCallByURL() - Unable to retrieve URL: " + link + ". " + errorThrown);
                }
            });
            return promise;
        }
        else {
            return null;
        }
    }
    catch (err) {
        console.error("ERROR - URLManager.ajaxCallByURL() - Unable to retrieve URL: " + err.message);
        return "";
    }
};
