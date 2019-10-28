from celery import Celery
import mysql.connector
import os
from minio import Minio
from datetime import timedelta
import numpy
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)

minioClient = Minio('data:9000',
                  access_key='admin',
                  secret_key='asdhgrwert12',
                  secure=False)

celery = Celery(__name__, broker='amqp://guest:guest@broker',backend='rpc://')

### Double check if database and table exists, else build it
db = mysql.connector.connect(
            host='db',
            user='root',
            password='123')
mycursor = db.cursor(buffered=True)

mycursor.execute('CREATE DATABASE IF NOT EXISTS airfoil')

db.commit()

mycursor.execute('''
            CREATE TABLE IF NOT EXISTS airfoil.results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                angle FLOAT(20, 10),
                status TEXT,
                url TEXT
            )
        ''')


#to upload result to minio
def upload_result(angle):
    bucketname='angle'+str(angle)
    zipfile='./results.tar.gz'
    try:
        minioClient.make_bucket(bucketname, location="us-east-1")
    except BucketAlreadyOwnedByYou as err:
        pass
    except BucketAlreadyExists as err:
        pass
    except ResponseError as err:
        raise

    try:
        downloadurl=minioClient.presigned_put_object(bucketname, zipfile,expires=timedelta(days=3))
    except ResponseError as err:
        print(err)
    return str(downloadurl)



@celery.task
def caculate(angle):

    #update mysql status
    try:
        sql = "INSERT INTO airfoil.results (angle, status, url) VALUES ("+str(angle)+", 'computing', 'url')"
        mycursor.execute(sql)
        db.commit()
    except:
        pass

    #generate mash
    generate_mash="cd ./murtazo/cloudnaca && ./runme.sh"+" "+str(angle)+" "+str(angle)+" 1"+" 200 3"
    os.system(generate_mash)

    #convert mash file
    mashfile='./murtazo/cloudnaca/msh/r2a'+str(angle)+'n200.msh'
    xmlfile='./murtazo/cloudnaca/msh/r2a'+str(angle)+'n200.xml'

    generate_xml='dolfin-convert '+mashfile+' '+xmlfile
    os.system(generate_xml)

    run_airfoil='./murtazo/navier_stokes_solver/airfoil  10 0.0001 10. 0.01 '+xmlfile
    os.system(run_airfoil)
    
    #zip result
    zipcommand='tar -zcvf results.tar.gz ./results'
    os.system(zipcommand)

    #upload to minio
    miniourl=upload_result(angle)

    #delete result folder and results.tar.gz
    os.system("rm -r results")
    os.system("rm -r results.tar.gz")

    #Update URL in db
    try:
        sql="UPDATE airfoil.results SET url = '"+miniourl+"' WHERE angle = '"+str(angle)+"'"
        mycursor.execute(sql)
        db.commit()
        #Update status in db
        try:
            sql="UPDATE airfoil.results SET status = 'done' WHERE angle = '"+str(angle)+"'"
            mycursor.execute(sql)
            db.commit()
        except:
            db.rollback()
    except:
        pass

    return miniourl

#calculate(12)
