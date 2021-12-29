Azure
=====
*Written by Joel Oswald*

|img0|  [#]_

.. |img0| image:: ../../img/azure_logo.jpeg
    :width: 10%



Microsoft Azure is a public cloud provider and together with AWS, GCP, Alibaba and IBM among the largest of its kind. [#]_
It offers a variety of services for IaaS, PaaS, SaaS, and MLaaS.
We used multiple Azure services for different parts of our project. An overview of the services and how they are connected can be seen in the :ref:`overview <arch_overview_reference>`.
Like most big players in the public cloud business, Azure provides free credit for students without the need to provide a credit card or other payment options. 
Being six students gave us enough credit to execute all required tasks (Kubernetes cluster, pipelines, docker instances, etc. ) on Azure.
In this Section we explain some services and how they are used that are not covered by the :ref:`CI/CD Pipelines <ci_reference>`. 
The most essential part is the possibility to train in the cloud. 
To be as platform independent as possible we did not use cloud-specific services like Azure Machine Learning, which would make switching to a different cloud provider harder.
Instead we just used IaaS and PaaS resources, such as container instances, that could be easily transferred to another provider.

Container Registry
------------------

We have our own container registry in place, which hosts all docker images that are used for the training of our networks. 
This allows autonomous updating of the images when a new version of the corresponding dockerfile is pushed to our repository.

File Share
----------

With the amount of data and models we trained, it was necessary to have a central place where all training data are stored.
In addition, we wanted a central place for all trained models, so that they could be easily compared with a tool like Tensorboard. Using *Azure File Shares* solved this for us in a cost-efficient way. 
Using access tokens there was no need to share private login credentials. Furthermore the file share can be mounted as a volume to Docker container running in a Container instance, so that the models can be saved right there without any manual copy and move commands.
Lastly, the file share is easily accessible by GUI and hence allows drag-and-drop uploading, either via its web interface, or via the Azure Storage Explorer. 

.. _sec:azure:

Container Instances
-------------------

Container instances are the central part for our cloud training pipeline. 
A container instance is a running container with a certain amount of resources that it can access. 
While it is possible to create such a resource via the Azure GUI, we aimed for scalability. So we defined a template via a  `yaml-file <https://git.scc.kit.edu/ukojp/aiss-cv/-/blob/master/azure_tf_train.yaml>`_ which allowed the repeatable and automatic deployment of container instances with our own images from the container registry.
Besides that, we specified our file share to be mounted as a volume and the amount of resources that are available. 
If needed, it now takes only seconds to adjust the necessary amount of memory or GPU power. Deployment can either be triggered locally via the Azure CLI or web-based using the cloud shell.
As the main process we are usually running a permanent service in the container, such as Tensorboard. The yaml-file also specifies exposed ports, so that the Tensorboard could always be accessed by the entire team via a web browser. 

We then connected to the container to start the chosen training, where all necessary configuration files reside in the file share, thus persisting the state over the lifetime of a single container. 
In the same way, all checkpoints during training are written to that file share so that it is possible to continue an aborting training from another person with a new container instance. 

This allowed training multiple models in parallel from all members of the team, even if they had little experience in setting up a training environment.

Kubernetes
-----------

Out of curiosity we also setup a Kubernetes cluster (*Azure Kubernetes Service*) and installed the GitLab runners to execute our GitLab specific pipelines, which worked well throughout the whole project.

.. rubric:: Image Sources

.. [#] https://swimburger.net/media/0zcpmk1b/azure.jpg
.. [#] https://www.statista.com/chart/18819/worldwide-market-share-of-leading-cloud-infrastructure-service-providers/
