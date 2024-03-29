(function() {  
    var system = require('system');  
    var fs = require('fs');  
    var config = {  
        // default container width and height  
        DEFAULT_WIDTH : '800',
        DEFAULT_HEIGHT : '400'  
    }, parseParams, render, pick, usage;  
	var flag = 0;
	
    usage = function() {  
        console.log(
		"Usage: \n"  
		+ "-url     image load html \n"
		+ "-width   image save width \n"
		+ "-height  image save height \n"
		+ "-outfile image save outpath ,default path tmp \n"
		+ "-json    json string call local_main params \n"
	    );	
    };  
  
    pick = function() {
		
        var args = arguments, i, arg, length = args.length;  
        for (i = 0; i < length; i += 1) {  
            arg = args[i];  
			
            if (arg !== undefined && arg !== null && arg !== 'null' && arg != '0') {  
                return arg;  
            }  
        }  
    };  
  
    parseParams = function() {  
        var map = {}, i, key;  

        if (system.args.length < 2) {  
            usage();  
            phantom.exit();  
        }  
        for (i = 0; i < system.args.length; i += 1) {  
            if (system.args[i].charAt(0) === '-') {  
			
                key = system.args[i].substr(1, i.length);
				
				if(key == 'url') {
					var buff_url = system.args[i + 1].split('/');
					if(buff_url[buff_url.length-1].indexOf('1') > 0) {
						flag = 1;
					}else if(buff_url[buff_url.length-1].indexOf('2') > 0) {
						flag = 2;
					}else if(buff_url[buff_url.length-1].indexOf('3') > 0) {
						flag = 3;
					}else if(buff_url[buff_url.length-1].indexOf('4') > 0) {
						flag = 4;
					}
				}
				map[key] = system.args[i + 1];  
            }
        }
        return map;  
    };  
  
    render = function(params) {  
        var page = require('webpage').create();  

        page.onConsoleMessage = function(msg) {  
            console.log(msg);  
        };  
  
        page.onAlert = function(msg) {  
            console.log(msg);  
        };  
  
		var url = pick(params.url);
        // parse the params  
        page.open(url, function(status) {  
			if (status !== 'success') {
				console.log('Unable to load the address!');
				phantom.exit();
			} else {
				var width = pick(params.width, config.DEFAULT_WIDTH);  
				var height = pick(params.height, config.DEFAULT_HEIGHT);  
				// define the clip-rectangle  
				page.clipRect = {  
					top : 0,  
					left : 0,  
					width : width,  
					height : height  
				}; 
				
				page.evaluate(function(json_str){
					var json_args = JSON.parse(json_str);
					load_main(json_args);
				},params.json);
				
				window.setTimeout(function () {
						page.render(params.outfile);
						phantom.exit();
						console.log('export success');  
				}, 2000);
			}

        });  
    };  

    // get the args  
    var params = parseParams();  
	
	
    // validate the params  
    if (params.url === undefined ) {  
        usage();  
        phantom.exit();  
    }  
    // set the default out file  
    if (params.outfile === undefined) {  
        var tmpDir = fs.workingDirectory + '/tmp';  
        // exists tmpDir and is it writable?  
        if (!fs.exists(tmpDir)) {  
            try {  
                fs.makeDirectory(tmpDir);  
            } catch (e) {  
                console.log('ERROR: Cannot make tmp directory');  
            }  
        }  
        //params.outfile = tmpDir + "/" + new Date().getTime() + ".png";  
		if(flag == 1) {
			params.outfile = tmpDir + "/" + "sys_chart_1.png";
		}else if(flag == 2) {
			params.outfile = tmpDir + "/" + "sys_chart_2.png";
		}else if(flag == 3) {
			params.outfile = tmpDir + "/" + "sys_chart_3.png";
		}else if(flag == 4) {
			params.outfile = tmpDir + "/" + "sys_chart_4.png";
		}else {
			params.outfile = tmpDir + "/" + "error.png";
		}
		
    }  
  
    // render the image  
    render(params);  
}());  