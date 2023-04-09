#!/bin/bash
# Add the cron job to the crontab file
(crontab -l 2>/dev/null; echo "0 * * * * /usr/bin/curl http://localhost:5000/fetch_and_store_transactions") | crontab -
