"""Trusted pilot intake rejects stale or ambiguous review data before model use."""
import importlib.util
from pathlib import Path
import unittest

mod = importlib.util.spec_from_file_location("intake", Path(__file__).resolve().parents[1] / "consumer-pilot/prepare_context.py")
intake = importlib.util.module_from_spec(mod)
mod.loader.exec_module(intake)
repo, author = "sample/barista", "owner"

class IntakeTests(unittest.TestCase):
    def setUp(self):
        self.run = dict(id=4, event="pull_request", conclusion="success", actor={"login":author},
            path=".github/workflows/advisor-pr-intake.yml", head_repository={"full_name":repo},
            pull_requests=[{"number":2}], head_sha="a"*40)
        self.pr = dict(state="open", draft=False, user={"login":author}, title="Barista", body="data", changed_files=1,
            head={"sha":"a"*40,"ref":"pilot/barista-export-key","repo":{"full_name":repo}},
            base={"sha":"b"*40,"ref":"main","repo":{"full_name":repo}})
        self.file = dict(filename="App/src/DataModel/BRISalesSetupExt.TableExt.al",status="modified",
                         patch="@@ -1,0 +2 @@\n+change",additions=1,deletions=0)

    def capture(self):
        values = {"actions/runs/4":self.run, "pulls/2":self.pr, "pulls/2/files?per_page=2":[self.file]}
        return intake.collect("workflow_run", {"workflow_run":{"id":4}}, repo, author, values.__getitem__)

    def test_pr_source_and_diff(self):
        task=self.capture()
        self.assertEqual((task["headSha"],task["files"][0]["patch"]),(self.run["head_sha"], self.file["patch"]))

    def test_reject_stale_head(self):
        self.run["head_sha"]="c"*40
        with self.assertRaises(ValueError): self.capture()

    def test_reject_incomplete_patch(self):
        self.file["additions"]=2
        with self.assertRaises(ValueError): self.capture()

    def test_reject_fork_and_ambiguous_intake(self):
        self.pr["head"]["repo"]={"full_name":"other/fork"}
        with self.assertRaises(ValueError): self.capture()
        self.run["pull_requests"]=[]
        with self.assertRaises(ValueError): self.capture()

    def test_issue_uses_authoritative_report_without_diff(self):
        issue=dict(number=1,state="open",user={"login":author},comments=0,updated_at="now",body="reported",
                   title="Preparar la autenticación del envío de incidencias de Barista a un servicio externo")
        values={"issues/1":issue,"issues/1/comments?per_page=11":[]}
        result=intake.collect("issues",{"action":"opened","issue":{"number":1}},repo,author,values.__getitem__)
        self.assertEqual((result["kind"],result["body"]),("issue","reported"))
        self.assertNotIn("headSha",result)
