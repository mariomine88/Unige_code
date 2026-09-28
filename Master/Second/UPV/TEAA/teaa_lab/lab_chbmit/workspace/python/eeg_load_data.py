import os
import sys
import time
import pickle
import gzip
import math
import numpy
import tempfile
import ray
import logging

# --------------------------------------------------------------------------------
def tts_to_label(tts):
    label = 0
    ### BEGIN: Students can change this to check other approaches
    if tts >   2     : label = 1
    if tts >  10 * 60: label = 2
    if tts >  20 * 60: label = 3
    if tts < -10     : label = 4
    if tts < -20 * 60: label = 5
    ### END: Students can change this to check other approaches
    return label
# --------------------------------------------------------------------------------
''' deprecated 2024-10-06
def generate_y_true(time_to_seizure):
    tts = time_to_seizure
    y_true = numpy.zeros(len(tts), dtype = int)
    y_true[tts >   2     ] = 1
    y_true[tts >  10 * 60] = 2
    y_true[tts >  20 * 60] = 3
    y_true[tts <    -10  ] = 4
    y_true[tts < -20 * 60] = 5
    y_true[tts == 0      ] = 0 # redundant, but just in case
    return y_true
'''
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
def csv_line_to_patient_tts_label_and_sample_binary_classification(line):
    parts = line.split(';')
    patient = parts[0]
    index = int(parts[1])
    tts = float(parts[2])
    label = 0 if tts == 0 else 1
    x = numpy.array([float(x) for x in parts[3:]])
    return [patient, index, tts, label, x]
# --------------------------------------------------------------------------------
def csv_batch_to_patient_tts_label_and_sample_binary_classification(batch):
    patient = list()
    index = list()
    tts = list()
    label = list()
    X = list()
    for _row_ in batch.iterrows():
        row = _row_[1]
        line = row['text']
        #print(line)
        line_data = csv_line_to_patient_tts_label_and_sample_binary_classification(line)
        patient.append(line_data[0])
        index.append(  line_data[1])
        tts.append(    line_data[2])
        label.append(  line_data[3])
        X.append(      line_data[4])
    return {'X': X, 'y': label, 'label': label, 'patient': patient, 'tts': tts, 'index': index}
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
def csv_line_to_patient_tts_label_and_sample_multiclass_classification(line):
    parts = line.split(';')
    patient = parts[0]
    index = int(parts[1])
    tts = float(parts[2])
    label = tts_to_label(tts)
    x = numpy.array([float(x) for x in parts[3:]])
    return [patient, index, tts, label, x]
# --------------------------------------------------------------------------------
def csv_batch_to_patient_tts_label_and_sample_multiclass_classification(batch):
    patient = list()
    index = list()
    tts = list()
    label = list()
    X = list()
    for _row_ in batch.iterrows():
        row = _row_[1]
        line = row['text']
        #print(line)
        line_data = csv_line_to_patient_tts_label_and_sample_multiclass_classification(line)
        patient.append(line_data[0])
        index.append(  line_data[1])
        tts.append(    line_data[2])
        label.append(  line_data[3])
        X.append(      line_data[4])
    return {'X': X, 'y': label, 'label': label, 'patient': patient, 'tts': tts, 'index': index}
# --------------------------------------------------------------------------------
# --------------------------------------------------------------------------------
def extract_and_gather_samples(l, block_size = None):
    r = []
    x = []
    y = []
    for sample in l:
        x.append(sample[4])
        y.append(sample[3])
        if block_size is not None and len(x) == block_size:
            r.append({'X': numpy.array(x), 'y': numpy.array(y)})
            x = []
            y = []
        #
    #
    if len(x) > 0:
        r.append({'X': numpy.array(x), 'y': numpy.array(y)})
    return r
# --------------------------------------------------------------------------------
def from_bag_to_samples(data, block_size = 1000, generate_local_samples = False):
    samples_bag = data.map_partitions(extract_and_gather_samples, block_size).persist()
    samples = numpy.vstack(samples_bag.map(lambda l: l['X']).compute()) if generate_local_samples else None
    return samples_bag, samples
