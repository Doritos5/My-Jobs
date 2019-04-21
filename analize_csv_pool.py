
## Author: Dor Mordechai.
## Home assignment

import time
import os
import argparse
import csv

try:
    from StringIO import StringIO   # for python 2
except ImportError:
    from io import StringIO         # for python 3

from concurrent.futures import ProcessPoolExecutor


def measure_runtime(func):
    # This decorator is wrapped over the main instance,
    # responsible for measuring the execution time of
    # the whole process, returned as a tuple along with
    # the original output.
    def execute_func(*args, **kwargs):
        timestamp = time.time()
        result = func(*args, **kwargs)
        runtime = time.time() - timestamp
        return result, runtime

    return execute_func


@measure_runtime
def filter_and_calc(file_name, min_age, max_age, pool_size):
    if not os.path.isfile(file_name):
        raise OSError('file name {name} does not exist'
                      .format(name=file_name))

    # Use workers to process the csv file in parallel.
    # Each of the workers is responsible for processing
    # a specific chunk of data.
    fsize = os.path.getsize(file_name)
    chunk_size = int(fsize / pool_size)

    features = list()
    with ProcessPoolExecutor(pool_size) as executor:
        seek_index = 0
        for _ in range(pool_size):
            feature = executor.submit(
                rows_processor_worker, file_name, min_age, max_age,
                seek_index, seek_index+chunk_size)
            features.append(feature)

            seek_index += chunk_size

        # When all the workers are done, sum up the results.
        counts = {'f': 0, 'm': 0, 'other': 0}
        for feature in features:
            result = feature.result()
            counts['f'] += result['f']
            counts['m'] += result['m']
            counts['other'] += result['other']

    return counts


def rows_processor_worker(file_name, min_age, max_age, start_index, stop_index):
    counts = {'f': 0, 'm': 0, 'other': 0}

    with open(file_name) as file:
        data = '{line}\n'.format(line=file.readline())

        # Iterate over the csv rows from start_index until
        # stop_index and count the relevant gender-per-age
        # records.
        file.seek(start_index)

        # Keep update the current position in the file to
        # detect when reached the stop_index.
        # Build block of data from the lines between the
        # given indexes to convert to csv.
        fposition = start_index
        while fposition <= stop_index:
            line = '{line}\n'.format(line=file.readline())
            data += line
            fposition += len(line)  # one char = one byte.


        reader = csv.DictReader(StringIO(data))
        for i, row in enumerate(reader):
            if i == 0:
                update_counts_by_row(row, counts, min_age, max_age, True)
            else:
                update_counts_by_row(row, counts, min_age, max_age)

    return counts


def update_counts_by_row(row, counts, min_age, max_age, is_first_line=False):
    try:
        age = float(row['age'])

        if min_age <= age <= max_age:
            gender = row['gender'].lower()

            if gender in ['f', 'm']:
                counts[gender] += 1
            else:
                counts['other'] += 1
    except (ValueError, KeyError):
        # Skip exceptions if this is the first row, that
        # might be partial.
        if not is_first_line:
            raise RuntimeError('corrupted data received: {row}'
                               .format(row=row))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='return a counts per gender of records '
                    'that fit the criteria (between ages)',
        usage='python filter_and_calc_parallel.py [file_name] '
              '[min_age] [max_age] [pool_size]')

    parser.add_argument(
        dest='file_name', type=str, help='file name (path)')
    parser.add_argument(
        dest='min_age', type=float, help='min age')
    parser.add_argument(
        dest='max_age', type=float, help='max age')
    parser.add_argument(
        dest='pool_size', nargs='?', type=int, default=4,
        help='pool size (default: 4)')

    res, rtime = filter_and_calc(**parser.parse_args().__dict__)

    print('result: {res} runtime: {rtime} seconds'
          .format(res=res, rtime=rtime))