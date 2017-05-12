import os
import shutil

import pytest

from bobslide import app


test_app = pytest.fixture(lambda: app.test_client())


@pytest.fixture(autouse=True)
def setup(request, tmpdir):
    for folder in ('presentations', 'themes'):
        tmp_path = tmpdir.join(folder).strpath
        shutil.copytree(
            os.path.join(app.config.root_path, 'tests', folder), tmp_path)
        app.config['%s_PATHS' % folder.upper()] = [tmp_path]
