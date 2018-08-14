# Consumer

## Purpose

Consumer is an agent that will be installed on each worker machine, somewhat similar to Jenkins agents or Kubernetes
Kubelet.

It communicates with the producer API server, accepts jobs from it via an HTTP api and starts NHMMER processes
in background.

I'm currently pondering over some other design decisions: so far I think that consumer should be sending heartbeat
signals to the central API server at regular intervals, indicating that it's alive. Also, upon completion of the task,
it should be submitting the results to the API server via push (this is better than making API server). We might also
store incoming jobs in a queue for later processing.

## Architecture

Consumer is written in aiohttp, which is a new asynchronous HTTP framework for python3 only, based on the new asyncio
API (python3.5.3+).

We want consumer to accept jobs and run NHMMER in background, while also sending heartbeat signals to the producer
API server, pushing back job results and queuing new incoming jobs. Hence, synchronous Django or Flask servers would've
been unable to handle this without some kind of message queues/workers solution like Celery/RabbitMQ/Redis Queues.

Still, I'm mostly following django directory structure and using same abstractions (declarative urls, views, models,
templates, middlewares...).

## Installation

I suggest that you run consumer as a docker container. Dockerfile contains NHMMER installation code, while python
dependencies are listed in requirements.txt and can be installed with: `pip3 install -r requirements.txt`.

## Code samples:

 - http://edmundmartin.com/aiohttp-background-tasks/ - this is a demo on how to run background tasks with aiohttp
 - https://github.com/aio-libs/aiohttp-demos/tree/master/demos - several sample aiohttp projects, layed out like django