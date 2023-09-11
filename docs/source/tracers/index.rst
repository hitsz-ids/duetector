Tracer
=====================================

``Tracer`` will be capturing information in some way.
:doc:`Collector </collectors/index>` will convert ``Tracer``'s  ``data_t`` to :doc:`Tracking </collectors/models>`.

.. note::
   Some filed of ``data_t`` will be converted to other more readable filed,
   if you want to fit this feature, you should refer to :doc:`Tracking.normalize_field </collectors/models>`.


.. automodule:: duetector.tracers
   :members:
   :undoc-members:
   :inherited-members:


Avaliable Tracer
--------------------------------------

.. toctree::
   :maxdepth: 2

   CloneTracer <clone>
   OpenTracer <openat2>
   TcpconnectTracer <tcpconnect>
   UnameTracer <uname>
