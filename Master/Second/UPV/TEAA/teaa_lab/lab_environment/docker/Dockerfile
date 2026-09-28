FROM ghcr.io/dask/dask:latest

RUN pip install scikit-learn xgboost pandas msgpack toolz dask-ml dask-expr distributed
RUN pip install scikit-learn xgboost pandas msgpack toolz dask-ml dask-expr distributed --upgrade

COPY configuration/packages.sh /packages.sh
RUN  /packages.sh

RUN mkdir /data
RUN chmod go+rwx /data
RUN ls -l /
