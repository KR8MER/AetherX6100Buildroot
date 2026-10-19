################################################################################
#
#  X6100 GUI
#
################################################################################

X6100_WEBSERVER_VERSION = e33056296c6e3445a2c2eb75e534ad59306194ad
X6100_WEBSERVER_SITE = https://github.com/KR8MER/x6100_webserver
X6100_WEBSERVER_SITE_METHOD = git
X6100_WEBSERVER_LICENSE = GPLv2
X6100_WEBSERVER_DEPENDENCIES = python-bottle-sqlite
X6100_WEBSERVER_SETUP_TYPE = flit

$(eval $(python-package))
