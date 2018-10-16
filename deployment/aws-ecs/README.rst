Deploying Jicket on AWS ECS
==================================

AWS `ECS <https://docs.aws.amazon.com/ecs>`_ is a way to host docker containers without the need to manage individual servers. This folder contains an example on how you could deploy Jicket in ECS using Fargate.

It uses `cloudformation <>`_ to create the necessary AWS resources. The cloudformation description is in turn generated with `troposphere <https://github.com/cloudtools/troposphere>`_, a python library for generating cloudformation descriptions.


How-To
--------------
First you need to create a VPC with a public subnet and an internet gateway. Make sure to route ``0.0.0.0/0`` to the internet gateway, otherwise the internet can't be reached.

Change the subnet designation to reflect your created subnet in the ``jicketsubnet`` variable.

Also set all the jicket configuration variables according to the documentation.