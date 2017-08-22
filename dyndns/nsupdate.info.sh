#!/usr/bin/env bash
# updates dns entries on nsupdate.info, currently hardcoded to ipv6

# nsupdate_user="USERNAME:HOSTSECRET"
source ~/pers.env

if [ -z $nsupdate_user ]
then
  echo "no user:secret string defined"
  exit 1
fi

# check lockfile for  seconds since last successful update
if [ -f /tmp/dns_update ]
then
  lockfile_age="$(stat --format %Y /tmp/dns_update)"
else
  lockfile_age="$(date -d yesterday +%s)"
fi
last_execution="$(expr "$(date +%s)" - "${lockfile_age}")"

date

if [[ "${last_execution}" < "$(( 5 * 60 ))" ]]
then
  echo "last Update was ${last_execution} seconds ago, please give the DNS time to update"
  exit 1
fi

ipv6_addr="$(curl -s https://ipv6.nsupdate.info/myip)" # current ip addr
dns_addr="$(getent hosts ${nsupdate_user%:*} | awk '{ print $1 }')" # ip addr in DNS

if [ "${ipv6_addr}" != "${dns_addr}" ]
then
  echo -e "changed ${nsupdate_user%:*} addr from \n  ${dns_addr} to\n  ${ipv6_addr}"
  curl -s --user "${nsupdate_user}" https://ipv6.nsupdate.info/nic/update
  touch /tmp/dns_update
else
  echo "no changes for ${nsupdate_user%:*}"
fi
