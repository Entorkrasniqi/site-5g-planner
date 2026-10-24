import pytest

from site5g.ifc_loader import load_ifc
from site5g.sample_ifc import build_sample


@pytest.fixture(scope="session")
def sample_ifc(tmp_path_factory):
    path = tmp_path_factory.mktemp("ifc") / "sample_office.ifc"
    build_sample(str(path))
    return str(path)


@pytest.fixture(scope="session")
def storey(sample_ifc):
    return load_ifc(sample_ifc)[0]
