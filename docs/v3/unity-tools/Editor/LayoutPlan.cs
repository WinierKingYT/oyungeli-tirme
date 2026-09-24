// Target: Assets/_Project/Scripts/Editor/LayoutPlan.cs  (assembly: Game.Editor, Editor only)
// validate_layout / apply_layout: plan → validate → apply for blockouts.
// The agent writes layout.json; Validate checks it against gameplay metrics before anything touches
// the scene; Apply creates the primitives under _Env/Blockout in one undoable step.
using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Game.EditorTools
{
    public static class LayoutPlan
    {
        // Must mirror game/METRICS.md. Future: read from a Metrics ScriptableObject.
        private const float MaxGap = 2.5f;
        private const float RequiredGapShare = 0.70f;
        private const float MinCorridorWidth = 1.2f;
        private const float MinCeilingHeight = 2.4f;
        private const float MaxStepHeight = 0.35f;
        private const string BlockoutRoot = "_Env/Blockout";

        [Serializable]
        public sealed class Element
        {
            public string name;
            public string kind;        // floor | wall | platform | ramp | landmark | gap | corridor | room
            public float[] position;   // x, y, z (metres)
            public float[] size;       // x, y, z (metres)
            public float rotationY;
            public bool required;      // on the critical path
            public string purpose;     // why it exists (from the level card)
        }

        [Serializable]
        public sealed class Plan
        {
            public string level;
            public List<Element> elements = new List<Element>();
        }

        /// <summary>Validates a layout.json. Returns "OK" or one line per problem.</summary>
        public static string Validate(string layoutPath)
        {
            Plan plan = Read(layoutPath, out string error);
            if (plan == null)
            {
                return error;
            }

            var problems = new StringBuilder();
            var names = new HashSet<string>();
            foreach (Element e in plan.elements)
            {
                string id = string.IsNullOrEmpty(e.name) ? "(unnamed)" : e.name;
                if (!names.Add(id)) problems.AppendLine($"{id}: duplicate name.");
                if (e.position == null || e.position.Length != 3) problems.AppendLine($"{id}: position must be [x,y,z].");
                if (e.size == null || e.size.Length != 3) { problems.AppendLine($"{id}: size must be [x,y,z]."); continue; }
                if (string.IsNullOrEmpty(e.purpose)) problems.AppendLine($"{id}: purpose is empty (every element needs a reason).");

                float width = Mathf.Min(e.size[0], e.size[2]);
                switch (e.kind)
                {
                    case "gap":
                        float longest = Mathf.Max(e.size[0], e.size[2]);
                        float limit = e.required ? MaxGap * RequiredGapShare : MaxGap * 0.95f;
                        if (longest > limit)
                            problems.AppendLine($"{id}: gap {longest:F2} m exceeds {(e.required ? "required" : "challenge")} limit {limit:F2} m (max jump {MaxGap} m).");
                        break;
                    case "corridor":
                        if (width < MinCorridorWidth) problems.AppendLine($"{id}: corridor width {width:F2} m < {MinCorridorWidth} m.");
                        if (e.size[1] < MinCeilingHeight) problems.AppendLine($"{id}: height {e.size[1]:F2} m < {MinCeilingHeight} m.");
                        break;
                    case "room":
                        if (e.size[1] < MinCeilingHeight) problems.AppendLine($"{id}: height {e.size[1]:F2} m < {MinCeilingHeight} m.");
                        break;
                    case "platform":
                        if (e.required && e.position != null && e.position.Length == 3 && e.position[1] > 0f && e.position[1] < 1f && e.position[1] > MaxStepHeight)
                            problems.AppendLine($"{id}: height {e.position[1]:F2} m is above step height but below jump reach; make it a step, a ramp, or a clear jump.");
                        break;
                }
            }
            return problems.Length == 0 ? "OK" : problems.ToString().TrimEnd();
        }

        /// <summary>Validates, then builds primitives under _Env/Blockout. Returns a summary.</summary>
        public static string Apply(string layoutPath)
        {
            string validation = Validate(layoutPath);
            if (validation != "OK")
            {
                return "Not applied. Fix the plan first:\n" + validation;
            }
            Plan plan = Read(layoutPath, out _);
            Transform root = EnsureRoot();
            int group = Undo.GetCurrentGroup();
            Undo.SetCurrentGroupName($"Apply layout {plan.level}");

            foreach (Element e in plan.elements)
            {
                if (e.kind == "gap")
                {
                    continue; // gaps are absence of geometry; kept in the plan for validation only
                }
                GameObject go = GameObject.CreatePrimitive(PrimitiveType.Cube);
                Undo.RegisterCreatedObjectUndo(go, "Create blockout element");
                go.name = e.name;
                go.transform.SetParent(root, false);
                go.transform.localPosition = new Vector3(e.position[0], e.position[1], e.position[2]);
                go.transform.localRotation = Quaternion.Euler(0f, e.rotationY, 0f);
                go.transform.localScale = new Vector3(e.size[0], e.size[1], e.size[2]);
            }
            Undo.CollapseUndoOperations(group);
            EditorSceneManager.MarkSceneDirty(root.gameObject.scene);
            EditorSceneManager.SaveScene(root.gameObject.scene);
            return $"Applied {plan.elements.Count} elements to {BlockoutRoot} and saved the scene.";
        }

        private static Plan Read(string path, out string error)
        {
            error = null;
            if (!File.Exists(path))
            {
                error = $"layout file not found: {path}";
                return null;
            }
            try
            {
                Plan plan = JsonUtility.FromJson<Plan>(File.ReadAllText(path));
                if (plan?.elements == null || plan.elements.Count == 0)
                {
                    error = "layout has no elements.";
                    return null;
                }
                return plan;
            }
            catch (ArgumentException ex)
            {
                error = $"layout is not valid JSON: {ex.Message}";
                return null;
            }
        }

        private static Transform EnsureRoot()
        {
            string[] parts = BlockoutRoot.Split('/');
            GameObject env = GameObject.Find("/" + parts[0]) ?? new GameObject(parts[0]);
            Transform blockout = env.transform.Find(parts[1]);
            if (blockout == null)
            {
                blockout = new GameObject(parts[1]).transform;
                blockout.SetParent(env.transform, false);
            }
            return blockout;
        }
    }
}
