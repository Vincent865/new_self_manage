#!/bin/sh

echo "Starting merge JS library code!"

rm -f libraries/library.js

cat libraries/3rdparty/jquery/jquery.min.js\
	spacer.js\
    libraries/3rdparty/jquery/jquery.form.min.js\
	spacer.js\
	libraries/3rdparty/jquery/jquery-ui-1.10.3.custom.min.js\
	spacer.js\
	libraries/3rdparty/wsio/socket.io.min.js\
    spacer.js\
    libraries/3rdparty/md5/jQuery.md5.js\
	spacer.js\
	libraries/3rdparty/jquery/jquery.typetype.min.js\
	spacer.js\
	libraries/3rdparty/jquery/Validform_v5.3.2_min.js\
	spacer.js\
	libraries/3rdparty/jquery/jtopo-0.4.8-min.js\
	spacer.js\
	libraries/3rdparty/bootstrap/bootstrap.min.js\
	spacer.js\
	libraries/3rdparty/multiselect/bootstrap-multiselect.js\
    spacer.js\
	libraries/3rdparty/echart/echarts-all.js\
	spacer.js\
	libraries/3rdparty/layer/layer.js\
	spacer.js\
	libraries/3rdparty/datepicker/WdatePicker.js\
	spacer.js\
	libraries/3rdparty/jspdf/FileSaver.min.js\
	spacer.js\
	libraries/3rdparty/jspdf/jspdf.js\
	spacer.js\
	libraries/3rdparty/jspdf/jspdf.plugin.addimage.js\
	spacer.js\
	libraries/3rdparty/jspdf/jspdf.plugin.split_text_to_size.js\
	spacer.js\
	libraries/3rdparty/jspdf/jspdf.plugin.standard_fonts_metrics.js\
	spacer.js\
	libraries/3rdparty/jspdf/wPDF.js\
	spacer.js\
	libraries/global/ExtensionControl.js\
	spacer.js\
	libraries/global/Constants.js\
	spacer.js\
	libraries/global/CookieManager.js\
	spacer.js\
	libraries/global/LocalStorageManager.js\
	spacer.js\
	libraries/global/FormatterManager.js\
	spacer.js\
	libraries/global/Validation.js\
	spacer.js\
	libraries/global/URLManager.js\
	spacer.js\
	libraries/global/TemplateManager.js\
	spacer.js\
	libraries/global/AuthManager.js\
	spacer.js\
	libraries/global/ContentFactory.js\
	spacer.js\
	libraries/global/ScriptLoader.js\
	> libraries/library.js

echo "Merge JS library code done!"

