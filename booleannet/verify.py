"""Whether optional packages imported by the commands are available."""


def _ready(name: str) -> bool:
    try:
        __import__(name)
        return True
    except ImportError:
        return False


# Optional package -> import succeeded.
READY = {
    "pyboolnet": _ready("pyboolnet"),
    "pystablemotifs": _ready("pystablemotifs"),
}

PYBOOLNET_READY = READY["pyboolnet"]
PYSTABLEMOTIFS_READY = READY["pystablemotifs"]
