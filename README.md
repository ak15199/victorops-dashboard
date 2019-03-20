This is an experimental Python Flask app that polls the VictorOps API on a regular basis and presents a filterable/sortable list of recent incidents in a browser. 

Installation
-----
After cloning the repo, you will need to:

pip install -r requirements.txt

Prerequisites
-----
As configured, you will need to provide APIID and APIKEY environment variables in order to authenticate with VictorOps. 

If you do not configure these environment variables, then a KeyError will be thrown.

Running
-----
When running locally from the command line, use:

    $ python src/runserver.py

You can then point your web browser to the url listed in the start-up message.

Modifying for Production
-----
As it stands, this code is designed to be run locally and is not hardened for production use.

If you would like to use this in a production environment, then there are two recomemnded changes that should be applied:
* Implement a more secure means of passing in ID and key by modifying the Secrets class;
* Use a production WSGI server such as Waitress, or uWSGI.
