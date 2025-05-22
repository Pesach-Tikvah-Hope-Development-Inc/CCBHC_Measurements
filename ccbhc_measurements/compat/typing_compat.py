import sys
from typing import Any

if sys.version_info >= (3, 12):
    from typing import override
else:
    def override(method: Any) -> Any:
        return method