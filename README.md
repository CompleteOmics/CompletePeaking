# CompletePeaking

**CompletePeaking** is a collection of open-source tools developed by **CompleteOmics** for automated **peak detection and boundary assignment** in LC–MS data.  

It currently includes:

- **[CompletePeaker-Metabolomics](./CompletePeaker-Metabolomics/)**  
  Peak boundary detection for LC–MS **metabolomics** data.  
  Input: chromatogram CSVs → Output: refined start/end boundaries.

- **[CompletePeaker-Proteomics](./CompletePeaker-Proteomics/)**  
  Machine learning–powered peak picking for LC–MS **proteomics** data.  
  Input: Skyline/mProphet CSVs + retention-time reference + XGBoost model → Output: peptide-level boundaries.

---

## 📦 Installation

Clone the repository and choose the submodule you want to work with:

```bash
git clone https://github.com/CompleteOmics/CompletePeaking.git
cd CompletePeaking
