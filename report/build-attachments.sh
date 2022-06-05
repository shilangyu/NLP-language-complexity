#!/bin/sh
set -e

prepare() {
	p=$1
	z=$2
	info=$3
	tag=$4

	rm $z || true

	zip -r $z $p

	sed -i'' -e "s|%$tag%|\\\textattachfile[color=0 0 1]{$z}{$z} -- $info|g" report.tex
}

prepare ../scraper/ scraper.zip 'Scraper source code' SCRAPER_ZIP
prepare ../data_cleaner/ data_cleaner.zip 'Data cleaner source code' DATA_CLEANER_ZIP
