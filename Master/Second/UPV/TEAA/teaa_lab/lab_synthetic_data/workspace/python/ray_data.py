import sys
from typing import Any, Dict
import numpy
import ray
from ray.data.aggregate import AggregateFn

aggregation = AggregateFn(
    init = lambda column: 0,
    accumulate_row = lambda a, row: a + row['X'],
    merge = lambda a1, a2: a1 + a2,
    name = 'sum'
)

x_columns = [f'x{i + 1:02d}' for i in range(20)]

def map_batch_to_X_y(batch: Dict[str, numpy.ndarray]) -> Dict[str, numpy.ndarray]:
    #print(type(batch), batch.keys())
    X = numpy.array([batch[col] for col in x_columns]).T
    y = batch['y']
    #print('map_batch_to_X_y()', X.shape, y.shape)
    return {'X': X, 'y': y}
    
def map_to_X_y(row: Dict[str, Any]) -> Dict[str, Any]:
    #print(type(row), row.keys())
    X = numpy.array([row[col] for col in x_columns])
    y = row['y']
    return {'X': X, 'y': y}
    

ds = ray.data.read_parquet("/bigdata/disk/teaa/synthetic_data/parquet.test")
#ds = ray.data.read_parquet("/data/synthetic_data/parquet.train")

print(ds.schema())
#print(ds.show(2))
#b = ds.take_batch()
#print(type(b), len(b))
#print(b)

mds = ds.map_batches(map_batch_to_X_y, zero_copy_batch = True).materialize()
#mds = ds.map(map_to_X_y).materialize()
print(mds.count(), mds.num_blocks())
#print(mds.show(2))

#print(mds.aggregate(aggregation))
#print(mds.sum('X'))
#print(help(ds))

del ds

#X_refs = mds.to_numpy_refs(column = 'X')
#print(len(X_refs))
Xy_refs = mds.to_numpy_refs()#column = 'X')
print(len(Xy_refs))

print(mds.take(1))

del mds

@ray.remote
def ray_sum(_ref_):
    #print(_ref_.keys())
    X_chunk = _ref_['X']
    return X_chunk.sum(axis = 0)

futures = [ray_sum.remote(_ref_) for _ref_ in Xy_refs]
results = ray.get(futures)
print(len(results))
print(results[0])

print(numpy.vstack(results).sum(axis = 0))


@ray.remote
def ray_sample(_ref_, n):
    X_chunk = _ref_['X']
    return X_chunk[numpy.random.choice(len(X_chunk), n, replace = False)].copy()

futures = [ray_sample.remote(_ref_, 1) for _ref_ in Xy_refs]
results = ray.get(futures)
results = numpy.array(results)
results = results[numpy.random.choice(len(results), 3, replace = False)].copy()
print(results)
print(len(results))

sys.exit(1)

from RayKMeans import RayKMeans

kmeans = RayKMeans(n_clusters = 100, n_workers = 20, verbose = 2, codebook = numpy.random.randn(100, 20))
kmeans.fit(X_refs)
print(kmeans.wssse_)
