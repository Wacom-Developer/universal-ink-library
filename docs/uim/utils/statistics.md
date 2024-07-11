Module uim.utils.statistics
===========================

Classes
-------

`StatisticsAnalyzer()`
:   Statistics analyzer
    ===================
    Analyze the model and compute statistics.

    ### Ancestors (in MRO)

    * uim.utils.analyser.ModelAnalyzer
    * abc.ABC

    ### Static methods

    `analyze(model: uim.model.ink.InkModel, ignore_predicates: Optional[List[str]] = None, ignore_properties: Optional[List[str]] = None) ‑> Dict[str, Any]`
    :   Analyze the model and compute statistics.
        Parameters
        ----------
        model: InkModel
            Ink model to analyze.
        ignore_predicates: Optional[List[str]]
            List of predicates to ignore.
        ignore_properties: Optional[List[str]]
            List of properties to ignore.
        
        Returns
        -------
        stats: Dict[str, Any]
            The computed statistics.
        
        Raises
        ------
        StatisticsError
            If an error occurs while analyzing the model.

    `merge_stats(*stats)`
    :   Merge stats.
        
        Parameters
        ----------
        stats: Tuple[Dict[str, Any]]
            Stats to merge.

    `summarize(stats: Dict[str, Any], verbose: bool = False)`
    :   Summarize stats.
        
        Parameters
        ----------
        stats: Dict[str, Any]
            Stats to summarize.
        verbose: bool
            Verbose mode.