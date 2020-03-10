#!/bin/sh

echo "Starting merge JS KEA-C200 code!"

rm -f screen/kea-c200.js

cat screen/kea-c200/index/HeaderController.js\
	spacer.js\
	screen/kea-c200/index/MenuControlle.js\
	spacer.js\
	screen/kea-c200/home/HomeController.js\
	> screen/kea-c200.js

echo "Merge JS KEA-C200 code done!"

