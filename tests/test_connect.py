from src.router import connect
from click.testing import CliRunner

weyland_return = """Welcome to [32mWeyland Yutani Refreshments[0m, please select a purchase
Gear
  Item #  Name       Cost (eb)    Weight (kg)
--------  -------  -----------  -------------
       1  Pepsi             50            0.5
       2  Cheetos           20            0.3
Weapons
  Item #  Name                     Cost (eb)  Type      Accuracy  Concealability    Availability    Damage/Ammo           #Shots    Rate of Fire  Reliability    Range
--------  ---------------------  -----------  ------  ----------  ----------------  --------------  ------------------  --------  --------------  -------------  -------
       3  Malorian Sliver Gun            372  P               +0  J                 P               2d6x1d6/2*(Sliver)         7               2  UR             40m
       4  Federated Arms Impact           60  P               +1  J                 E               1d6(.22)                  10               2  VR             50m
Or q to quit
: q
"""

def test_connect_info():
    runner = CliRunner()
    result = runner.invoke(connect, ['Night City Tourism'], input='q\n')
    assert result.output == \
"""Night City offers a variety of exciting places to visit! To learn more, select one
1) The Sewers
2) The Docks
Or q to quit
: q
"""

def test_connect_info_submenu():
    runner = CliRunner()
    result = runner.invoke(connect, ['Night City Tourism'], input='1\ny\n')
    assert """The sewers are incredibly scenic
Exit? [y/N]: y
""" in result.output
    result = runner.invoke(connect, ['Night City Tourism'], input='2\ny\n')
    assert """The Docks are next to water
Exit? [y/N]: y
""" in result.output

def test_connect_shop():
    runner = CliRunner()
    result = runner.invoke(connect, ['Weyland Yutani Refreshments'], input='q\n')
    assert  weyland_return == result.output

def test_connect_shop_fuzzy_name():
    runner = CliRunner()
    result = runner.invoke(connect, ['weyland'], input='q\n')
    assert weyland_return == result.output