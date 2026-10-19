'''
test/unit/test_convert.py
'''

from app.infrastructure.api.interface import StatementAdapter
import pandas as pd
import pytest




@pytest.fixture()
def create_dataframe():
    return pd.DataFrame({'a' : 1, 'b': 2, 'c':3, 'd':4}, index = [0])


def test_convert_happy_path_renames_and_filters_columns(create_dataframe):
    """Verify _convert renames target columns and drops unmapped vendor columns."""
    df = create_dataframe
    to_drop = 'd'
    to_convert = {'a' : 'x', 'b' : 'y', 'c' : 'z'}

    converted = StatementAdapter._convert(raw_data = df, col_mapping = to_convert)


    assert set(converted.columns) == {'x', 'y', 'z'}
    assert to_drop not in converted.columns



def test_convert_partial_data_when_mapped_column_is_missing(create_dataframe):
    """Verify behavior when raw DataFrame is missing a column specified in the mapping."""
    # Arrange: Input DataFrame missing one of the keys from col_mapping

    # Act & Assert: Observe behavior when _convert is invoked

    df = create_dataframe
    to_convert = {'a' : 'x', 'b' : 'y', 'fake' : 'z'}

    with pytest.raises(KeyError):
        converted = StatementAdapter._convert(raw_data = df, col_mapping = to_convert)







