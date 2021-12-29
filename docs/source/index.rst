.. AISS-CV documentation master file, created by
   sphinx-quickstart on Wed May 12 15:06:46 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Detection of Damaged Packages
===================================
Welcome to our project page! Our work took place during Summer Term 2021 at KIT in the course "Artificial Intelligence in Service Systems - Applications in Computer Vision" . This Document consists of three sections. First, we explain the use case and further details of the project itself. The second part consits of a detailed explanation and discussion of the system architecture. Lastly, we provide a documentation of our code base.

Summary
-------
We built a system that utilizes a NVIDIA Jetson to visually detect packages and - if existent - damaged areas on the detected packages.

.. warning:: This is not  production ready software yet

Project Description
--------------------

.. toctree::   
   :caption: Project
   :maxdepth: 2
   :numbered:

   chapters/project/use-case
   chapters/project/collaboration
   chapters/project/timeline
   chapters/project/training_data_collection
   chapters/project/augmentation
   chapters/project/model-comparison-and-choice   
   chapters/project/outlook
   chapters/project/learnings

System Description
-------------------

.. toctree::   
   :caption: System
   :maxdepth: 2
   :numbered:
   
   chapters/architecture/architecture-overview
   chapters/architecture/object-detection
   chapters/architecture/code-overview
   chapters/architecture/subsequent-damage-handling

Code Documentation
------------------

.. toctree::
   :caption: Code
   :maxdepth: 2 
     
   code-docs/aisscv.inference
   code-docs/aisscv.augmentation
   code-docs/aisscv.utils
   code-docs/tests
   



.. The stuff below creates a summary, uncomment if you want to try it out
.. .. rubric:: Modules
.. .. autosummary::
..    :toctree: generated
..    
..    aisscv


 Indices and tables
 ==================

 * :ref:`genindex`
 * :ref:`modindex`
 * :ref:`search`
