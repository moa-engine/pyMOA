from concurrent.futures import ThreadPoolExecutor
from pyMOA.core.engine_loader import EngineLoader
from pyMOA.core.plugin_loader import PluginLoader
from typing import Optional, Annotated

def search(
    q: Annotated[Optional[str], "Search query"] = None,
    engine: Annotated[Optional[list[str]], "List of search engines"] = None,
    plugin: Annotated[Optional[list[str]], "List of plugins"] = None,
    time_range: Annotated[str, "Time range filter"] = None,
    lang: Annotated[str, "Search language"] = "",
    size: Annotated[Optional[int], "Number of results per engine"] = None,
    page: Annotated[int, "Page number"] = 1,
    safesearch: Annotated[int, "Safe search level"] = 0,
    country: Annotated[str, "Country to search"] = "",
    category: Annotated[str, "Search category"] = "general",
    ):
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

    # Loading engines and plugin anf determining healthy
    ploader = PluginLoader()
    loader = EngineLoader()
    engine_status = loader.list_engines()
    plugin_status = ploader.list_plugins()
    selected_engines = engine if engine is not None else engine_status["active"]
    selected_pre_plugins = []
    selected_post_plugins = []

    if plugin:
        for plugin_name in plugin:
            plugin_instance = ploader.get_plugin(plugin_name)
            if not plugin_instance:
                return "Plugin '%s' not found or failed to load.", plugin_name

            plugin_type = plugin_instance.get_type().lower()
            if plugin_type == "pre":
                selected_pre_plugins.append(plugin_instance)
            elif plugin_type == "post":
                selected_post_plugins.append(plugin_instance)
            else:
                return f"Plugin '{plugin_name}' has unknown type '{plugin_type}'"

    else:
        selected_pre_plugins = ploader.pre_plugins
        selected_post_plugins = ploader.post_plugins






    results = {}
    pre_plugin_outputs = {}
    # Adding active or inactive motors to the results
    results["active_engines"] = engine_status["active"]
    results["failed_engines"] = engine_status["failed"]
    results["active_plugins"] = plugin_status["active"]
    results["failed_plugins"] = plugin_status["failed"]

    with ThreadPoolExecutor() as executor:
        futures = {}
        for engine_name in selected_engines:
            engine = loader.get_engine(engine_name)
            if not engine:
                results[engine_name] = {"error": f"Engine {engine_name} not found!"}
                continue
            # Creating search parameters
            search_params = {
                "query": q,
                "page": page,
                "safesearch": safesearch,
                "time_range": time_range,
                "locale": lang,
                "country": country,
                "num_results": size, # For engines that can return a certain number of results by default
#                "category": category
            }

            futures[executor.submit(engine.search, **search_params)] = ("engine", engine_name)



        for plugin in selected_pre_plugins:
            futures[executor.submit(plugin.run, q)] = ("pre_plugin", plugin.__class__.__name__)

        for future in futures:
            ftype, name = futures[future]
            try:
                output = future.result()
                if ftype == "engine":
                    if size and isinstance(output, dict) and "results" in output and isinstance(output["results"], list):
                        output["results"] = output["results"][:size]
                    results[name] = output
                elif ftype == "pre_plugin":
                    pre_plugin_outputs[name] = output

            except Exception as e:
                if ftype == "engine":
                    results[name] = {"error": str(e)}
                elif ftype == "pre_plugin":
                    pre_plugin_outputs[name] = {"error": str(e)}

    return {
        "results": results,
        "pre_plugins": pre_plugin_outputs
    }
