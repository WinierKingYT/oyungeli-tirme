// Target: Assets/_Project/Scripts/Editor/CriticalPathProbe.cs  (assembly: Game.Editor, Editor only)
// measure_critical_path: uses the baked NavMesh to measure Start → Decision/Moment points → Goal,
// reports reachability, length, and estimated duration at walk speed.
// Requires a baked NavMesh (AI Navigation package) and ReviewPoint markers.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Game.Tools;
using UnityEditor;
using UnityEngine;
using UnityEngine.AI;
using UnityEngine.SceneManagement;

namespace Game.EditorTools
{
    public static class CriticalPathProbe
    {
        // Must match game/METRICS.md "walk speed".
        private const float WalkSpeed = 3.5f;
        private const float SampleRadius = 2f;

        [Serializable]
        private sealed class Leg
        {
            public string from;
            public string to;
            public string status;
            public float length;
            public float seconds;
        }

        [Serializable]
        private sealed class Report
        {
            public string scene;
            public bool reachable;
            public float totalLength;
            public float totalSeconds;
            public List<Leg> legs = new List<Leg>();
            public List<string> unreachablePoints = new List<string>();
        }

        [MenuItem("Tools/Review/Measure Critical Path")]
        public static void MeasureFromMenu() => Debug.Log($"[CriticalPathProbe] {MeasureActiveScene()}");

        /// <summary>
        /// Orders points as Start, then Decision/Moment points by distance along the route, then Goal.
        /// Returns a one-line summary and writes path.json next to the review captures.
        /// </summary>
        public static string MeasureActiveScene()
        {
            Scene scene = SceneManager.GetActiveScene();
            ReviewPoint[] points = UnityEngine.Object.FindObjectsByType<ReviewPoint>(FindObjectsSortMode.None);
            ReviewPoint start = points.FirstOrDefault(p => p.Kind == ReviewPointKind.Start);
            ReviewPoint goal = points.FirstOrDefault(p => p.Kind == ReviewPointKind.Goal);
            if (start == null || goal == null)
            {
                return "Need one ReviewPoint of kind Start and one of kind Goal.";
            }

            var report = new Report { scene = scene.path, reachable = true };
            List<ReviewPoint> route = OrderRoute(start, goal, points);

            for (int i = 0; i < route.Count - 1; i++)
            {
                Leg leg = MeasureLeg(route[i], route[i + 1]);
                report.legs.Add(leg);
                if (leg.status != nameof(NavMeshPathStatus.PathComplete))
                {
                    report.reachable = false;
                    report.unreachablePoints.Add(leg.to);
                }
                report.totalLength += leg.length;
            }
            report.totalSeconds = report.totalLength / WalkSpeed;

            string folder = Path.Combine("reviews", DateTime.Now.ToString("yyyy-MM-dd"), scene.name);
            Directory.CreateDirectory(folder);
            File.WriteAllText(Path.Combine(folder, "path.json"), JsonUtility.ToJson(report, true));
            return report.reachable
                ? $"Reachable. {report.totalLength:F0} m, ~{report.totalSeconds:F0} s at walk speed."
                : $"NOT reachable: {string.Join(", ", report.unreachablePoints)}";
        }

        private static List<ReviewPoint> OrderRoute(ReviewPoint start, ReviewPoint goal, ReviewPoint[] points)
        {
            // Intermediate points ordered by straight-line progress from start toward goal.
            Vector3 axis = (goal.transform.position - start.transform.position).normalized;
            IEnumerable<ReviewPoint> middle = points
                .Where(p => p.Kind == ReviewPointKind.Decision || p.Kind == ReviewPointKind.Moment)
                .OrderBy(p => Vector3.Dot(p.transform.position - start.transform.position, axis));
            return new[] { start }.Concat(middle).Concat(new[] { goal }).ToList();
        }

        private static Leg MeasureLeg(ReviewPoint from, ReviewPoint to)
        {
            var leg = new Leg { from = from.Label, to = to.Label };
            if (!NavMesh.SamplePosition(from.transform.position, out NavMeshHit a, SampleRadius, NavMesh.AllAreas)
                || !NavMesh.SamplePosition(to.transform.position, out NavMeshHit b, SampleRadius, NavMesh.AllAreas))
            {
                leg.status = "OffNavMesh";
                return leg;
            }

            var path = new NavMeshPath();
            NavMesh.CalculatePath(a.position, b.position, NavMesh.AllAreas, path);
            leg.status = path.status.ToString();
            for (int i = 1; i < path.corners.Length; i++)
            {
                leg.length += Vector3.Distance(path.corners[i - 1], path.corners[i]);
            }
            leg.seconds = leg.length / WalkSpeed;
            return leg;
        }
    }
}
