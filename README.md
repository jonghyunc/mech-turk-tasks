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

### Usage
```
$ python mturk_annotation.py -config config_shining3_potential.json
```

### Format of configuration file (-config) (json format)

```
{
    "sandbox_or_real": "sandbox" or "real",
    "category_annotation_fn": path of "categories.json",
    "static_params": {
        "title": Turk job's title,
        "description": Turk job's description,
        "keywords": list of keywords (list format: ["a", "b", "c"],
        "frame_height": frame height value (integer),
        "amount": money (float, in dollar),
        "duration": turk job duration (in sec. simple equation is possible. e.g., "3600 * 12"),
        "lifetime": turk job staying duration (in sec. simple equation is possible. e.g., "3600 * 24 * 3"),
        "max_assignments": number of assignment
    },
    "file_to_annotate": path of file to annotate,
    "duplicated_files": path of file containing list of duplicated files,
    "webpage_url": annotating webpage URL (the input file name and category name is attached as "?image=<filename>&imageType=<image_category>",
    "hit_id_output_file": output file (including path) of generated HIT list
}
```
