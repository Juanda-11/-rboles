# Hospital Patient Registry

Workshop project for the **Data Structures** course (Trees topic). It models a real-life case, the patient registry of a hospital, using a **binary search tree (BST)** in Python, with a web frontend served by the script itself.

## Case study

A hospital needs to find, admit and discharge patients quickly. Each patient is a node of a binary search tree ordered by **patient ID**:

- Smaller IDs go to the left subtree.
- Larger IDs go to the right subtree.
- Searching, inserting and deleting only follow one branch, so each operation takes `O(h)` where `h` is the height of the tree.

## Features

| Feature | Tree concept |
| --- | --- |
| Admit patient | BST insertion (duplicate IDs are rejected) |
| Search patient | Descent from the root, showing the path of comparisons |
| Discharge patient | Deletion with 0, 1 or 2 children (in-order successor) |
| In-order traversal | Patients sorted by ID |
| Pre-order / Post-order traversal | Depth-first orders |
| Level-order traversal | Breadth-first order using a queue |
| Panel statistics | Size, height, minimum and maximum |
| Tree drawing | Root, internal nodes and leaves in different colors |

## Requirements

- Python 3.8 or newer
- A web browser

No external packages are needed, only the Python standard library.

## Run

```bash
python3 hospital_registry.py
```

The browser opens automatically at `http://127.0.0.1:8000`. Press `Ctrl+C` in the terminal to stop the server.

## How to use

1. **Admit patient**: fill in ID, name, age and diagnosis, then press *Add to registry*.
2. **Search or discharge**: type an ID and press *Search* to highlight the path followed in the tree, or *Discharge* to remove the patient.
3. **Selected patient**: click any node to see the patient data and the number of comparisons needed to reach it.
4. **Traversals**: press a traversal button to see the visiting order animated on the tree.

The registry starts with nine sample patients. Data is kept in memory only and is lost when the program stops.

## Project structure

```
hospital_registry.py   Tree classes, HTTP server and frontend
README.md              Project documentation
```

Main classes and functions in `hospital_registry.py`:

- `PatientNode`: tree node holding the patient data and the left and right children.
- `PatientTree`: `insert`, `search`, `delete`, `height`, `in_order`, `pre_order`, `post_order`, `level_order`, `minimum`, `maximum` and `snapshot`.
- `RegistryHandler`: REST API used by the frontend.

## API

| Method | Route | Description |
| --- | --- | --- |
| GET | `/api/tree` | Full tree and statistics |
| GET | `/api/search?id=<id>` | Patient data and search path |
| GET | `/api/traversal?kind=<kind>` | `in_order`, `pre_order`, `post_order` or `level_order` |
| POST | `/api/patients` | Admit a patient (JSON body) |
| DELETE | `/api/patients/<id>` | Discharge a patient |
