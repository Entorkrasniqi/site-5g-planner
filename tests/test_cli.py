import json

from site5g.cli import main


def test_sample_inspect_plan_pipeline(tmp_path, capsys):
    ifc = tmp_path / "office.ifc"
    assert main(["sample", str(ifc)]) == 0 and ifc.exists()

    assert main(["inspect", str(ifc)]) == 0
    out = capsys.readouterr().out
    assert "28 walls, 10 spaces" in out and "Concrete" in out

    outdir = tmp_path / "out"
    assert main(["plan", str(ifc), "--out", str(outdir), "--format", "png"]) == 0
    assert "goals met" in capsys.readouterr().out
    plan = json.loads((outdir / "plan.json").read_text())
    assert plan["storeys"][0]["goals_met"] is True
    assert (outdir / "coverage_Level_1.png").exists()


def test_plan_reports_unmet_goals(tmp_path, capsys):
    ifc = tmp_path / "office.ifc"
    main(["sample", str(ifc)])
    assert main(["plan", str(ifc), "--out", str(tmp_path / "o"), "--freq", "28", "--max-aps", "2"]) == 0
    assert "GOALS NOT MET" in capsys.readouterr().out


def test_missing_file_gives_a_friendly_error(tmp_path, capsys):
    assert main(["plan", str(tmp_path / "nope.ifc")]) == 1
    assert "error" in capsys.readouterr().err
