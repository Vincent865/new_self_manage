:: Merges contents of each file in /scripts/screen/kea-c200/* into base.js
rem screen\kea-c200.js
copy /b screen\kea-c200\index\HeaderController.js+^
	spacer.js+^
	screen\kea-c200\index\MenuControlle.js+^
	spacer.js+^
	screen\kea-c200\home\HomeController.js ^
	screen\kea-c200.js