// Target: Assets/_Project/Scripts/Editor/SceneLint.cs  (assembly: Game.Editor, Editor only)
// lint_scene: finds common scene defects and writes reviews/<date>/<scene>/lint.json.
// Checks: missing scripts, broken object references, walkable renderers without colliders,
// objects below the kill height, duplicate stacked objects, root naming convention.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Game.EditorTools
{
    public static class SceneLint
    {
        private const float KillHeight = -50f;
        private const float StackedTolerance = 0.001f;
        private static readonly string[] ExpectedRoots = { "_Env", "_Gameplay", "_Lighting", "_Cameras", "_UI", "_Debug" };
        private const string WalkableRoot = "_Env";

        [Serializable]
        private sealed class Issue
        {
            public string severity;
            public string rule;
            public string path;
            public string detail;
        }

        [Serializable]
        private sealed class Report
        {
            public string scene;
            public string checkedAt;
            public int errors;
            public int warnings;
            public List<Issue> issues = new List<Issue>();
        }

        [MenuItem("Tools/Review/Lint Scene")]
        public static void LintFromMenu() => Debug.Log($"[SceneLint] {LintActiveScene()}");

        /// <summary>Runs all checks on the active scene and returns a one-line summary.</summary>
        public static string LintActiveScene()
        {
            Scene scene = SceneManager.GetActiveScene();
            var report = new Report { scene = scene.path, checkedAt = DateTime.Now.ToString("s") };
            GameObject[] roots = scene.GetRootGameObjects();
            GameObject[] all = roots.SelectMany(r => r.GetComponentsInChildren<Transform>(true))
                .Select(t => t.gameObject).ToArray();

            CheckRoots(roots, report);
            foreach (GameObject go in all)
            {
                CheckMissingScripts(go, report);
                CheckBrokenReferences(go, report);
                CheckKillHeight(go, report);
            }
            CheckWalkableColliders(roots, report);
            CheckStacked(all, report);

            report.errors = report.issues.Count(i => i.severity == "error");
            report.warnings = report.issues.Count(i => i.severity == "warning");

            string folder = Path.Combine("reviews", DateTime.Now.ToString("yyyy-MM-dd"), scene.name);
            Directory.CreateDirectory(folder);
            string file = Path.Combine(folder, "lint.json");
            File.WriteAllText(file, JsonUtility.ToJson(report, true));
            return $"{report.errors} errors, {report.warnings} warnings → {Path.GetFullPath(file)}";
        }

        private static void CheckRoots(GameObject[] roots, Report report)
        {
            foreach (GameObject root in roots.Where(r => !ExpectedRoots.Contains(r.name)))
            {
                Add(report, "warning", "root-convention", root, $"Root '{root.name}' is not one of {string.Join(", ", ExpectedRoots)}");
            }
        }

        private static void CheckMissingScripts(GameObject go, Report report)
        {
            int missing = GameObjectUtility.GetMonoBehavioursWithMissingScriptCount(go);
            if (missing > 0)
            {
                Add(report, "error", "missing-script", go, $"{missing} missing script(s)");
            }
        }

        private static void CheckBrokenReferences(GameObject go, Report report)
        {
            foreach (Component component in go.GetComponents<Component>())
            {
                if (component == null)
                {
                    continue; // reported by missing-script
                }
                var serialized = new SerializedObject(component);
                SerializedProperty property = serialized.GetIterator();
                while (property.NextVisible(true))
                {
                    if (property.propertyType == SerializedPropertyType.ObjectReference
                        && property.objectReferenceValue == null
                        && property.objectReferenceInstanceIDValue != 0)
                    {
                        Add(report, "error", "broken-reference", go,
                            $"{component.GetType().Name}.{property.propertyPath} points to a missing object");
                    }
                }
            }
        }

        private static void CheckKillHeight(GameObject go, Report report)
        {
            if (go.transform.position.y < KillHeight)
            {
                Add(report, "warning", "below-kill-height", go, $"y = {go.transform.position.y:F1}");
            }
        }

        private static void CheckWalkableColliders(GameObject[] roots, Report report)
        {
            GameObject env = roots.FirstOrDefault(r => r.name == WalkableRoot);
            if (env == null)
            {
                return;
            }
            foreach (MeshRenderer renderer in env.GetComponentsInChildren<MeshRenderer>(true))
            {
                if (renderer.GetComponentInParent<Collider>() == null && renderer.GetComponentInChildren<Collider>() == null)
                {
                    Add(report, "warning", "renderer-without-collider", renderer.gameObject,
                        "Visible geometry under _Env has no collider (player may fall through or clip)");
                }
            }
        }

        private static void CheckStacked(GameObject[] all, Report report)
        {
            var groups = all
                .Where(go => go.GetComponent<MeshFilter>() != null)
                .GroupBy(go => (
                    mesh: go.GetComponent<MeshFilter>().sharedMesh,
                    x: Mathf.Round(go.transform.position.x / StackedTolerance),
                    y: Mathf.Round(go.transform.position.y / StackedTolerance),
                    z: Mathf.Round(go.transform.position.z / StackedTolerance)))
                .Where(g => g.Key.mesh != null && g.Count() > 1);
            foreach (var group in groups)
            {
                Add(report, "warning", "stacked-duplicates", group.First(),
                    $"{group.Count()} objects with the same mesh at the same position");
            }
        }

        private static void Add(Report report, string severity, string rule, GameObject go, string detail)
        {
            report.issues.Add(new Issue { severity = severity, rule = rule, path = PathOf(go.transform), detail = detail });
        }

        private static string PathOf(Transform t) => t.parent == null ? t.name : PathOf(t.parent) + "/" + t.name;
    }
}
