

````markdown
#  CompletePeaker-Metabolomics

**CompletePeaker-Metabolomics** is a Python-based command-line tool for automated **peak boundary detection** in LC–MS metabolomics data.  
It smooths chromatographic signals, identifies peak apex near the expected retention time, and assigns optimal start/end boundaries.



##  Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/CompleteOmics/CompletePeaking.git
cd CompletePeaking/CompletePeaker-Metabolomics
````

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
```

This installs the CLI tool: `completepeaker-met`



##  Input Format

The tool expects a CSV file with the following columns:

| Column                    | Description                              |
| ------------------------- | ---------------------------------------- |
| `Times`                   | Comma-separated retention times (floats) |
| `Intensities`             | Comma-separated intensities (floats)     |
| `Molecule`                | Molecule name or ID                      |
| `Explicit Retention Time` | Expected RT (float)                      |
| `FileName`                | Source file/run name                     |

**Example:**

```
0.1,0.2,0.3,...    100,150,200,...    Glucose    5.6    Sample1.d
```

---

##  Usage

Run the tool via CLI:

```bash
completepeaker-met --input-file examples/Raw_Data_example.csv --output-file examples/Final_Peak_Boundaries.csv
```

### Optional Arguments

| Flag                 | Description                                         | Default    |
| -------------------- | --------------------------------------------------- | ---------- |
| `--input-file`       | Path to input CSV                                   | *required* |
| `--output-file`      | Path to output CSV                                  | *required* |
| `--rt-half-window`   | RT window (± minutes) around explicit RT for search | `1.0`      |
| `--fraction-of-apex` | Boundary threshold as fraction of apex intensity    | `0.05`     |
| `--max-extension`    | Maximum number of points to extend beyond threshold | `50`       |
| `--verbose`          | Enable logging                                      | off        |



##  Output Format

The output is a CSV with one row per detected peak:

| Column         | Description                      |
| -------------- | -------------------------------- |
| `FileName`     | Input filename                   |
| `Molecule`     | Molecule ID                      |
| `MinStartTime` | Left boundary of the peak (min)  |
| `MaxEndTime`   | Right boundary of the peak (min) |


