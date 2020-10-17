from src.router import connect
from click.testing import CliRunner

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
    assert """Welcome to [32mWeyland Yutani Refreshments[0m, please select a purchase
Gear
  Item #  Name       Price (eb/unit)    Weight (kg)
--------  -------  -----------------  -------------
       1  Pepsi                   50            0.5
       2  Cheetos                 50            0.3
Weapons
  Item #  Name      Price (eb/unit)  Type      Accuracy  Concealability    Availability    Damage/Ammo      #Shots    Rate of Fire  Reliability      Range
--------  ------  -----------------  ------  ----------  ----------------  --------------  -------------  --------  --------------  -------------  -------
       3  C-6                   100  HVY              0  P                 P               8D10 per kg           1               1  VR                  -1
Or q to quit
: q
""" == result.output