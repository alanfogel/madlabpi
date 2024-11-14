#!/bin/bash
crontab -l > file
cat cron_commands >> file
crontab file
rm file