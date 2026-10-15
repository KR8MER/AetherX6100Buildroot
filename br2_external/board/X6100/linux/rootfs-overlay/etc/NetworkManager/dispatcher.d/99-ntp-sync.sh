#!/bin/sh

. /etc/ntp-server.sh

interface=$1 status=$2
case "$status" in
  up)
    server=$(ntp_server)
    [ -n "$server" ] || server=time.nist.gov
    /usr/bin/ntpdate -u "$server" >> /var/log/ntpdate.log  2>&1 && \
    hwclock -w -f /dev/rtc1 >> /var/log/ntpdate.log  2>&1 && \
    touch /var/run/time-sync
    ;;
esac
