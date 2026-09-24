// Target: Assets/_Project/Scripts/Tools/ReviewPoint.cs  (assembly: Game.Tools, runtime)
// Marks a camera position for visual review and critical-path measurement.
// Place via Unity MCP on the level's start, goal, decision points, and key moments (see the level card).
using UnityEngine;

namespace Game.Tools
{
    public enum ReviewPointKind
    {
        Start,
        Goal,
        Decision,
        Moment
    }

    [DisallowMultipleComponent]
    public sealed class ReviewPoint : MonoBehaviour
    {
        [SerializeField] private ReviewPointKind kind = ReviewPointKind.Moment;
        [SerializeField] private string label = "";
        [Tooltip("Camera field of view used for this capture.")]
        [SerializeField, Range(20f, 120f)] private float fieldOfView = 75f;
        [Tooltip("What the player must notice from here (copied from the level card).")]
        [SerializeField, TextArea] private string intendedRead = "";

        public ReviewPointKind Kind => kind;
        public string Label => string.IsNullOrEmpty(label) ? name : label;
        public float FieldOfView => fieldOfView;
        public string IntendedRead => intendedRead;

#if UNITY_EDITOR
        private void OnDrawGizmos()
        {
            Gizmos.color = kind switch
            {
                ReviewPointKind.Start => Color.green,
                ReviewPointKind.Goal => Color.red,
                ReviewPointKind.Decision => Color.yellow,
                _ => Color.cyan
            };
            Gizmos.DrawWireSphere(transform.position, 0.3f);
            Gizmos.DrawRay(transform.position, transform.forward * 1.5f);
        }
#endif
    }
}
