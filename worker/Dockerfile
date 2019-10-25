# Might require more RAM and Cores to be allocated to docker
# 2 cores and a few gigs of RAM should be 'nuff

FROM quay.io/fenicsproject/stable:current
RUN apt-get update
RUN apt-get install -y python3 python3-pip python3-numpy gmsh
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install celery minio
RUN wget https://blob.novium.pw/shrx/2019/10/7FgjGco/murtazo.tgz
RUN tar xvf murtazo.tgz
RUN cd murtazo && tar xzf cloudnaca.tgz && tar xf navier_stokes_solver.tar
RUN cd murtazo/navier_stokes_solver/src && ./compile_forms && cd .. && cmake . && make -j 2
ENV PATH="/home/fenics/murtazo/navier_stokes_solver:${PATH}"
RUN cd /home/fenics/murtazo/cloudnaca && sed -i '20s/.*/GMSHBIN="\/usr\/bin\/gmsh"/' runme.sh

WORKDIR /usr/share
ENTRYPOINT sh -c 'cd /usr/share && /usr/local/bin/celery -A worker worker'