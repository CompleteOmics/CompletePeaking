Absolutely 👍 — here’s the **full README.md in one piece** (no breaks, no missing parts) that you can just copy-paste into your `CompletePeaker-Metabolomics/README.md`.

---

````markdown
# CompletePeaker-Metabolomics

**CompletePeaker-Metabolomics** is a Python command-line tool for **peak boundary detection** in LC–MS metabolomics chromatograms.  
It smooths signals, finds the apex near expected retention time, and assigns start/end peak boundaries.

---

##  Installation

1. Clone the repository:
```bash
git clone https://github.com/CompleteOmics/CompletePeaking.git
cd CompletePeaking/CompletePeaker-Metabolomics
````

2. Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\activate
```

3. Install the package:

```bash
pip install -e .
```

This installs the CLI tool: **`completepeaker-met`**

---

##  Input format

The tool expects a CSV file with the following columns:

| Column                    | Description                                 |
| ------------------------- | ------------------------------------------- |
| `Times`                   | Comma-separated retention times (floats)    |
| `Intensities`             | Comma-separated signal intensities (floats) |
| `Molecule`                | Molecule identifier                         |
| `Explicit Retention Time` | Expected RT (float)                         |
| `FileName`                | File/run identifier                         |

**Example row**

```
0.1,0.2,0.3,0.4,...    100,150,200,120,...    Glucose    5.6    Sample1.d
```

---

## ▶ Usage

Run the tool from the command line:

```bash
completepeaker-met --input-file examples/Raw_Data_example.csv --output-file examples/Final_Peak_Boundaries.csv
```

### Arguments

* `--input-file` : Path to the input CSV
* `--output-file` : Path to save the results CSV
* `--rt-half-window` : Search window around explicit RT (default: 1.0 min)
* `--fraction-of-apex` : Boundary threshold fraction (default: 0.05)
* `--max-extension` : Maximum extension points for bounds (default: 50)
* `--verbose` : Print detailed logs

---

##  Output format

The output is a CSV file with one row per detected peak:

| Column         | Description                      |
| -------------- | -------------------------------- |
| `FileName`     | Original file name               |
| `Molecule`     | Molecule identifier              |
| `MinStartTime` | Calculated left bound (minutes)  |
| `MaxEndTime`   | Calculated right bound (minutes) |
