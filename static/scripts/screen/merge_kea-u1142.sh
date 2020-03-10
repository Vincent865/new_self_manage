#!/bin/sh

echo "Starting merge JS KEA-U1142 code!"

rm -f screen/kea-u1142.js

cat screen/kea-u1142/index/HeaderController.js\
	spacer.js\
	screen/kea-u1142/index/MenuControlle.js\
	spacer.js\
	screen/kea-u1142/home/HomeController.js\
	> screen/kea-u1142.js

echo "Merge JS KEA-U1142 code done!"

