pdfreader.viewer submodule
==========================

   .. autoclass:: pdfreader.viewer.SimplePDFViewer

      .. autoproperty:: current_page
      .. autoattribute:: current_page_number
        :annotation:
      .. autoattribute:: gss
        :annotation:
      .. autoattribute:: canvas
        :annotation:
      .. autoattribute:: resources
        :annotation:

      .. automethod:: render
      .. automethod:: navigate
      .. automethod:: next
      .. automethod:: prev
      .. autoproperty:: annotations
      .. automethod:: __iter__
      .. automethod:: iter_pages


  .. autoclass:: pdfreader.viewer.SimpleCanvas

        .. autoattribute:: text_content
          :annotation:
        .. autoattribute:: strings
          :annotation:
        .. autoattribute:: images
          :annotation:
        .. autoattribute:: inline_images
          :annotation:
        .. autoattribute:: forms
          :annotation:


  .. autoclass:: pdfreader.viewer.GraphicsState

        .. autoattribute:: CTM
          :annotation:
        .. autoattribute:: LW
          :annotation:
        .. autoattribute:: LC
          :annotation:
        .. autoattribute:: LJ
          :annotation:
        .. autoattribute:: ML
          :annotation:
        .. autoattribute:: D
          :annotation:
        .. autoattribute:: RI
          :annotation:
        .. autoattribute:: I
          :annotation:
        .. autoattribute:: Font
          :annotation:  [font_name, font_size]
        .. autoattribute:: Tc
          :annotation:
        .. autoattribute:: Tw
          :annotation:
        .. autoattribute:: Tz
          :annotation:
        .. autoattribute:: TL
          :annotation:
        .. autoattribute:: Tr
          :annotation:
        .. autoattribute:: Ts
          :annotation:

  .. autoclass:: pdfreader.viewer.GraphicsStateStack

      .. autoproperty:: state
      .. automethod:: save_state
      .. automethod:: restore_state

  .. autoclass:: pdfreader.viewer.Resources

  .. autoclass:: pdfreader.viewer.PageDoesNotExist