#!/bin/bash
# updates DNS Entries on afraid.org, currently ipv4

freedns_url='http://freedns.afraid.org/dynamic'
# declare -a hostkeys=('Q.......dv2' 'Q.....TM5')
source ~/pers.env

if [ -z "${HOSTKEYS[*]}" ]
then
  echo "no hostkeys defined"
  exit 1
fi

# print date for log
date
for hostkey in "${HOSTKEYS[@]}"
do
    cacheip="/tmp/ip_${hostkey: -6}.cache"
    test -f $cacheip || touch $cacheip
        [ -r "${cacheip}" ] && read -r _date _time _oldip <<< "$(tail -1 "${cacheip}")"
        _newip="$(wget "${freedns_url}/check.php" -o /dev/null -O /dev/stdout | sed -n 's/^Detected.*: \(.\+\)/\1/p')"

        [ "${_newip}" == "${_oldip}" ] && printf "IP has not changed: %s\n" "${_newip}" && continue

        if wget -q --waitretry=5 --tries=4 "${freedns_url}/update.php?${hostkey}" -o /dev/null -O /dev/stdout; then
                printf "%s %s\n" "$(date +"%F %R")" "${_newip}" >> "${cacheip}"
                printf "IP updated: %s\n" "${_newip}"
        else
                printf "%s %s\n" "$(date +"%F %R")" "failed" >> "${cacheip}"
        fi
done
