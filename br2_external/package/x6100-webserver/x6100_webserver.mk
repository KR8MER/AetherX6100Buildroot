################################################################################
#
#  X6100 GUI
#
################################################################################

X6100_WEBSERVER_VERSION = 8397c1049b61238a7e594822c6d592ce881a24b5
X6100_WEBSERVER_SITE = https://github.com/KR8MER/x6100_webserver
X6100_WEBSERVER_SITE_METHOD = git
X6100_WEBSERVER_LICENSE = GPLv2
X6100_WEBSERVER_DEPENDENCIES = python-bottle-sqlite
X6100_WEBSERVER_SETUP_TYPE = flit

$(eval $(python-package))
