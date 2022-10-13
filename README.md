celery -A main:celery beat --loglevel=INFO  

celery -A main.celery worker --pool=solo -l info  


celery -A main.celery flower --port=28106  
