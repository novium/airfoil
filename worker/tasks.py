from celery import Celery
import os
from datetime import timedelta
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)

minioClient = Minio('data',
                  access_key='admin',
                  secret_key='asdhgrwert12',
                  secure=TRUE)

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


celery = Celery(__name__, broker='pyamqp://',backend='rpc://')


@celery.task
def caculate(angle):

    #generate mash
    generate_mash="cd ./murtazo/cloudnaca && ./runme.sh"+" "+str(angle)+" "+str(angle)+" 1"+" 200 3"
    os.system(generate_mash)

    #convert mash file
    mashfile='./murtazo/cloudnaca/msh/r3a'+str(angle)+'n200.msh'
    xmlfile='./murtazo/cloudnaca/msh/r3a'+str(angle)+'n200.xml'

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

    return miniourl

#caculate(12)
