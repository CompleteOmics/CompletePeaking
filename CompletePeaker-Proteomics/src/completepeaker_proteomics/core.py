import os
import glob
import pandas as pd
import numpy as np
import xgboost as xgb

FEATURES = [
    "main_var_Intensity",
    "var_Library_intensity_dot-product",
    "var_Shape_(weighted)",
    "var_Co-elution_(weighted)",
    "var_Co-elution_count",
    "var_Signal_to_noise",
]

def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    return df[FEATURES]

def postprocess_predictions(df: pd.DataFrame, scores: np.ndarray, seq_col="Sequence", file_col="FileName") -> pd.DataFrame:
    df = df.copy()
    df["Prediction_Score"] = scores
    df["Predicted_Label"] = 0
    idxmax = df.groupby([seq_col, file_col])["Prediction_Score"].idxmax()
    df.loc[idxmax, "Predicted_Label"] = 1
    return df

def _log(msg: str, verbose: bool):
    if verbose:
        print(msg)

def process_file(file_path: str, rt_peptides_df: pd.DataFrame, output_folder: str, model: xgb.XGBClassifier, *, verbose: bool = False):
    _log(f"—— Processing: {os.path.basename(file_path)}", verbose)
    new_data = pd.read_csv(file_path)
    _log(f"   columns: {', '.join(map(str, new_data.columns))}", verbose)

    merged = pd.merge(
        new_data,
        rt_peptides_df[["Peptide", "Peptide Retention Time"]],
        left_on="Sequence",
        right_on="Peptide",
        how="left",
    )
    has_rt = merged["Peptide Retention Time"].notna()
    with_rt = merged[
        has_rt
        & (merged["RT"] >= merged["Peptide Retention Time"] - 0.4)
        & (merged["RT"] <= merged["Peptide Retention Time"] + 0.4)
    ]
    without_rt = merged[~has_rt]
    final_df = pd.concat([with_rt, without_rt], ignore_index=True)
    final_df = final_df.drop(columns=["Peptide", "Peptide Retention Time"])
    _log(f"   rows: total={len(new_data)}, kept_with_RT={len(with_rt)}, kept_no_RT={len(without_rt)}", verbose)

    X = preprocess_data(final_df)
    scores = model.predict_proba(X)[:, 1]
    processed = postprocess_predictions(final_df, scores)

    out_cols = ["FileName", "PeptideModifiedSequence", "MinStartTime", "MaxEndTime", "Prediction_Score"]
    out = processed.loc[processed["Predicted_Label"] == 1, out_cols]

    base = os.path.basename(file_path).replace("_mprophet", "")
    os.makedirs(output_folder, exist_ok=True)
    out_path = os.path.join(output_folder, base)
    out.to_csv(out_path, index=False)
    _log(f"   wrote: {out_path} (rows={len(out)})", verbose)

def process_folder(input_folder: str, output_folder: str, rt_peptides_file: str, model_file: str, *, verbose: bool = False, limit: int = 0):
    _log(f"input: {input_folder}", verbose)
    _log(f"rt xlsx: {rt_peptides_file}", verbose)
    _log(f"model: {model_file}", verbose)
    _log(f"output: {output_folder}", verbose)

    rt_peptides_df = pd.read_excel(rt_peptides_file)
    model = xgb.XGBClassifier()
    model.load_model(model_file)

    files = sorted(glob.glob(os.path.join(input_folder, "*.csv")))
    if limit and limit > 0:
        files = files[:limit]
    _log(f"found {len(files)} CSV file(s)", verbose)

    for i, f in enumerate(files, 1):
        _log(f"[{i}/{len(files)}]", verbose)
        process_file(f, rt_peptides_df, output_folder, model, verbose=verbose)