# --------------------------------------------------------------------------------
def convert_to_binary_task(data):
    #                              patient    index      tts        label                       x
    return data.map(lambda sample: sample[0], sample[1], sample[2], 0 if sample[2] == 0 else 1, sample[4])
# --------------------------------------------------------------------------------
def convert_to_multiclass_task(data):
    #                              patient    index      tts        label                    x
    return data.map(lambda sample: sample[0], sample[1], sample[2], label_to_tts(sample[2]), sample[4])
# --------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------
@ray.remote
def ray_compute_count(_dict_):
    X = _dict_['X']
    assert len(X.shape) == 2
    return X.shape[0]
# ----------------------------------------------------------------------------------------

def load_csv_from_eeg(spark, dask_bag, ray, filenames, num_partitions = None, do_binary_classification = False):
    if spark is not None:
        # load files using Apache Spark
        rdd = None
        for filename in filenames:
            print(f'loading {filename}')
            csv_lines = spark.textFile(filename)
            if num_partitions is not None:
                csv_lines = csv_lines.repartition(num_partitions)
            if do_binary_classification:
                csv_lines = csv_lines.map(csv_line_to_patient_tts_label_and_sample_binary_classification)
            else:
                csv_lines = csv_lines.map(csv_line_to_patient_tts_label_and_sample_multiclass_classification)
            if rdd is not None:
                rdd = rdd.union(csv_lines)
            else:
                rdd = csv_lines
        print(f'loaded {rdd.count()} samples into {rdd.getNumPartitions()} partitions', flush = True)
        return rdd
    elif dask_bag is not None:
        print(f'starting to load {filenames}', flush = True)
        if do_binary_classification:
            db = dask_bag.read_text(filenames).map(csv_line_to_patient_tts_label_and_sample_binary_classification) # this will be persisted after performing some transformation when required
        else:
            db = dask_bag.read_text(filenames).map(csv_line_to_patient_tts_label_and_sample_multiclass_classification) # this will be persisted after performing some transformation when required
        print(f'loaded {db.count().compute()} samples into {db.npartitions} partitions', flush = True)
        return db
    elif ray is not None:
        ray_data_logger = logging.getLogger("ray.data")
        ray_data_logger.setLevel(logging.ERROR)

        if do_binary_classification:
            # this will be persisted after performing some transformation when required
            mds = ray.data.read_text(filenames, override_num_blocks = num_partitions).map_batches(csv_batch_to_patient_tts_label_and_sample_binary_classification, zero_copy_batch = True, batch_format = 'pandas').repartition(num_partitions).materialize()
        else:
            # this will be persisted after performing some transformation when required
            mds = ray.data.read_text(filenames, override_num_blocks = num_partitions).map_batches(csv_batch_to_patient_tts_label_and_sample_multiclass_classification, zero_copy_batch = True, batch_format = 'pandas').repartition(num_partitions).materialize()
        # **********************************************
        Xy_refs = mds.to_numpy_refs()
        """
        _sample_ = mds.take(2)
        print(type(_sample_))
        print(type(_sample_[0]))
        print(_sample_[0].keys(), _sample_[0]['X'].shape)
        del mds
        del _sample_
        """
        futures = [ray_compute_count.remote(_ref_) for _ref_ in Xy_refs]
        results = ray.get(futures)
        num_samples = sum(results)
        # **********************************************
        print(f'loaded {num_samples} samples into {len(Xy_refs)} blocks', flush = True)
        return Xy_refs
    else:
        # load files using opening files from the local filesystem
        data = []
        for filename in filenames:
            print(f'loading {filename}')
            f = gzip.open(filename, 'rt')
            for line in f:
                if do_binary_classification:
                    data.append(csv_line_to_patient_tts_label_and_sample_binary_classification(line.strip()))
                else:
                    data.append(csv_line_to_patient_tts_label_and_sample_multiclass_classification(line.strip()))
            f.close()
        print(f'loaded {len(data)} samples', flush = True)
        return data
# --------------------------------------------------------------------------------
