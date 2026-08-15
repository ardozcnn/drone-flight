import logging
from typing import Any

import certifi
import requests
import urllib3
from requests.exceptions import SSLError

logger = logging.getLogger(__name__)

_ssl_configured = False


def _configure_ssl() -> None:
    global _ssl_configured
    if _ssl_configured:
        return
    try:
        import truststore
        truststore.inject_into_ssl()
        logger.info("SSL: Windows/macOS sertifika deposu (truststore) etkin.")
    except ImportError:
        logger.debug("truststore yüklü değil, certifi kullanılacak.")
    _ssl_configured = True


def http_get(url: str, **kwargs: Any) -> requests.Response:
    _configure_ssl()
    kwargs.setdefault("timeout", 15)

    verify_options: list[bool | str] = [certifi.where(), True, False]
    last_error: SSLError | None = None

    for verify in verify_options:
        try:
            response = requests.get(url, verify=verify, **kwargs)
            if verify is False:
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                logger.warning(
                    "SSL doğrulaması devre dışı bırakıldı (%s). "
                    "Kalıcı çözüm: pip install truststore",
                    url.split("/")[2],
                )
            return response
        except SSLError as exc:
            last_error = exc
            continue

    assert last_error is not None
    raise last_error
