from main import process

def test_source_single():

    assert process('example_1', True) == 437
    assert process('example_2', True) == 8362689594
