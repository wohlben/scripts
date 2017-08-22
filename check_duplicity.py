#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python script to verify collection status of a duplicity backup
The BACKUP_TARGET is read from the bash variable 'DUPLICITY_BACKUP_TARGET'.
This can be hardcoded to the correct value (string) or kept as is.
"""

import subprocess as sub
from datetime import datetime, timedelta
from sys import exit as sys_exit
from os import environ


BACKUP_TARGET = environ['DUPLICITY_BACKUP_TARGET']
EXPECTED_BACKUPS = 2
ACCEPTABLE_AGE_OF_BACKUP = 1  # warning if exceeded
MAXIMUM_AGE_OF_BACKUP = 30  # critical if exceeded
ACCEPTABLE_AGE_OF_BACKUP = timedelta(days=ACCEPTABLE_AGE_OF_BACKUP)
MAXIMUM_AGE_OF_BACKUP = timedelta(hours=MAXIMUM_AGE_OF_BACKUP)


class Backup(object):
    "Class for getting the status of a duplicity backup and storing it"
    backup_target = str
    last_backup = datetime
    last_full_backup = datetime
    last_diff = datetime
    chain_start = datetime
    full_backups = 0
    status = "unknown"
    status_message = "to be determined"

    def __init__(self, backup_target):
        self.backup_target = backup_target
        self.set_backup_status(self.backup_target)

    def set_backup_status(self, backup_target: str) -> None:
        "executes Bash Command and evaluate the StdOut"
        backup_status = sub.check_output(["duplicity",
                                          "collection-status",
                                          backup_target]).decode('utf-8')
        for line in backup_status.split('\n'):
            if "Last full backup date:" in line:
                last_backup_string = line.split(':', 1)[-1]
                if last_backup_string == ' none':
                    break
                else:
                    self.last_full_backup = self.split_date(last_backup_string)
            if "Chain end time: " in line:
                last_diff_string = line.split(':', 1)[-1]
                self.last_diff = self.split_date(last_diff_string)
            if "Full " in line:
                self.full_backups += 1
            if "Chain start time: " in line:
                chain_start_string = line.split(':', 1)[-1]
                self.chain_start = self.split_date(chain_start_string)
        if self.last_diff > self.last_full_backup:
            self.last_backup = self.last_diff
        else:
            self.last_backup = self.last_full_backup
        return

    def split_date(self, date_string: str) -> datetime:
        "receives a datestring and returns a date object"
        backup_date = date_string.split()
        # weekday = backup_date[0]
        month = backup_date[1]
        day = int(backup_date[2])
        time = backup_date[3]
        year = int(backup_date[4])
        last_backup = datetime.strptime("{day}-{month}-{year}-{time}".format(
            day=day, month=month, year=year, time=time), "%d-%b-%Y-%H:%M:%S")
        return last_backup


class StatusMessages(object):
    "Facilitate the exits and exit codes on errors"
    messages = {
        "ok": 0,
        "warning": 1,
        "critical": 2,
        "unknown": 3
    }

    def exit(self, backup: Backup) -> None:
        "Exitpoint for the Check"
        print("{} | {}".format(backup.status, backup.status_message))
        sys_exit(self.messages[backup.status])


def main() -> None:
    "decides on the status message and exitcode"
    backup = Backup(BACKUP_TARGET)
    messenger = StatusMessages()
    today = datetime.today()

    if (EXPECTED_BACKUPS == backup.full_backups):
        if today - MAXIMUM_AGE_OF_BACKUP > backup.last_backup:
            backup.status = "critical"
            backup.status_message = "backup is ancient ({})".format(backup.last_backup.isoformat())

        elif today - ACCEPTABLE_AGE_OF_BACKUP > backup.last_backup:
            backup.status = "warning"
            backup.status_message = "Backup is old ({})".format(backup.last_backup.isoformat())

        else:
            backup.status = "ok"
            backup.status_message = "Backup is up-to-date ({})".format(
                backup.last_backup.isoformat())
            messenger.exit(backup)

    else:
        backup.status = "warning"
        backup.status_message = "{} of {} expected backups".format(
            backup.full_backups, EXPECTED_BACKUPS)
        if today - MAXIMUM_AGE_OF_BACKUP > backup.last_backup:
            backup.status = "critical"
            backup.status_message = "{} and backup is ancient ({})".format(
                backup.status_message, backup.last_backup.isoformat())

        elif today - ACCEPTABLE_AGE_OF_BACKUP > backup.last_backup:
            backup.status_message = "{} and backup is old ({})".format(
                backup.status_message, backup.last_backup.isoformat())

        messenger.exit(backup)
    return


if __name__ == "__main__":
    main()
