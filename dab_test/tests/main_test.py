from unittest.mock import MagicMock, patch

from dab_test import main


def test_find_all_taxis():
    mock_df = MagicMock()
    mock_reader = MagicMock()
    mock_spark = MagicMock()

    mock_spark.read = mock_reader
    mock_reader.table.return_value = mock_df

    with patch.object(main, "spark", mock_spark):
        taxis = main.find_all_taxis()

    mock_reader.table.assert_called_once_with("samples.nyctaxi.trips")
    assert taxis == mock_df