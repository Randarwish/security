"""Read MITRE ATT&CK STIX, preserve source IDs, and summarize relationships."""
import json
from pathlib import Path
from urllib.request import urlopen

SOURCE="https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master/enterprise-attack/enterprise-attack.json"

def main():
    with urlopen(SOURCE,timeout=90) as response:
        bundle=json.load(response)
    objects=[o for o in bundle["objects"] if not o.get("revoked") and not o.get("x_mitre_deprecated")]
    techniques={}
    for o in objects:
        if o.get("type")!="attack-pattern": continue
        ids=[r["external_id"] for r in o.get("external_references",[]) if r.get("source_name")=="mitre-attack" and "external_id" in r]
        if not ids: continue
        techniques[o["id"]]={"attack_id":ids[0],"name":o.get("name",""),"description":o.get("description","")[:300],"stix_id":o["id"]}
    relationships=[{"source":r["source_ref"],"target":r["target_ref"],"type":r["relationship_type"]} for r in objects if r.get("type")=="relationship" and (r.get("source_ref") in techniques or r.get("target_ref") in techniques)]
    output={"source":SOURCE,"stix_bundle_id":bundle.get("id"),"technique_count":len(techniques),"relationship_count":len(relationships),"techniques":list(techniques.values()),"relationships":relationships}
    Path("results").mkdir(exist_ok=True)
    Path("results/threatgraph.json").write_text(json.dumps(output,indent=2))
    print(f"Indexed {len(techniques)} techniques and {len(relationships)} associated relationships")

if __name__=="__main__": main()
