该文件在 neutron 安装时会被拷贝到 /etc/init.d下，作为操作系统的服务启动脚本。

```
#! /bin/sh
### BEGIN INIT INFO
# Provides:          neutron-server
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: neutron-server
# Description:       Provides the Neutron networking service
### END INIT INFO

set -e

PIDFILE=/var/run/neutron/neutron-server.pid
LOGFILE=/var/log/neutron/neutron-server.log

DAEMON=/usr/bin/neutron-server
DAEMON_ARGS="--log-file=$LOGFILE"
DAEMON_DIR=/var/run

ENABLED=true

if test -f /etc/default/neutron-server; then
  . /etc/default/neutron-server
fi

mkdir -p /var/run/neutron
mkdir -p /var/log/neutron

. /lib/lsb/init-functions

export PATH="${PATH:+$PATH:}/usr/sbin:/sbin"
export TMPDIR=/var/lib/neutron/tmp

if [ ! -x ${DAEMON} ] ; then  #确定 /usr/bin/neutron-server 文件的存在并可执行
    exit 0
fi

case "$1" in
  start)
    test "$ENABLED" = "true" || exit 0
    log_daemon_msg "Starting neutron server" "neutron-server"
    start-stop-daemon -Sbmv --pidfile $PIDFILE --chdir $DAEMON_DIR --exec $DAEMON -- $DAEMON_ARGS
    log_end_msg $?
    ;;
  stop)
    test "$ENABLED" = "true" || exit 0
    log_daemon_msg "Stopping neutron server" "neutron-server"
    start-stop-daemon --stop --oknodo --pidfile ${PIDFILE}
    log_end_msg $?
    ;;
  restart|force-reload)
    test "$ENABLED" = "true" || exit 1
    $0 stop
    sleep 1
    $0 start
    ;;
  status)
    test "$ENABLED" = "true" || exit 0
    status_of_proc -p $PIDFILE $DAEMON neutron-server && exit 0 || exit $?
    ;;
  *)
    log_action_msg "Usage: /etc/init.d/neutron-server {start|stop|restart|force-reload|status}"
    exit 1
    ;;
esac

exit 0

```



