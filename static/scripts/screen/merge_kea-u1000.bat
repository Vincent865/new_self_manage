:: Merges contents of each file in /scripts/screen/kea-u1000/* into base.js
rem screen\kea-u1000.js
copy /b screen\kea-u1000\index\HeaderController.js+^
	spacer.js+^
	screen\kea-u1000\index\MenuControlle.js+^
	spacer.js+^
	screen\kea-u1000\home\HomeController.js ^
	screen\kea-u1000.js