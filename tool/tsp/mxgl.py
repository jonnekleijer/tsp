#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Tom van Steijn, Royal HaskoningDHV

def q_ghg(self, tmin=None, tmax=None, key='simulated', q=0.94):
        """Gemiddeld Hoogste Grondwaterstand (GHG) also called MHGL (Mean High Groundwater Level)
        Approximated by taking a quantile of the timeseries values, after
        resampling to daily values.


        This function does not care about series length!

        Parameters
        ----------
        key : None, optional
            timeseries key ('observations' or 'simulated')
        tmin, tmax: Optional[pd.Timestamp]
            Time indices to use for the simulation of the time series model.
        q : float, optional
            quantile, fraction of exceedance (default 0.94)

        Returns
        -------
        TYPE
            Description
        """
        series = self.bykey(key=key, tmin=tmin, tmax=tmax)
        series = series.resample('d').median()
        return series.quantile(q)

def q_glg(self, tmin=None, tmax=None, key='simulated', q=0.06):
    """Gemiddeld Laagste Grondwaterstand (GLG) also called MLGL (Mean Low Groundwater Level)
    Approximated by taking a quantile of the timeseries values, after
    resampling to daily values.

    This function does not care about series length!

    Parameters
    ----------
    key : None, optional
        timeseries key ('observations' or 'simulated')
    tmin, tmax : Optional[pd.Timestamp]
        Time indices to use for the simulation of the time series model.
    q : float, optional
        quantile, fraction of exceedance (default 0.06)

    Returns
    -------
    TYPE
        Description
    """
    series = self.bykey(key=key, tmin=tmin, tmax=tmax)
    series = series.resample('d').median()
    return series.quantile(q)

def __inspring__(self, series):
    """Test if timeseries index is between 14 March and 15 April.

    Parameters
    ----------
    series : pd.Series
        series with datetime index

    Returns
    -------
    pd.Series
        Boolean series with datetimeindex
    """
    isinspring = lambda x: (((x.month == 3) and (x.day >= 14)) or
                            ((x.month == 4) and (x.day < 15)))
    return series.index.map(isinspring)

def q_gvg(self, tmin=None, tmax=None, key='simulated'):
    """Gemiddeld Voorjaarsgrondwaterstand (GVG) also called MSGL (Mean Spring Groundwater Level)
    Approximated by taking the median of the values in the
    period between 14 March and 15 April (after resampling to daily values).

    This function does not care about series length!

    Parameters
    ----------
    key : None, optional
        timeseries key ('observations' or 'simulated')
    tmin, tmax: Optional[pd.Timestamp]
        Time indices to use for the simulation of the time series model.

    Returns
    -------
    TYPE
        Description
    """
    series = self.bykey(key=key, tmin=tmin, tmax=tmax)
    series = series.resample('d').median()
    inspring = self.__inspring__(series)
    if np.any(inspring):
        return series.loc[inspring].median()
    else:
        return np.nan

def d_ghg(self, tmin=None, tmax=None):
    """
    Difference in GHG between simulated and observed values

    Parameters
    ----------
    tmin, tmax: Optional[pd.Timestamp]
        Time indices to use for the simulation of the time series model.

    Returns
    -------
    TYPE
        Description
    """
    return (self.q_ghg(tmin=tmin, tmax=tmax, key='simulated') -
            self.q_ghg(tmin=tmin, tmax=tmax, key='observations'))

def d_glg(self, tmin=None, tmax=None):
    """
    Difference in GLG between simulated and observed values

    Parameters
    ----------
    tmin, tmax: Optional[pd.Timestamp]
        Time indices to use for the simulation of the time series model.

    Returns
    -------
    TYPE
        Description
    """
    return (self.q_glg(tmin=tmin, tmax=tmax, key='simulated') -
            self.q_glg(tmin=tmin, tmax=tmax, key='observations'))

def d_gvg(self, tmin=None, tmax=None):
    """
    Difference in GVG between simulated and observed values

    Parameters
    ----------
    tmin, tmax: Optional[pd.Timestamp]
        Time indices to use for the simulation of the time series model.

    Returns
    -------
    TYPE
        Description
    """
    return (self.q_gvg(tmin=tmin, tmax=tmax, key='simulated') -
            self.q_gvg(tmin=tmin, tmax=tmax, key='observations'))

