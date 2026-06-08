import polars as pl
import numpy as np

def convert_txt_to_parquet(fname, out_fname, columns=None):
    """
    Directly converts a raw CSV/text trajectory file to Parquet out-of-core.
    Saves RAM by streaming the conversion.
    
    If 'columns' is provided, the columns of the resulting Parquet file are renamed.
    Example columns: ['traj_id', 'x', 'y', 'z', 'vx', 'vy', 'vz', 'ax', 'ay', 'az', 'time']
    """
    lf = pl.scan_csv(fname, separator='\t', has_header=False)
    
    if columns is not None:
        old_cols = lf.columns
        mapping = dict(zip(old_cols, columns))
        lf = lf.rename(mapping)
        
    # Write directly to disk without loading into RAM
    lf.sink_parquet(out_fname)


def get_std_velocity_profiles(lf: pl.LazyFrame, start: float, stop: float, nbins: int, direction_col: str, kind_col: str):
    """
    Lazily computes the standard deviation of 'kind_col' along bins in 'direction_col'.
    lf: Polars LazyFrame (e.g. from pl.scan_parquet())
    """
    bin_size = (stop - start) / nbins
    
    res = (
        lf.filter((pl.col(direction_col) >= start) & (pl.col(direction_col) <= stop))
          .with_columns(
              bin_idx = ((pl.col(direction_col) - start) / bin_size).cast(pl.Int64)
          )
          .group_by('bin_idx')
          .agg(
              pl.col(kind_col).std().alias('std_val')
          )
          .collect() 
    )
    
    # Map bin_idx back to physical centers
    res = res.with_columns(
        center = start + (pl.col('bin_idx') + 0.5) * bin_size
    ).sort('center')
    
    return res['center'].to_numpy(), res['std_val'].to_numpy()


def get_mean_velocity_profiles(lf: pl.LazyFrame, start: float, stop: float, nbins: int, direction_col: str, kind_col: str):
    """
    Lazily computes the mean of 'kind_col' along bins in 'direction_col'.
    """
    bin_size = (stop - start) / nbins
    
    res = (
        lf.filter((pl.col(direction_col) >= start) & (pl.col(direction_col) <= stop))
          .with_columns(
              bin_idx = ((pl.col(direction_col) - start) / bin_size).cast(pl.Int64)
          )
          .group_by('bin_idx')
          .agg(
              pl.col(kind_col).mean().alias('mean_val')
          )
          .collect() 
    )
    
    res = res.with_columns(
        center = start + (pl.col('bin_idx') + 0.5) * bin_size
    ).sort('center')
    
    return res['center'].to_numpy(), res['mean_val'].to_numpy()


def get_velocity_increments_at_lag(lf: pl.LazyFrame, col: str, lag: int, group_col: str = 'traj_id', sort_col: str = 'time'):
    """
    Calculates (v(t+lag) - v(t)) for each trajectory in an out-of-core manner.
    Returns the raw increments as a 1D numpy array.
    """
    res = (
        lf.sort([group_col, sort_col])
          .select([
              (pl.col(col).shift(-lag).over(group_col) - pl.col(col)).alias('inc')
          ])
          .drop_nulls()
          .collect()
    )
    return res['inc'].to_numpy()


def get_velocity_list(lf: pl.LazyFrame, col: str):
    """
    Returns all values from a specified column as a 1D numpy array.
    Equivalent to get_velocity_list in analysis_tools.py.
    """
    res = lf.select(pl.col(col).drop_nulls()).collect()
    return res[col].to_numpy()

def get_velocity_increments(lf: pl.LazyFrame, kind: str, max_lag: int = 100, group_col: str = 'traj_id', sort_col: str = 'time'):
    '''
    For out-of-core data, this computes increments up to max_lag. 
    It returns a list of lists of increments, mimicking the original function.
    '''
    # We must map 'x', 'y', 'z' to 'vx', 'vy', 'vz' if the user passed 'x'
    if kind == 'x': col = 'vx'
    elif kind == 'y': col = 'vy'
    elif kind == 'z': col = 'vz'
    else: col = kind
    
    res_list = [[]] # index 0 is empty (lag 0)
    for lag in range(1, max_lag + 1):
        incs = get_velocity_increments_at_lag(lf, col=col, lag=lag, group_col=group_col, sort_col=sort_col)
        res_list.append(incs.tolist())
    return res_list
