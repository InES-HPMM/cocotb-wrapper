.. currentmodule:: cocotb_wrapper

.. _testbench:

************************************
Testing entities with AXI interfaces
************************************

The :mod:`~cocotb_wrapper.axi` provides classes to instantiate AXI interfaces.
These classes wrap around `cocotbext-axi <https://github.com/alexforencich/
cocotbext-axi>`_ and provide a standardized interface across all AXI interface
types.

AXI
===

The fully fledged AXI interface.

.. autosummary::
   :toctree: generated/

   axi.AxiMaster
   axi.AxiRam
   axi.RandomAxiPayloadGenerator

AXI-Lite
========

The lighter AXI-Lite interface.

.. autosummary::
   :toctree: generated/

   axi.AxiLiteMaster
   axi.AxiLiteRam
   axi.RandomAxiLitePayloadGenerator

AXI-Stream
==========

The AXI-Stream interface for streaming applications.

.. autosummary::
   :toctree: generated/

   axi.AxiStreamSource
   axi.AxiStreamSink
   axi.RandomAxiStreamPayloadGenerator

AXI Flags
=========

AXI related flags and enumeration classes.

.. autosummary::
   :toctree: generated/

   axi.AxiBurstType
   axi.AxiBurstSize
   axi.AxiLockType
   axi.AxiCacheBit
   axi.AxiProt
   axi.AxiResp
