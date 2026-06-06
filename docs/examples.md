# Examples guide

The repository includes simple starter examples under `examples/` and more complex textbook-inspired examples under `examples/textbook/`.

## Starter examples

```bash
python3 -m geomdsl.cli examples/basic_axes.geom -o /tmp/basic_axes.svg
python3 -m geomdsl.cli examples/circle_tangent.geom -o /tmp/circle_tangent.svg
python3 -m geomdsl.cli examples/line_segment.geom -o /tmp/line_segment.svg
python3 -m geomdsl.cli examples/vector_curve.geom -o /tmp/vector_curve.svg
python3 -m geomdsl.cli examples/filled_cube.geom -o /tmp/filled_cube.svg
```

## Textbook-inspired examples

These are original diagrams inspired by open online educational sources. They are not direct copies of textbook figures.

### Green's theorem circulation

File:

```text
examples/textbook/green_theorem_circulation.geom
```

Reference topic:

```text
OpenStax Calculus Volume 3, Section 6.4 Green's Theorem
https://openstax.org/books/calculus-volume-3/pages/6-4-greens-theorem
```

Try it:

```bash
python3 -m geomdsl.cli examples/textbook/green_theorem_circulation.geom -o /tmp/green_theorem.svg
```

### Gradient and level curves

File:

```text
examples/textbook/gradient_level_curves.geom
```

Reference topic:

```text
LibreTexts/OpenStax, Directional Derivatives and the Gradient
https://math.libretexts.org/Bookshelves/Calculus/Calculus_%28OpenStax%29/14%253A_Differentiation_of_Functions_of_Several_Variables/14.06%253A_Directional_Derivatives_and_the_Gradient
```

Try it:

```bash
python3 -m geomdsl.cli examples/textbook/gradient_level_curves.geom -o /tmp/gradient_levels.svg
```

### Linear transformation grid

File:

```text
examples/textbook/linear_transformation_grid.geom
```

Reference topic:

```text
MIT OpenCourseWare 18.06SC Linear Algebra
https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/
```

Try it:

```bash
python3 -m geomdsl.cli examples/textbook/linear_transformation_grid.geom -o /tmp/linear_grid.svg
```

### Eigenvectors and invariant directions

File:

```text
examples/textbook/eigenvectors_invariant_directions.geom
```

Reference topic:

```text
MIT OpenCourseWare 18.06SC, Eigenvalues and Eigenvectors
https://ocw.mit.edu/courses/18-06sc-linear-algebra-fall-2011/pages/least-squares-determinants-and-eigenvalues/eigenvalues-and-eigenvectors/
```

Try it:

```bash
python3 -m geomdsl.cli examples/textbook/eigenvectors_invariant_directions.geom -o /tmp/eigenvectors.svg
```
