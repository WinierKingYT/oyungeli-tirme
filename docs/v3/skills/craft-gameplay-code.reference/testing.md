# Gameplay code — test design

## Rules
- One test = one equivalence partition = one definite expected outcome. Parameterize only cases that share the same outcome.
- Names: `<Method>_<Condition>_<Expected>` (unit/editor), `<Condition>_<Expected>` (integration/visual). Expected is a concrete state (`IsTilted`), not a phrase.
- Every acceptance criterion in the card has a **same-layer witness** (a unit test cannot witness a scene or UI requirement).
- Undefined behavior for invalid input → ask the owner; do not invent it.
- Multi-frame tests wait on a condition (`while (x.IsBusy) await Awaitable.NextFrameAsync();`), never a fixed frame count.
- Resource systems: a simulation test runs N iterations and asserts the curve stays in the card's target range (record the seed).
- Test seams inside `#if UNITY_INCLUDE_TESTS`; tests that spawn objects use a fresh scene.
- Do not split one class's coverage between EditMode and PlayMode.

## Visual verification tests
For anything the player sees:
1. PlayMode test sets up the state and captures a screenshot.
2. `[Description("…")]` lists what to judge (readability, contrast, placement, silhouette) and the card's intended read.
3. `[Category("VisualVerification")]`; no assert.
4. The agent reviews each image against its description (one focused question per aspect); findings are *inferred-visual* until confirmed.
Deterministic properties (inside screen, not overlapping, text not overflowing, reachable by raycast) get real asserts first.

## Example
```csharp
[Test]
public void Tilt_HeavierOnLeft_TiltsLeft()
{
    var config = TestConfigs.Deck(maxTiltDeg: 12f, tiltFactor: 20f);
    var balance = new CargoBalance(config);
    balance.Place(new Cargo(massKg: 500f), DeckSide.Left);

    Assert.That(balance.TiltDegrees, Is.LessThan(0f));
}
```
