# CompletePeaker-Proteomics

**CompletePeaker-Proteomics** is a command-line tool for **automated peak picking in proteomics LC–MS data**.  
It uses a pre-trained **XGBoost model** together with peptide retention time references to select the most likely correct peak boundaries for each peptide.  

---

## ✨ Features
- Works directly on **Skyline/mProphet CSV outputs**
- Uses **retention time filtering** with a reference file
- Machine learning model (**XGBoost**) for robust peak scoring
- Ensures **one peptide per file** is selected
- Produces clean boundary files (`MinStartTime`, `MaxEndTime`) ready for downstream analysis

---

## 📦 Installation

Clone the repository and install:

## USAGE

```bash
git clone https://github.com/CompleteOmics/CompletePeaking.git
cd CompletePeaking/CompletePeaker-Proteomics
pip install -e .

completepeaker-pro \
  --input-folder path/to/mprophet \
  --output-folder path/to/output \
  --rt-peptides-file path/to/final.xlsx \
  --model-file xgb_model.json


