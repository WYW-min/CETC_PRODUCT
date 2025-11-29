latest_log="$(ls -1t ./logs/*/pipeline_*.log | head -n1)"
error_log="$(ls -1t ./logs/*/error_*.log | head -n1)"
ln -sf "$latest_log" cur_log.log
ln -sf "$error_log" cur_error.log