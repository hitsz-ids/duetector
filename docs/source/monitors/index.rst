Monitor
=========================================

Monitor combines :doc:`Tracer </tracers/index>`, :doc:`Collector </collectors/index>`
and :doc:`Filter </filters/index>` by :doc:`Manager </managers/index>` to provide an
entry point for the polling, filtering and collecting of the data.

:doc:`Poller </tools/poller>` is used to poll the data periodically.


.. autoclass:: duetector.monitors.base.Monitor
   :members:
   :undoc-members:
   :show-inheritance:


Avaliable Monitor
-------------------------------------------

.. toctree::
   :maxdepth: 2

   Bcc Monitor <bcc>
   Shell Monitor <sh>
