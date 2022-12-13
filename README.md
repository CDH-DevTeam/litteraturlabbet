# litteraturlabbet
A Django app for the Litteraturlabbet project at CDH

## Data
The data for this application was collected from the Litteraturbanken data as `.html` as files, which were subsequently processed and analyzed with the [Passim](https://github.com/dasmiq/passim) tool. The data is organized as `Work`s belonging to `Author`s. Each `Work` has multiple `Pages`.

The original data was delivered as directories corresponding to a work, or book, containing each page as a separate `.html` file.
```
├── lb7598
│   ├── res_000000.html
│   ├── res_000001.html
│   ├── res_000002.html
│   ├── res_000003.html
│   ├── res_000004.html
│   ├── res_000005.html
│   └── ...
├── lb7598
└── ...
```
Methods to parse this structure is found in the `data/litteraturbanken.py` file.

Methods to upload this data to Diana is found in the `data/upload.py` file.

### Metadata
To extract the metadata, use the Litteraturbanken API: `https://litteraturbanken.se/api/get_work_info?lbworkid=<lbworkid>`, where `lbworkid` is a (non-unique) identifier of a certain work in their collections. See `data/upload.py` for an example.

## Using Passim
It is highly recommended to read the [instructions](https://github.com/dasmiq/passim) and examples of Passim before using it. Also consult the model specification of this application to understand how to upload the results.
### Input
To run Passim, it is important that the data has a correct input format. The scope of the text should be the minimal context where reuse can be identified, which is normally at *page* level of works. 

To make sure Passim works, use create a single file, e.g. `in.json`. It uses a non-standard JSON format, where each entry is a piece of text represented as a JS array, followed by a newline, like follows:

```js
{"id": 0, "page": 497812, "series": "lb1", "work": "lb1", "text": "..."}
{"id": 1, "page": 497811, "series": "lb1", "work": "lb1", "text": "..."}
{"id": 2, "page": 497810, "series": "lb1", "work": "lb1", "text": "..."}
{"id": 3, "page": 497810, "series": "lb2", "work": "lb2", "text": "..."}
{"id": 4, "page": 497810, "series": "lb3", "work": "lb3", "text": "..."}
```

Each array has the following attributes:
- `id`: A unique ID for the entry
- `page`: A unique ID for the page
- `series`: The scope where not to look for reuse, e.g. within a book. Most often the ID of the work, e.g. `lbworkid`.
- `work`: The work ID
- `text`: The raw text on the page

### Run 
To run Passim, please consult the [instructions](https://github.com/dasmiq/passim). If you have a powerful computer, consider launching it with
```bash
SPARK_SUBMIT_ARGS='--master local[12] --driver-memory 32G --executor-memory 8G' passim in.json out/ 
```

### Output

The resulting output is organized in the `out/out.json/*.json` directory as multiple json files. The results in each file are found cases of reuse, so called *segments*, which look like the following:
```js
{"uid":-6649366733325186173,"cluster":298,"size":68,"bw":0,"ew":140,"id":255145,"page":500053,"series":"lb1","text":"...","work":"lb1","gid":6696630315996178597,"begin":0,"end":1148}
{"uid":-1031951694183583480,"cluster":298,"size":68,"bw":0,"ew":135,"id":255195,"page":509037,"series":"lb2","text":"...","work":"lb2","gid":276275582612511478,"begin":0,"end":1097}
```
with these attributes:
- `uid`: Unique identifier for the segment
- `cluster`: Cluster which the segment belongs to
- `size`: Number of segments in cluster
- `bw`: Word location beginning
- `ew`: Word location end
- `id`: Incremental unique identifier
- `page`: ID of the page where the segment was found
- `series`: Scope where the segment was found
- `text`: The extracted textual reuse
- `gid`: Unique identifier for the segment
- `begin`: Character location beginning
- `end`: Character location end

### Converting to Diana
The resulting data is converted to Django and Diana with simple mappings. One segment in the resulting files corresponds to a row in the `Segment` table in Diana. Each segment belongs to a `Cluster`, with an ID and size. A `Cluster` belongs to a `Page`, and a `Page` belongs to a `Work`. Each `Work` then has a foreign key to an `Author`.