def gxg(self, year_agg, tmin, tmax, key, fill_method, limit, output):
    """Worker method for classic GXG statistics.
    Resampling the series to every 14th and 28th of the month.
    Taking the mean of aggregated values per year.

    Parameters
    ----------
    year_agg : function series -> scalar
        Aggregator function to one value per year
    tmin, tmax : Optional[pd.Timestamp]
        Time indices to use for the simulation of the time series model.
    key : None, optional
        timeseries key ('observations' or 'simulated')
    fill_method : str or None
        fill method for interpolation to 14th and 28th of the month
        see: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.ffill.html
             http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.bfill.html
             http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.interpolate.html
        Use None to omit filling and drop NaNs
    limit : int or None
        Maximum number of timesteps to fill using fill method, use None to fill all
    output : str
        output type 'yearly' for series of yearly values, 'mean' for
        mean of yearly values

    Returns
    -------
    pd.Series or scalar
        Series of yearly values or mean of yearly values

    Raises
    ------
    ValueError
        When output argument is unknown
    """
    series = self.bykey(key=key, tmin=tmin, tmax=tmax)
    series = series.resample('d').mean()
    if fill_method is None:
        series = series.dropna()
    elif fill_method == 'ffill':
        series = series.ffill(limit=limit)
    elif fill_method == 'bfill':
        series = series.bfill(limit=limit)
    else:
        series = series.interpolate(method=fill_method, limit=limit)

    the14or28 = lambda x: (x.day == 14) or (x.day == 28)
    is14or28 = series.index.map(the14or28)
    if not np.any(is14or28):
        return np.nan
    series = series.loc[is14or28]
    yearly = series.resample('a').apply(year_agg)
    if output == 'yearly':
        return yearly
    elif output == 'mean':
        return yearly.mean()
    else:
        raise ValueError('{output:} is not a valid output option'.format(
            output=output))

def ghg(self, tmin=None, tmax=None, key='simulated',
        fill_method='linear', limit=15, output='mean'):
    """Classic method:
    Resampling the series to every 14th and 28th of the month.
    Taking the mean of the mean of three highest values per year.

    This function does not care about series length!

    Parameters
    ----------
    tmin, tmax : Optional[pd.Timestamp]
        Time indices to use for the simulation of the time series model.
    key : None, optional
        timeseries key ('observations' or 'simulated')
    fill_method : str
        fill method for interpolation to 14th and 28th of the month
        see: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.ffill.html
             http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.bfill.html
             http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.interpolate.html
        Use None to omit filling and drop NaNs
    limit : int or None
        Maximum number of timesteps to fill using fill method, use None to fill all
    output : str
        output type 'yearly' for series of yearly values, 'mean' for
        mean of yearly values

    Returns
    -------
    pd.Series or scalar
        Series of yearly values or mean of yearly values
    """
    mean_high = lambda s: s.nlargest(3).mean()
    return self.gxg(mean_high, tmin=tmin, tmax=tmax, key=key,
                    fill_method=fill_method, limit=limit, output=output)

def glg(self, tmin=None, tmax=None, key='simulated',
        fill_method='linear', limit=15, output='mean'):
    """Classic method:
    Resampling the series to every 14th and 28th of the month.
    Taking the mean of the mean of three lowest values per year.

    This function does not care about series length!

    Parameters
    ----------
    tmin, tmax : Optional[pd.Timestamp]
        Time indices to use for the simulation of the time series model.
    key : None, optional
        timeseries key ('observations' or 'simulated')
    fill_method : str
        fill method for interpolation to 14th and 28th of the month
        see: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.ffill.html
             http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.bfill.html
             http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.interpolate.html
        Use None to omit filling and drop NaNs
    limit : int or None
        Maximum number of timesteps to fill using fill method, use None to fill all
    output : str
        output type 'yearly' for series of yearly values, 'mean' for
        mean of yearly values

    Returns
    -------
    pd.Series or scalar
        Series of yearly values or mean of yearly values
    """
    mean_low = lambda s: s.nsmallest(3).mean()
    return self.gxg(mean_low, tmin=tmin, tmax=tmax, key=key,
                    fill_method=fill_method, limit=limit, output=output)

def __mean_spring__(self, series):
    """Determine mean of timeseries values in spring.

    Year aggregator function for gvg method.

    Parameters
    ----------
    series : pd.Series
        series with datetime index

    Returns
    -------
    float
        Mean of series, or NaN if no values in spring
    """
    inspring = self.__inspring__(series)
    if np.any(inspring):
        return series.loc[inspring].mean()
    else:
        return np.nan

def gvg(self, tmin=None, tmax=None, key='simulated',
        fill_method='linear', limit=15, output='mean'):
    """Classic method:
    Resampling the series to every 14th and 28th of the month.
    Taking the mean of the values on March 14, March 28 and April 14.

    This function does not care about series length!

    Parameters
    ----------
    tmin, tmax : Optional[pd.Timestamp]
        Time indices to use for the simulation of the time series model.
    key : None, optional
        timeseries key ('observations' or 'simulated')
    fill_method : str
        fill method for interpolation to 14th and 28th of the month
        see: http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.ffill.html
             http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.bfill.html
             http://pandas.pydata.org/pandas-docs/stable/generated/pandas.Series.interpolate.html
        Use None to omit filling and drop NaNs
    limit : int or None
        Maximum number of timesteps to fill using fill method, use None to fill all
    output : str
        output type 'yearly' for series of yearly values, 'mean' for
        mean of yearly values

    Returns
    -------
    pd.Series or scalar
        Series of yearly values or mean of yearly values
    """
    return self.gxg(self.__mean_spring__, tmin=tmin, tmax=tmax, key=key,
                    fill_method=fill_method, limit=limit, output=output)
