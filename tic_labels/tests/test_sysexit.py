
# http://doc.pytest.org/en/latest/getting-started.html

# content of test_sysexit.py
import pytest



# content of test_sysexit.py
def f():
    raise SystemExit(1)

def test_mytest():
    with pytest.raises(SystemExit):
        f()