Requirements
======

### Server side
* Apache
* Python 2.7
* DB2

Specific libraries used
[requirements.txt][]


# Installation
There are two ways to install this service:

One way to mount this service is to upload to a  [Cloud Foundry][] container for python, but since this version is set up for a specific client there are a couple of changes to be made.
1. The [manifest.yml][] must match the necessities for the new CF container that will be used
2. The [connection][] to the db is currently calling a [db in the cloud][].
3. There is also a connection to a [storage service][] that must have it's credentials changed [here](https://bit.ly/2uuvpAW)
  * if not using them same storage service, some extra changes will need to be made [here](https://bit.ly/2L3WgOh) and [here](https://bit.ly/2LpNExB) in order to store the new images
4. Finally, the core of this application revolves around the [Watson VR][] service and it will need new credentials [here](https://bit.ly/2LqxUhn)

This can also work outside of Cloud Foundry as long as the server side requirements are met, but keep the following in mind.
1. This service powered by Flask, so be sure to read the deployment [documentation][]
2. You can choose any sql database management system, just make sure that it has a driver that will work with python and change the connection string
3. In case of storing the new images locally, make sure changes are made were noted previously
4. This service will always depend on the Watson VR service

[requirements.txt]: https://git.ng.bluemix.net/carlos.santillan/test-watson-ver/blob/master/requirements.txt
[Cloud Foundry]: https://console.bluemix.net/catalog/starters/python-flask
[manifest.yml]: https://git.ng.bluemix.net/carlos.santillan/test-watson-ver/blob/master/manifest.yml
[connection]: https://git.ng.bluemix.net/carlos.santillan/test-watson-ver/blob/master/welcome_consultas.py#L14
[db in the cloud]: https://console.bluemix.net/catalog/services/db2-warehouse
[storage service]: https://console.bluemix.net/catalog/services/cloud-object-storage
[Watson VR]: https://console.bluemix.net/catalog/services/visual-recognition
[documentation]: http://flask.pocoo.org/docs/1.0/tutorial/deploy/

