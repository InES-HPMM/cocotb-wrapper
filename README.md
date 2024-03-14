# cocotb-wrapper

`cocotb-wrapper` provides a wrapper class, called `Testbench`, that facilitates
the use of `cocotb.test()`. Additionally, this module also contains a wrapper
around `cocotbext-axi`.

## Documentation

A little more detailed documentation is available [here](https://ines-hpmm.github.io/cocotb-wrapper/).

## Writing tests using `Testbench`

First, import the wrapper module with

```python
import cocotb_wrapper as ctw
```

Writing tests with the `Testbench` class is a lot less verbose. First, we create
a new `Testbench` object by providing some basic information.

```python

TB = ctw.Testbench("adder", clk="clk_i", rst="rst_ni", reset_active_level=0)
```

We provided the main clock signal and the main reset signal and its properties
(i.e. active high or active low).

Usually, our component requires some setup and teardown procedure, that is
required before each test we want to perform. A register and teardown function
can be registered using the `register_setup` and `register_teardown` decorators.

```python
@TB.register_setup()
async def setup(dut):
  TB.start_clk(dut, period=2, units="ns")
  # Do some initialization
  await TB.reset(dut, time=2, unit="ns")

@TB.register_teardown()
async def teardown(dut):
  # Do some teardown
  await TB.reset(dut, time=2, unit="ns")
```

The `setup` and `teardown` function will be called before and after every
registered test. Additionally, the `Testbench` class provides the `start_clk`
and `reset` method to start the clock and reset the DUT. Additionaly, clocks
and resets have to be driven manually. If no setup or teardown functions are
registered, the default ones are executed, which are the ones showed above.

Finally, we can register tests with

```python
@TB.register_test()
async def test_add(dut):
  # Do some stuff
  assert # Some condition
```

Now when we call the registered tests, every test will execute:

1. the registered setup function
2. the registered test function
3. the registered teardown function

until all the registered tests have been executed. An additional `test_id`
signal (preferrably with the type integer) within the DUT is set to the test ID
number. This allows to distinguish tests more easily within the generated wave
files, since all the tests are sequentially in one file.
