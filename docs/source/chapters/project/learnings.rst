Learnings
=========

*Written by Luca Deck and Manuel Sauter*

While working on this project, we faced several challenges and struggled with a lot of unforeseen issues. Additionally, in hindsight we encountered a multitude of things we would approach differently in future endeavors regarding data science in general or specifically for computer vision. Apart from our handed-in repository, we see these findings and learnings as the major takeaway of this course and want to summarize them shortly.

Training Data Collection
--------------------------

With little to no experience in computer vision projects, especially in the early stages of training data collection we had to make some decisions that were fundamental for the further development of the project. Some of these turned out to be suboptimal in hindsight. With more experience, some deeper preliminary considerations would have been helpful. However, we of course acknowledge that some of these issues might never be resolved perfectly due to the inherently iterative nature of data science projects.

+ **Define use case narrowly precisely** The more specific the problem at hand the lower the complexity and effort. By narrowing down the use case upfront e.g. only for a specific kind of package (brown with white label) and only one or two damages, we could have concentrated our efforts more effectively and thus possibly reach a higher precision.
+ **Take the productive setting into consideration** By strictly defining external factors for the deployment stage we could have created a more realistic or authentic training dataset. Determining image quality, angle, background etc. promises a more effective data collection process as well as higher precision for the productive setting. In our case it would have been advisable to collect the dataset on-site instead of our rooms. 
+ **Label once to save effort** Knowing the exact demand of training data helps to perform this step in one go providing more efficiency. Instead, our training data collection was more of an iterative process based on noticed shortcomings. We underestimated the huge amount of data for our model to perform sufficiently.
+ **Hinge the decision on number and type of classes on the amount of training data** The effort for training data  collection increases in the number of label classes. Agreeing on less label classes thus can reduce the effort significantly.
+ **Include "negative" examples in the training set** Depending on the architecture (especially YOLO), adding negative instances increases model performance significantly. These should show the surroundings without the focal object, for example in our case our room, the floor and the background without the package. Apparently, this helps the model to adapt to the environment and to be more confident in the detections.
+ **Set up strict guidelines for labeling and communicate them appropriately** A consistent dataset requires all people working at the labeling tasks to agree on guidelines (regarding label type, narrowness, annotation format etc.). These have to be communicated explicitly in a manner that no misunderstandings can happen whatsoever. Even minor misunderstandings can be very costly if not noticed in time.
+ **Choose the model framework upfront to know the data requirements** Knowing the model framework in advance helps to define the data requirements. For example, this implies certain annotation formats or that polygons are not compatible with the model anyway. Similarly, early downscaling saves a lot of computing effort and time if you know that the model can only handle a maximum of pixels.
 

Choice of Models and Training
-----------------------------

*Written by Johannes Jestram*

+ **Do not only consider performance benchmarks** When having different models at hand, the choice for a model should also depend on softer factors such as hardware support, effort to train, effort to deploy, and in our case FPS in the video inference. During the project, we found that Darknet and Tensorflow differ strongly in those points.
+ **Build the end-to-end pipeline early** When trying out a model, before focusing for many hours on preparing data and training, make sure that you can already deploy it for inference. Further, make sure to get to the point where you successfully start the training once, even with dummy data, on the target system where you want to train. We found that out the hard way when trying to train YOLO on Azure, which required a lot of effort in the last weeks of the project. If we had considered this earlier, we could have saved time and nerves.

Co-Working & Communication
--------------------------
*Written by Luca Deck and Johannes Jestram*

While we were a completely motivated team and enjoyed working together, we stumbled across some hurdles in our workflow.
 
+ **Read instructions, guidelines and Readmes thoroughly** Although we documented most of our internal work and processes carefully and generally maintained a healthy communication, one is always prone to overlooking essential notes. This refers, for example, to the labeling guidelines. This also makes the entire work reproducible and comprehensible for external people.
+ **Git** To avoid tedious merge conflicts, it is essential to always pull all recent changes before working on anything and to always push afterwards. Git is a powerful tool for workflow coordination, collaboration and versioning but requires a certain level of experience and knowhow.
+ **Check each other's code** In order to prevent bad coding habits, missing tests for important code, and sloppy docstrings, check each other's code. Either via automatic pipelines, or by hand. We did this and thereby were able to greatly improve the overall code quality.
