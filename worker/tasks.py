from celery import Celery
import os
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,
                         BucketAlreadyExists)

minioClient = Minio('data',
                  access_key='admin',
                  secret_key='asdhgrwert12',
                  secure=True)

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
        minioClient.fput_object(bucketname, 'results.tar.gz', zipfile)
    except ResponseError as err:
        print(err)
    return 'url' #### can't figure out where it stored

@celery.task
def caculate(angle):

    #generate mash
    generate_mesh="cd ./murtazo/cloudnaca && ./runme.sh"+" "+str(angle)+" "+str(angle)+" 1"+" 200 3"
    os.system(generate_mesh)

    #convert mash file
    meshfile='./murtazo/cloudnaca/msh/r3a'+str(angle)+'n200.msh'
    xmlfile='./murtazo/cloudnaca/msh/r3a'+str(angle)+'n200.xml'

    generate_xml='dolfin-convert '+meshfile+' '+xmlfile
    os.system(generate_xml)

    run_airfoil='./murtazo/navier_stokes_solver/airfoil  10 0.0001 10. 0.01 '+xmlfile
    os.system(run_airfoil)
    
    #zip result
    zipcommand='tar -zcvf results.tar.gz ./results'
    os.system(zipcommand)

    #upload to minio !!!! THIS DOESN'T WORK !!!
    # miniourl=upload_result(angle)

    #delete result folder and results.tar.gz
    os.system("rm -r results")
    os.system("rm -r results.tar.gz")

    return "miniourl"

caculate(12)
