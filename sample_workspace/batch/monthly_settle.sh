#!/bin/bash
# 월 정산 배치: 매월 1일 전월 정산 데이터를 집계하여 확정 처리한다.
export JAVA_HOME=/usr/java/default
LOG=/logs/settle/monthly_$(date +%Y%m).log

echo "[$(date)] monthly settle batch start" >> $LOG
java -cp /app/lib/settle-batch.jar com.acme.settle.batch.MonthlySettleJob >> $LOG 2>&1
echo "[$(date)] monthly settle batch end rc=$?" >> $LOG
