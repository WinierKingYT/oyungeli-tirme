// Target: Assets/_Project/Scripts/Editor/ReviewCapture.cs  (assembly: Game.Editor, Editor only)
// capture_review_set: renders a top-down orthographic overview plus one image per ReviewPoint
// into reviews/<yyyy-MM-dd>/<scene>/ and writes index.json describing each image.
// Call from Unity MCP via the menu item or by invoking ReviewCapture.CaptureActiveScene().
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Game.Tools;
using UnityEditor;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace Game.EditorTools
{
    public static class ReviewCapture
    {
        private const int Width = 1600;
        private const int Height = 900;
        private const float OverviewPadding = 1.1f;

        [Serializable]
        private sealed class CaptureEntry
        {
            public string file;
            public string kind;
            public string label;
            public string intendedRead;
            public float[] position;
            public float[] forward;
        }

        [Serializable]
        private sealed class CaptureIndex
        {
            public string scene;
            public string capturedAt;
            public List<CaptureEntry> images = new List<CaptureEntry>();
        }

        [MenuItem("Tools/Review/Capture Review Set")]
        public static void CaptureFromMenu() => Debug.Log($"[ReviewCapture] {CaptureActiveScene()}");

        /// <summary>Captures the review set and returns the output folder path.</summary>
        public static string CaptureActiveScene()
        {
            Scene scene = SceneManager.GetActiveScene();
            string folder = Path.Combine("reviews", DateTime.Now.ToString("yyyy-MM-dd"), scene.name);
            Directory.CreateDirectory(folder);

            var index = new CaptureIndex { scene = scene.path, capturedAt = DateTime.Now.ToString("s") };
            var cameraObject = new GameObject("__ReviewCaptureCamera") { hideFlags = HideFlags.HideAndDontSave };
            try
            {
                Camera cam = cameraObject.AddComponent<Camera>();
                cam.enabled = false;

                if (TryGetSceneBounds(out Bounds bounds))
                {
                    ConfigureOverview(cam, bounds);
                    index.images.Add(Save(cam, folder, "00_overview", "Overview", "Top-down layout", ""));
                }

                ReviewPoint[] points = UnityEngine.Object.FindObjectsByType<ReviewPoint>(FindObjectsSortMode.None)
                    .OrderBy(p => p.Kind == ReviewPointKind.Start ? 0 : p.Kind == ReviewPointKind.Goal ? 2 : 1)
                    .ThenBy(p => p.Label)
                    .ToArray();

                for (int i = 0; i < points.Length; i++)
                {
                    ReviewPoint point = points[i];
                    ConfigurePerspective(cam, point);
                    string file = $"{i + 1:00}_{point.Kind}_{Sanitize(point.Label)}";
                    index.images.Add(Save(cam, folder, file, point.Kind.ToString(), point.Label, point.IntendedRead,
                        point.transform));
                }
            }
            finally
            {
                UnityEngine.Object.DestroyImmediate(cameraObject);
            }

            File.WriteAllText(Path.Combine(folder, "index.json"), JsonUtility.ToJson(index, true));
            return Path.GetFullPath(folder);
        }

        private static bool TryGetSceneBounds(out Bounds bounds)
        {
            Renderer[] renderers = UnityEngine.Object.FindObjectsByType<Renderer>(FindObjectsSortMode.None)
                .Where(r => r.enabled && r.gameObject.activeInHierarchy && !(r is ParticleSystemRenderer))
                .ToArray();
            bounds = default;
            if (renderers.Length == 0)
            {
                return false;
            }

            bounds = renderers[0].bounds;
            foreach (Renderer renderer in renderers)
            {
                bounds.Encapsulate(renderer.bounds);
            }
            return true;
        }

        private static void ConfigureOverview(Camera cam, Bounds bounds)
        {
            cam.orthographic = true;
            float aspect = (float)Width / Height;
            cam.orthographicSize = Mathf.Max(bounds.extents.z, bounds.extents.x / aspect) * OverviewPadding;
            cam.transform.SetPositionAndRotation(
                bounds.center + Vector3.up * (bounds.extents.y + 50f),
                Quaternion.Euler(90f, 0f, 0f));
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = bounds.size.y + 200f;
        }

        private static void ConfigurePerspective(Camera cam, ReviewPoint point)
        {
            cam.orthographic = false;
            cam.fieldOfView = point.FieldOfView;
            cam.transform.SetPositionAndRotation(point.transform.position, point.transform.rotation);
            cam.nearClipPlane = 0.05f;
            cam.farClipPlane = 1000f;
        }

        private static CaptureEntry Save(Camera cam, string folder, string file, string kind, string label,
            string intendedRead, Transform source = null)
        {
            var target = new RenderTexture(Width, Height, 24);
            RenderTexture previous = RenderTexture.active;
            var image = new Texture2D(Width, Height, TextureFormat.RGB24, false);
            try
            {
                cam.targetTexture = target;
                cam.Render();
                RenderTexture.active = target;
                image.ReadPixels(new Rect(0, 0, Width, Height), 0, 0);
                image.Apply();
                File.WriteAllBytes(Path.Combine(folder, file + ".png"), image.EncodeToPNG());
            }
            finally
            {
                cam.targetTexture = null;
                RenderTexture.active = previous;
                UnityEngine.Object.DestroyImmediate(target);
                UnityEngine.Object.DestroyImmediate(image);
            }

            Vector3 position = source != null ? source.position : cam.transform.position;
            Vector3 forward = source != null ? source.forward : cam.transform.forward;
            return new CaptureEntry
            {
                file = file + ".png",
                kind = kind,
                label = label,
                intendedRead = intendedRead,
                position = new[] { position.x, position.y, position.z },
                forward = new[] { forward.x, forward.y, forward.z }
            };
        }

        private static string Sanitize(string text)
        {
            char[] invalid = Path.GetInvalidFileNameChars();
            return new string(text.Select(c => invalid.Contains(c) || c == ' ' ? '_' : c).ToArray());
        }
    }
}
