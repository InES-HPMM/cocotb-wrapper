.. currentmodule:: cocotb_wrapper

.. _testbench:

*********
Testbench
*********

The testbench helper functions and classes provide usability features when
writing testbenches. If you want to learn how to test one of your component make
sure to read the :ref:`user` guide.

Creating a testbench
====================

The :class:`~cocotb_wrapper.Testbench` class provides a convenient
wrapper around the `cocotb API <https://docs.cocotb.org/en/stable/
writing_testbenches.html#passing-and-failing-tests>`_ to define
tests. Inside a test we use standard cocotb. However, tests are
not registered using the :class:`cocotb.test` decorator, but rather
by creating a :class:`~cocotb_wrapper.Testbench` instance and use
the :meth:`~cocotb_wrapper.Testbench.register_test` decorator method. This
provides several advantages over the traditional approach.

Beside the :meth:`~cocotb_wrapper.Testbench.register_test`
decorator method, the :class:`~cocotb_wrapper.Testbench` class
also provides the :meth:`~cocotb_wrapper.Testbench.register_setup`
and :meth:`~cocotb_wrapper.Testbench.register_teardown` decorator
methods, to register setup and teardown functions. The setup and
teardown functions get executed before and after each test. Additionally,
the :class:`~cocotb_wrapper.Testbench` automatically sets the integer signal
``test_id`` inside the DUT to an incrementing number. So each test has its own
ID and can be identified when looking at the wave file.

Finally, the :class:`~cocotb_wrapper.Testbench` class
provides the :meth:`~cocotb_wrapper.Testbench.start_clock`
and :meth:`~cocotb_wrapper.Testbench.reset` methods to start the clock and reset
the component. Those methods are usually called within a setup and teardown
function.

.. autosummary::
   :toctree: generated/

   testbench.Testbench
   testbench._Test
