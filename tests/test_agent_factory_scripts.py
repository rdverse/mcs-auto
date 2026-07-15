import json
import pathlib
import subprocess
import tempfile
import unittest


REPO_ROOT = pathlib.Path("/home/runner/work/mcs-auto/mcs-auto")


class AgentFactoryScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.tmp = pathlib.Path(self.temp_dir.name)
        self.agent_spec = self.tmp / "agent-spec.yaml"
        self.workflow_spec = self.tmp / "workflow-spec.yaml"
        self.output_dir = self.tmp / "generated"

        self.agent_spec.write_text(
            "\n".join(
                [
                    "name: Customer Support Agent",
                    "description: Helps support engineers investigate tickets.",
                    "knowledge:",
                    "  - SharePoint",
                    "actions:",
                    "  - Create Ticket",
                    "workflow:",
                    "  - Classify Ticket",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        self.workflow_spec.write_text(
            "\n".join(
                [
                    "name: ticket-workflow",
                    "description: Ticket workflow",
                    "triggers:",
                    "  - ticket.created",
                    "steps:",
                    "  - name: Classify Ticket",
                    "    type: classify",
                    "integrations:",
                    "  - Dataverse",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_validate_specs_passes_for_valid_yaml(self) -> None:
        result = subprocess.run(
            [
                "python",
                str(REPO_ROOT / "scripts" / "validate_specs.py"),
                "--agent-spec",
                str(self.agent_spec),
                "--workflow-spec",
                str(self.workflow_spec),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr + result.stdout)
        self.assertIn("Specification validation passed.", result.stdout)

    def test_validate_specs_fails_for_invalid_agent(self) -> None:
        self.agent_spec.write_text("name: ''\n", encoding="utf-8")
        result = subprocess.run(
            [
                "python",
                str(REPO_ROOT / "scripts" / "validate_specs.py"),
                "--agent-spec",
                str(self.agent_spec),
                "--workflow-spec",
                str(self.workflow_spec),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("agent-spec:", result.stdout)

    def test_generate_deploy_and_smoke_scripts(self) -> None:
        generate = subprocess.run(
            [
                "python",
                str(REPO_ROOT / "scripts" / "generate_assets.py"),
                "--agent-spec",
                str(self.agent_spec),
                "--workflow-spec",
                str(self.workflow_spec),
                "--output-dir",
                str(self.output_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(generate.returncode, 0, msg=generate.stderr + generate.stdout)

        deploy = subprocess.run(
            [
                "python",
                str(REPO_ROOT / "scripts" / "deploy_assets.py"),
                "--generated-dir",
                str(self.output_dir),
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(deploy.returncode, 0, msg=deploy.stderr + deploy.stdout)

        smoke = subprocess.run(
            [
                "python",
                str(REPO_ROOT / "scripts" / "smoke_test.py"),
                "--generated-dir",
                str(self.output_dir),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(smoke.returncode, 0, msg=smoke.stderr + smoke.stdout)

        manifest = json.loads((self.output_dir / "deployment-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["schemaVersion"], "1.0")


if __name__ == "__main__":
    unittest.main()
