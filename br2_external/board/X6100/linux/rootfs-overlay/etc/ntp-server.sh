# The internet time server chosen in the GUI (Settings -> General -> Time
# server). The GUI writes one host name to the DATA partition; nothing is
# printed when none is chosen, or the file holds anything but a host name.
ntp_server() {
    s=$(head -n 1 /mnt/ntp_server 2>/dev/null | tr -d ' \t\r\n')
    case "$s" in
        "" | -* | *[!A-Za-z0-9.-]*) ;;
        *) echo "$s" ;;
    esac
}
