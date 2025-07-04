

def get_proxy_config(enabled=True):

    """
    Global proxy settings for engines that use the "requests" library.
    Supported proxy types: Follows the "requests" supported ones. Current inputs are passed directly to requests.get proxies input. For more information, see https://requests.readthedocs.io.

    Set enabled to "True" or "False" to enable or disable proxy usage.
    (You can also enable this variable by default in each engine. But the settings in this section take precedence.)
    """

    if enabled:
        return {
            'http': 'http://192.168.1.102:12334',
            'https': 'http://192.168.1.102:12334',
            }
    else:
        return none
