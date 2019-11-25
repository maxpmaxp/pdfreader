pdfreader.viewer submodule
==========================

   .. autoclass:: pdfreader.viewer.SimplePDFViewer

      .. autoproperty:: current_page
      .. autoattribute:: current_page_number
      .. autoattribute:: gss
      .. autoattribute:: canvas
      .. autoattribute:: resources

      .. automethod:: render
      .. automethod:: navigate
      .. automethod:: next
      .. automethod:: prev

  .. autoclass:: pdfreader.viewer.SimpleCanvas

        .. autoattribute:: text_content
        .. autoattribute:: strings
        .. autoattribute:: images
        .. autoattribute:: inline_images
        .. autoattribute:: forms

  .. autoclass:: pdfreader.viewer.GraphicsState

        .. autoattribute:: CTM
        .. autoattribute:: LW
        .. autoattribute:: LC
        .. autoattribute:: LJ
        .. autoattribute:: ML
        .. autoattribute:: D
        .. autoattribute:: RI
        .. autoattribute:: I
        .. autoattribute:: Font
        .. autoattribute:: Tc
        .. autoattribute:: Tw
        .. autoattribute:: Tz
        .. autoattribute:: TL
        .. autoattribute:: Tr
        .. autoattribute:: Ts

  .. autoclass:: pdfreader.viewer.GraphicsStateStack

      .. autoproperty:: state
      .. automethod:: save_state
      .. automethod:: restore_state

  .. autoclass:: pdfreader.viewer.Resources

  .. autoclass:: pdfreader.viewer.PageDoesNotExist