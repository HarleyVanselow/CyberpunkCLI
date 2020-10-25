from src.router import route, base_roll
from click.testing import CliRunner
import src


def mock_query_character(character, attr):
    pass


def test_facedown(mocker):
    mock_base_roll = mocker.patch("src.router.base_roll")
    runner = CliRunner()
    character = 'harley'
    runner.invoke(route, ['--character', character, 'roll', 'facedown'])
    mock_base_roll.assert_called_once_with(
        ['cool', 'rep'], 10, None, character)
