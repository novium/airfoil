FROM quay.io/fenicsproject/stable:current
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y python-pip
RUN apt-get install -y gmsh
RUN apt-get install python-numpy
RUN python -m pip install --upgrade pip
RUN python -m pip install celery
RUN python -m pip install minio
WORKDIR /fenicsworker
# CMD ["tar xzvf murtazo.tgz"]
# CMD ["cd /fenicsworker/murtazo && tar xvf cloudnaca.tgz"]
# CMD ["cd /fenicsworker/murtazo && tar xvf navier_stokes_solver.tar"] 
CMD ["cd /fenicsworker/murtazo/navier_stokes_solver/src && ./compile_forms"]
CMD ["cd /fenicsworker/murtazo/navier_stokes_solver && cmake ."]
CMD ["cd /fenicsworker/murtazo/navier_stokes_solver && make -j 2"]
CMD ["cd /fenicsworker && python tasks.py"]


