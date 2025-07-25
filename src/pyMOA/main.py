from concurrent.futures import ThreadPoolExecutor
from pyMOA.core.engine_loader import EngineLoader
from pyMOA.core.plugin_loader import PluginLoader
from typing import Optional, Annotated , Union

def get_proxy_config(proxy: str | dict =None):

    """
    Global proxy settings for engines that use the "requests" library.
    Supported proxy types: Follows the "requests" supported ones. Current inputs are passed directly to requests.get proxies input. For more information, see https://requests.readthedocs.io.
    """
    if proxy is None:
        return None


    if isinstance(proxy, str):
        if proxy[:5] == "http:":
            return proxy
        elif proxy[:5] == "https":
            proxy = proxy.replace("https://", "http://", 1)
            return proxy
        else:
            raise TypeError("Proxy string must start with 'http://' or 'https://'.")

    elif isinstance(proxy, dict):
        if not set(proxy.keys()) & {"http", "https"}:
            raise TypeError("The input dictionary must contain at least one of the two proxy types http or https.")

        return proxy


def search(
    q: Annotated[Optional[str], "Search query"] = None,
    engines: Annotated[Optional[list[str]], "List of search engines"] = None,
    enabled_plugins: Annotated[Optional[list[str]], "List of plugins"] = None,
    time_range: Annotated[str, "Time range filter"] = None,
    language: Annotated[str, "Search language"] = "",
    limit: Annotated[Optional[int], "Number of results per engine"] = None,
    pageno: Annotated[int, "Page number"] = 1,
    safesearch: Annotated[int, "Safe search level"] = 0,
    country: Annotated[str, "Country to search"] = "",
    categories: Annotated[str, "Search category"] = "general",
    proxy: Annotated[Union[str, dict[str, str]], "HTTP or HTTPS proxy string or dict"] = None,
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

    categories = category.lower() if categories else "general"
    if categories not in engine_status:
        categories = "general"

    if engines:
        if categories in engine_status:
            invalid_engines = [e for e in engines if e not in engine_status[categories]]
            if invalid_engines:
                raise ValueError(f"Engine(s) {invalid_engines} not found in category '{categories}'")

        selected_engines = engines
    else:
        selected_engines = engine_status[categories]


    selected_pre_plugins = []
    selected_post_plugins = []

    if enabled_plugins:
        for plugin_name in enabled_plugins:
            plugin_instance = ploader.get_plugin(plugin_name)
            if not plugin_instance:
                raise ValueError(f"Plugin '{plugin_name}' not found or failed to load.")

            plugin_type = plugin_instance.get_type().lower()
            if plugin_type == "pre":
                selected_pre_plugins.append(plugin_instance)
            elif plugin_type == "post":
                selected_post_plugins.append(plugin_instance)
            else:
                raise ValueError(f"Plugin '{plugin_name}' has unknown type '{plugin_type}'")


    else:
        selected_pre_plugins = ploader.pre_plugins
        selected_post_plugins = ploader.post_plugins


    proxy = get_proxy_config(proxy)

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
                "page": pageno,
                "safesearch": safesearch,
                "time_range": time_range,
                "locale": language,
                "num_results": limit, # For engines that can return a certain number of results by default
                "country": country,
                "proxy": proxy
            }

            futures[executor.submit(engine.search, **search_params)] = ("engine", engine_name)



        for plugin in selected_pre_plugins:
            futures[executor.submit(plugin.run, q)] = ("pre_plugin", plugin.__class__.__name__)

        for future in futures:
            ftype, name = futures[future]
            try:
                output = future.result()
                if ftype == "engine":
                    if limit and isinstance(output, dict) and "results" in output and isinstance(output["results"], list):
                        output["results"] = output["results"][:limit]
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
