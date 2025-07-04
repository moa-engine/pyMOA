from concurrent.futures import ThreadPoolExecutor
from pyMOA.core.engine_loader import EngineLoader


def search(query, engines=None, page=1, safesearch=0, time_range=None):
    """
    Multi-engine search interface as a Python function.

    Args:
        query (str): Search query.
        engines (list[str] or None): List of engine names, or None to use all active.
        page (int): Page number.
        safesearch (int): 0 (off), 1 (moderate), 2 (strict).
        time_range (str or None): One of ["day", "week", "month", "year"].

    Returns:
        str: List search results.
    """

    # Validate safesearch
    if safesearch not in [0, 1, 2]:
        raise ValueError("Invalid safesearch level. Choose from 0 (off), 1 (moderate), 2 (strict).")

    # Validate time_range
    allowed_ranges = ["day", "week", "month", "year"]
    if time_range is not None and time_range not in allowed_ranges:
        raise ValueError(f"Invalid time_range. Choose from {allowed_ranges}")

    # Loading engines and determining healthy engines
    loader = EngineLoader()
    engine_status = loader.list_engines()
    selected_engines = engines if engines is not None else engine_status["active"]

    results = {}
    # Adding active or inactive motors to the results
    results["active_engines"] = engine_status["active"]
    results["failed_engines"] = engine_status["failed"]
    with ThreadPoolExecutor() as executor:
        futures = {}
        for engine_name in selected_engines:
            engine = loader.get_engine(engine_name)
            if not engine:
                results[engine_name] = {"error": f"Engine {engine_name} not found!"}
                continue
            # Creating search parameters
            search_params = {
                "query": query,
                "page": page,
                "safesearch": safesearch,
                "time_range": time_range,
    #               "num_results": num_results, # Unfinished
            }

            futures[executor.submit(engine.search, **search_params)] = engine_name

        for future in futures:
            engine_name = futures[future]
            try:
                results[engine_name] = future.result()
            except Exception as e:
                results[engine_name] = {"error": str(e)}
                results[engine_name] = {"error": str(e)}

    return results
