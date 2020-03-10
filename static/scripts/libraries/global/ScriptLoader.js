//ScriptLoader.js, Asyc load js
function ScriptLoader() {
    this.pInstance = null;
    this.pLoadedLibraries = [];
    this.pNumToLoad = 0;
    this.pNumLoaded = 0;
    this.pLoadDetails = { numToLoad: 0, numLoaded: 0, requestQueue: [], callbacks: [] };
    this.pLoadInProgress = false;
}

ScriptLoader.getInstance = function () {
    if (!this.pInstance) {
        this.pInstance = new ScriptLoader();
    }
    return this.pInstance;
};

ScriptLoader.prototype.includeLibraries = function (libraryList, callback) {
    try {
        var i, n;
        var parent = this;
        var script;

        if (APPCONFIG.ENV == "localhost1" || APPCONFIG.ENV == "127.0.0.0") {
            callback(true); 
        }
        else if (typeof (libraryList) != "undefined" && libraryList != null) {
            this.pLoadDetails.requestQueue = this.pLoadDetails.requestQueue.concat(libraryList);
            this.pLoadDetails.numToLoad += libraryList.length;
            this.pLoadDetails.callbacks.push(callback);

            if (this.pLoadInProgress == false) {
                // If load process is not already going, then kick it off, 
                // otherwise the change will automatically get picked up after the next script file is finished loading
                this.pLoadInProgress = true;
                this.loadNextLibrary();
            }
        }
    }
    catch (err) {
        console.error("ERROR - ScriptLoader.includeLibraries(): " + err.message);
    }
};

// Load script libraries in a sequential manner, so that script load operations complete in the order they are declared.
// Prevents dependancy issues from libraries loading out of order, when one depends on another already being in place.
ScriptLoader.prototype.loadNextLibrary = function () {

    var requestQueue = this.pLoadDetails.requestQueue;
    var parent = this;
    var i, n;

    if (this.pLoadDetails.numLoaded < this.pLoadDetails.numToLoad) {
        if (typeof (this.pLoadedLibraries[requestQueue[this.pLoadDetails.numLoaded]]) == "undefined") {
            // Not yet loaded
            function proxy(modulePath) {
                $.ajax({
                    url: "/static/scripts/" + modulePath + "?v=" + APPCONFIG.VERSION,
                    dataType: "script",
                    cache: true,
                    success: function (data, status, jqxhr) {
                        parent.pLoadDetails.numLoaded++;
                        parent.pLoadedLibraries[modulePath] = true;
                        parent.loadNextLibrary();
                    }
                });
            }
            proxy(requestQueue[this.pLoadDetails.numLoaded]);
        }
        else {
            // Already loaded from a previous request, can skip over
            this.pLoadDetails.numLoaded++;
            this.loadNextLibrary();
        }

    }
    else {
        for (i = 0, n = this.pLoadDetails.callbacks.length; i < n; i++) {
            this.pLoadDetails.callbacks[i](true);
        }
        this.pLoadInProgress = false;
        this.pLoadDetails.numLoaded = 0;
        this.pLoadDetails.numToLoad = 0;
        this.pLoadDetails.requestQueue = [];
        this.pLoadDetails.callbacks = [];
    }
}

ScriptLoader.prototype.includeModule = function (moduleName, callback) {
    var loadedLibraries = [];

    switch (moduleName) {
        case "kea-c200":
            this.includeLibraries([
				"screen/kea-c200.js"
            ], callback);
            break;
        case "kea-u1000":
            this.includeLibraries([
				"screen/kea-u1000.js"
            ], callback);
            break;
        case "kea-u1142":
            this.includeLibraries([
				"screen/kea-u1142.js"
            ], callback);
            break;
    }
};
