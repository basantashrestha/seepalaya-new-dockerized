#!/bin/bash
set -e

##Get latest pustakalaya database from EP server 
getlatest() {
latestsqlfile=`ssh -o "StrictHostKeyChecking no" ubuntu@pustakalaya.org ls -ltr /library/backup/postgres_backup/daily/pustakalaya | tail -n 1 | awk '{print $9}'`
sleep 10
scp ubuntu@pustakalaya.org:/library/backup/postgres_backup/daily/pustakalaya/$latestsqlfile /tmp/ &
scp_pid=$!
# Echo "Waiting..." until scp process is running
while ps -p $scp_pid > /dev/null; do
    echo "Waiting..."
    sleep 100 
done

# Once scp process is completed, echo transfer complete
echo "Transfer complete"

echo "Unziping..."
cd /home/olenepal/seepalaya-new-dockerized/seepalaya-new-database
bunzip2 /tmp/$latestsqlfile
mv /tmp/pustakalaya*.sql pustakalaya.sql 
}

##Run getlatest 
getlatest

rsync -ah gitlab-runner@olenepal.org:/home/gitlab-runner/builds/C8XRVxas/0/olenepal/seepalaya-new-backend/* /home/olenepal/seepalaya-new-dockerized/seepalaya-new-backend/
if [ "$?" == 0 ]; then
echo "backend sync is complete" 
else 
echo "backend sync is NOT done!!!"
fi

rsync -ah gitlab-runner@olenepal.org:/home/gitlab-runner/builds/C8XRVxas/0/olenepal/seepalaya-new-backend/* /home/olenepal/seepalaya-new-dockerized/seepalaya-new-celery/
if [ "$?" == 0 ]; then
echo "celery sync is complete" 
else 
echo "celery sync is NOT done!!!"
fi

rsync -ah gitlab-runner@olenepal.org:/home/gitlab-runner/builds/7XqTeJ4j/0/olenepal/seepalaya_new/* /home/olenepal/seepalaya-new-dockerized/seepalaya_new/
if [ "$?" == 0 ]; then
echo "frontend sync is complete" 
else 
echo "frontend sync is NOT done!!!"
fi

docker compose -f /home/olenepal/seepalaya-new-dockerized/docker-compose.yml stop && docker compose -f /home/olenepal/seepalaya-new-dockerized/docker-compose.yml build && docker compose -f /home/olenepal/seepalaya-new-dockerized/docker-compose.yml up -d 




