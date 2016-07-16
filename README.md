# APIs for Mechanical turk jobs

## 
* Utilities wrapping mechanical turk API using Boto
* An ipython notebook and supporting modules for performing annotation tasks using amazon mechanical turk.
* python scripts for dataset annotations (following datasets are supported)
  * vision - shining3

### Notable requirements

- requests
- boto
- pdfminer
- email
- jsonschema

#### minor requirements
- json
- progressbar


### Python compatibility
The boto modules that interact with mech-turk haven't been ported to python3 yet. As a result, everything here is only 
compatible with python 2.7. Thus, setup a python 2.7 virtual env for running this.
