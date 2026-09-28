import sys
import time
import os
import re
import argparse
import pandas
import pyarrow
import ray


from collections import Counter

from typing import List, Dict, Tuple, Any

# ---------------------------------------------------------------------------------------
def clean_strings(s):
    if s is None: return ''

    o = ''
    for c in s.lower():
        if c in 'abcdefghijklmnopqrstuvwxyz':
            o += c
        else:
            o += ' '
    return o
# ---------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------    
def batch_counting_words(batch : pandas.DataFrame) -> pandas.DataFrame:
    lwc = Counter()
    for row in batch.iterrows():
        lwc.update(clean_strings(row[1]['review_text']).split())
    #
    keys = list(lwc.keys())
    values = [lwc[k] for k in keys]
    return pandas.DataFrame({'word': keys, 'count': values})
# ----------------------------------------------------------------------------------------------------    
# ----------------------------------------------------------------------------------------------------    
def clean_and_strip(row) -> List:
    return [{'word': w, 'count': 1} for w in clean_strings(row['review_text']).split()]
# ----------------------------------------------------------------------------------------------------    


# static configuration for this example
data_dir = '/opt/asig/teaa-cd/data/text/goodreads_reviews_dedup'
column_name = "review_text"

def main(args):
    t0 = time.time()
    if args.cluster_type == 'local':
        ray.init(num_cpus = args.n_workers, object_store_memory = 128 * 1024 ** 3)
    else:
        ray.init()

    if args.num_files < 1:
        args.num_files = 787
    filenames = [f"{data_dir}/part_{i:04d}.json.gz" for i in range(args.num_files)]

    #batch_size = 1000
    batch_size = 20_000

    ds = ray.data.read_json(filenames)

    if args.verbose > 1:
        print(ds.schema())
        print(1, ds.count())

    # This will return a RAY DataSet based on Pandas DataFrame with two columns: 'word' and 'count'
    ds = ds.map_batches(batch_counting_words, batch_size = batch_size, batch_format = 'pandas')

    wc = Counter()
    for df_ref in ds.to_pandas_refs():
        df = ray.get(df_ref) # get the Pandas DataFrame object from its reference in the RAY distributed object store
        #wc.update({w: c for w, c in zip(df['word'], df['count'])}) # fails because in a Pandas object a key can be more than once
        for w, c in zip(df['word'], df['count']):
            if w in wc:
                wc[w] += c
            else:
                wc[w] = c

    total_different_words = len(wc)
    wc = wc.most_common(100)
    #wc = list(wc.items())

    wc.sort(key = lambda t: t[1], reverse = True)

    f = sys.stdout
    print("", file = f) # Necessary, don't ask me why ;-)
    for row in wc[:20]: # show the 20 more frequent words
        w, c = row
        print(f"WC: {c:12d}: {w}", file = f)
    print(f'WC: total different words {total_different_words}', file = f)
    print(f'WC: time {time.time() - t0} seconds', end = ' ', file = f)
    print(f"(n_workers: {args.n_workers}, cluster-type: {args.cluster_type})", file = f)
    if f != sys.stdout and f != sys.stderr: f.close()

    #ray.shutdown()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
                prog = 'wordcount.py',
                description = 'Wordcount example to illustrate how to implement map-reduce using RAY',
                epilog = 'That\'s all folks!!!')

    parser.add_argument('--num-files',
                        dest = 'num_files',
                        type = int,
                        default = 0,
                        help = 'Number of input files to load from disk. 0 to indicate loading all'
    )
    parser.add_argument('--n-workers',
                        dest = 'n_workers',
                        type = int,
                        default = 5,
                        help = 'Number of workers in the cluster'
    )
    parser.add_argument('--cluster-type',
                        dest = 'cluster_type',
                        type = str,
                        default = 'local',
                        help = 'Cluster type to use. One of local, ssh and kubernetes'
    )
    parser.add_argument('--verbose',
                        dest = 'verbose',
                        type = int,
                        default = 0,
                        help = 'Verbosity level'
    )

    main(parser.parse_args())
