// Target: Assets/_Project/Scripts/Editor/ImageDiff.cs  (assembly: Game.Editor, Editor only)
// compare_images: pixel difference between two captures of the same view (before/after or golden/current).
// Writes <after>_diff.png (changed pixels in red over a dimmed copy) and returns the changed share and
// the bounding box of the change, so vision is only asked to describe the changed region.
using System;
using System.IO;
using UnityEngine;

namespace Game.EditorTools
{
    public static class ImageDiff
    {
        // Per-channel difference (0–1) above which a pixel counts as changed; ignores compression noise.
        private const float ChannelThreshold = 0.08f;
        private const float DimFactor = 0.35f;

        [Serializable]
        public sealed class Result
        {
            public string before;
            public string after;
            public string diffImage;
            public float changedShare;
            public int minX, minY, maxX, maxY;
            public string error;
        }

        /// <summary>Compares two PNGs of equal size. Returns JSON.</summary>
        public static string Compare(string beforePath, string afterPath)
        {
            var result = new Result { before = beforePath, after = afterPath };
            Texture2D before = Load(beforePath);
            Texture2D after = Load(afterPath);
            try
            {
                if (before == null || after == null)
                {
                    result.error = "Could not read one of the images.";
                    return JsonUtility.ToJson(result, true);
                }
                if (before.width != after.width || before.height != after.height)
                {
                    result.error = $"Size mismatch: {before.width}x{before.height} vs {after.width}x{after.height}. Capture with the same resolution.";
                    return JsonUtility.ToJson(result, true);
                }

                Color[] a = before.GetPixels();
                Color[] b = after.GetPixels();
                var output = new Color[b.Length];
                int changed = 0;
                result.minX = after.width; result.minY = after.height; result.maxX = -1; result.maxY = -1;

                for (int i = 0; i < b.Length; i++)
                {
                    bool isChanged = Mathf.Abs(a[i].r - b[i].r) > ChannelThreshold
                                     || Mathf.Abs(a[i].g - b[i].g) > ChannelThreshold
                                     || Mathf.Abs(a[i].b - b[i].b) > ChannelThreshold;
                    if (!isChanged)
                    {
                        output[i] = b[i] * DimFactor;
                        continue;
                    }
                    changed++;
                    output[i] = Color.red;
                    int x = i % after.width;
                    int y = i / after.width;
                    result.minX = Mathf.Min(result.minX, x); result.maxX = Mathf.Max(result.maxX, x);
                    result.minY = Mathf.Min(result.minY, y); result.maxY = Mathf.Max(result.maxY, y);
                }

                result.changedShare = (float)changed / b.Length;
                var diff = new Texture2D(after.width, after.height, TextureFormat.RGB24, false);
                diff.SetPixels(output);
                diff.Apply();
                result.diffImage = Path.Combine(Path.GetDirectoryName(afterPath) ?? ".",
                    Path.GetFileNameWithoutExtension(afterPath) + "_diff.png");
                File.WriteAllBytes(result.diffImage, diff.EncodeToPNG());
                UnityEngine.Object.DestroyImmediate(diff);
                return JsonUtility.ToJson(result, true);
            }
            finally
            {
                if (before != null) UnityEngine.Object.DestroyImmediate(before);
                if (after != null) UnityEngine.Object.DestroyImmediate(after);
            }
        }

        private static Texture2D Load(string path)
        {
            if (!File.Exists(path))
            {
                return null;
            }
            var texture = new Texture2D(2, 2, TextureFormat.RGB24, false);
            return texture.LoadImage(File.ReadAllBytes(path)) ? texture : null;
        }
    }
}
