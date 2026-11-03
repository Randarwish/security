"""CIC-IDS2017 exploratory flow-classification and corruption stress test."""
import argparse
import json
from pathlib import Path

def main():
    import numpy as np
    import pandas as pd
    from sklearn.ensemble import HistGradientBoostingClassifier
    from sklearn.impute import SimpleImputer
    from sklearn.metrics import balanced_accuracy_score, classification_report, confusion_matrix
    from sklearn.model_selection import train_test_split
    from sklearn.pipeline import make_pipeline

    p=argparse.ArgumentParser()
    p.add_argument("--data-dir", default="data/cicids2017")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--max-rows", type=int, default=150000)
    args=p.parse_args()
    paths=sorted(Path(args.data_dir).rglob("*.csv"))
    if not paths: p.error("No CSV files found. Download official CIC-IDS2017 MachineLearningCSV first.")
    frames=[]
    for path in paths:
        frame=pd.read_csv(path, low_memory=False)
        frame.columns=frame.columns.str.strip()
        if "Label" not in frame: continue
        frames.append(frame)
    if not frames: p.error("CSV files did not contain a Label column")
    df=pd.concat(frames,ignore_index=True)
    if len(df)>args.max_rows: df=df.sample(args.max_rows,random_state=args.seed)
    y=(df["Label"].astype(str).str.strip().str.upper()!="BENIGN").astype(int)
    X=df.drop(columns=["Label"]).select_dtypes(include="number").replace([np.inf,-np.inf],np.nan)
    X=X.loc[:,X.notna().any()]
    if X.empty or y.nunique()<2: p.error("Need numeric features and both benign and attack labels")
    X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=.2,random_state=args.seed,stratify=y)
    pipe=make_pipeline(SimpleImputer(strategy="median"),HistGradientBoostingClassifier(max_iter=100,random_state=args.seed))
    pipe.fit(X_train,y_train)
    clean=pipe.predict(X_test)
    rng=np.random.default_rng(args.seed)
    scales=X_train.std().fillna(0).to_numpy()
    noisy=X_test.to_numpy(dtype=float)+rng.normal(0,0.05,size=X_test.shape)*scales
    noisy_pred=pipe.predict(pd.DataFrame(noisy,columns=X_test.columns))
    results={"dataset":"CIC-IDS2017 research testbed","seed":args.seed,"rows":len(df),"features":list(X.columns),"split":"random stratified; potential temporal leakage","clean_balanced_accuracy":balanced_accuracy_score(y_test,clean),"noise_stress_balanced_accuracy":balanced_accuracy_score(y_test,noisy_pred),"clean_report":classification_report(y_test,clean,output_dict=True,zero_division=0),"clean_confusion_matrix":confusion_matrix(y_test,clean).tolist(),"warning":"Gaussian feature noise is NOT a validated feasible adversarial network attack"}
    Path("results").mkdir(exist_ok=True)
    Path("results/adversarialsoc.json").write_text(json.dumps(results,indent=2))
    print("Saved results/adversarialsoc.json")

if __name__=="__main__": main()
