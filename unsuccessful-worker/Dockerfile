FROM quay.io/fenicsproject/stable:current
RUN apt-get update
RUN apt-get install -y python python-pip python-numpy gmsh
RUN python -m pip install --upgrade pip
RUN python -m pip install celery minio
RUN wget https://blob.novium.pw/shrx/2019/10/7FgjGco/murtazo.tgz
RUN tar xvf murtazo.tgz
RUN cd murtazo && tar xzf cloudnaca.tgz && tar xf navier_stokes_solver.tar
RUN cd murtazo/navier_stokes_solver/src && ./compile_forms && cd .. && cmake . && make -j 2
ENV PATH="/home/fenics/murtazo/navier_stokes_solver:${PATH}"
RUN cd /home/fenics/murtazo/cloudnaca && sed -i '20s/.*/GMSHBIN="\/usr\/bin\/gmsh"/' runme.sh

ARG CACHEBUST=8
WORKDIR /home/fenics/unsuccessful-worker

CMD ["celery -A tasks worker -l info"]
