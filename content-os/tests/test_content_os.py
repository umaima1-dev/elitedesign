import json, os, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import outlier

def posts(creator, views):
    return [dict(creator=creator, url=f"u{i}", views=v, likes=v // 20) for i, v in enumerate(views)]

class Outlier(unittest.TestCase):
    def test_flags_outlier_using_median_baseline(self):
        d = posts("a", [1000] * 9 + [9000])
        rows, _ = outlier.score(d, multiplier=5)
        top = rows[0]
        self.assertTrue(top["is_outlier"]); self.assertEqual(top["multiplier"], 9.0)
    def test_multiplier_configurable(self):
        d = posts("a", [1000] * 9 + [3000])
        self.assertFalse(outlier.score(d, 5)[0][0]["is_outlier"])
        self.assertTrue(outlier.score(d, 2)[0][0]["is_outlier"])
    def test_small_samples_skipped(self):
        rows, skipped = outlier.score(posts("b", [1, 2, 3]))
        self.assertEqual(rows, []); self.assertEqual(skipped, {"b": 3})

class Gate(unittest.TestCase):
    def run_cli(self, env, *args):
        return subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "approve.py"), *args],
                              capture_output=True, text=True, env=env)
    def test_gate_lifecycle(self):
        with tempfile.TemporaryDirectory() as t:
            env = dict(os.environ, CONTENT_OS_APPROVALS=os.path.join(t, "ap"))
            f = os.path.join(t, "post.md"); open(f, "w").write("hello")
            self.assertNotEqual(self.run_cli(env, "check", f, "--action", "publish").returncode, 0)
            rid = self.run_cli(env, "request", f, "--action", "publish").stdout.strip()
            self.assertNotEqual(self.run_cli(env, "check", f, "--action", "publish").returncode, 0)
            self.run_cli(env, "approve", rid, "--by", "tester")
            self.assertEqual(self.run_cli(env, "check", f, "--action", "publish").returncode, 0)
            self.assertNotEqual(self.run_cli(env, "check", f, "--action", "message").returncode, 0)
            open(f, "w").write("edited")
            self.assertNotEqual(self.run_cli(env, "check", f, "--action", "publish").returncode, 0)

class Lint(unittest.TestCase):
    def test_phrase_file_drives_lint(self):
        with tempfile.TemporaryDirectory() as t:
            b = os.path.join(t, "b.txt"); open(b, "w").write("# c\nforbidden thing\n")
            f = os.path.join(t, "x.md"); open(f, "w").write("this has a Forbidden Thing in it\n")
            env = dict(os.environ, CONTENT_OS_BANNED=b)
            r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "lint_voice.py"), f], capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 1)
            open(f, "w").write("clean\n")
            r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "lint_voice.py"), f], capture_output=True, text=True, env=env)
            self.assertEqual(r.returncode, 0)

class Repo(unittest.TestCase):
    def test_validate(self):
        r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "validate.py")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout)

if __name__ == "__main__":
    unittest.main()
