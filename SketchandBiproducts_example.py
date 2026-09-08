from dataclasses import dataclass, field
from typing import Dict, List, Tuple


# ============================================================
# BASIC DATA
# ============================================================

@dataclass(frozen=True)
class Sort:
    """An object (sort) of the sketch."""
    name: str


@dataclass(frozen=True)
class Map:
    """A morphism between sorts."""
    name: str
    source: Sort
    target: Sort


@dataclass(frozen=True)
class Cone:
    """
    A specified cone.

    For a binary product A x B, this consists of
        P -> A
        P -> B
    with P declared to be the limit.
    """
    name: str
    vertex: Sort
    legs: Tuple[Map, ...]
    is_limit: bool = True


@dataclass(frozen=True)
class Equation:
    """An equation between formal expressions."""
    left: str
    right: str


# ============================================================
# LIMIT SKETCH
# ============================================================

@dataclass
class Sketch:
    """
    Computational representation of a limit sketch:

        (Sorts, Maps, Cones, Equations)
    """

    sorts: Dict[str, Sort] = field(default_factory=dict)
    maps: Dict[str, Map] = field(default_factory=dict)
    cones: Dict[str, Cone] = field(default_factory=dict)
    equations: List[Equation] = field(default_factory=list)

    # --------------------------------------------------------
    # Add a sort
    # --------------------------------------------------------

    def add_sort(self, name: str) -> Sort:
        if name in self.sorts:
            raise ValueError(f"Sort '{name}' already exists.")

        sort = Sort(name)
        self.sorts[name] = sort
        return sort

    # --------------------------------------------------------
    # Add a map
    # --------------------------------------------------------

    def add_map(
        self,
        name: str,
        source: str,
        target: str
    ) -> Map:

        if name in self.maps:
            raise ValueError(f"Map '{name}' already exists.")

        if source not in self.sorts:
            raise ValueError(
                f"Unknown source sort '{source}'."
            )

        if target not in self.sorts:
            raise ValueError(
                f"Unknown target sort '{target}'."
            )

        map_ = Map(
            name=name,
            source=self.sorts[source],
            target=self.sorts[target]
        )

        self.maps[name] = map_

        return map_

    # --------------------------------------------------------
    # Add a cone
    # --------------------------------------------------------

    def add_cone(
        self,
        name: str,
        vertex: str,
        legs: Tuple[str, ...],
        is_limit: bool = True
    ) -> Cone:

        if name in self.cones:
            raise ValueError(
                f"Cone '{name}' already exists."
            )

        if vertex not in self.sorts:
            raise ValueError(
                f"Unknown cone vertex '{vertex}'."
            )

        leg_maps = []

        for leg in legs:

            if leg not in self.maps:
                raise ValueError(
                    f"Unknown map '{leg}'."
                )

            map_ = self.maps[leg]

            if map_.source.name != vertex:
                raise ValueError(
                    f"Map '{leg}' does not start at "
                    f"cone vertex '{vertex}'."
                )

            leg_maps.append(map_)

        cone = Cone(
            name=name,
            vertex=self.sorts[vertex],
            legs=tuple(leg_maps),
            is_limit=is_limit
        )

        self.cones[name] = cone

        return cone

    # --------------------------------------------------------
    # Add an equation
    # --------------------------------------------------------

    def add_equation(
        self,
        left: str,
        right: str
    ):
        self.equations.append(
            Equation(left, right)
        )

    # --------------------------------------------------------
    # Display
    # --------------------------------------------------------

    def describe(self):

        print("=" * 60)
        print("LIMIT SKETCH")
        print("=" * 60)

        print("\nSORTS:")
        for sort in self.sorts.values():
            print(f"  {sort.name}")

        print("\nMAPS:")
        for map_ in self.maps.values():
            print(
                f"  {map_.name}: "
                f"{map_.source.name} -> "
                f"{map_.target.name}"
            )

        print("\nCONES:")
        for cone in self.cones.values():

            kind = (
                "limit cone"
                if cone.is_limit
                else "cone"
            )

            print(
                f"  {cone.name}: "
                f"{kind}"
            )

            for leg in cone.legs:
                print(
                    f"      {leg.name}: "
                    f"{leg.source.name} -> "
                    f"{leg.target.name}"
                )

        print("\nEQUATIONS:")

        if not self.equations:
            print("  None")
        else:
            for equation in self.equations:
                print(
                    f"  {equation.left} = "
                    f"{equation.right}"
                )


# ============================================================
# PRODUCTS
# ============================================================

@dataclass
class Product:
    """
    A binary product specified by a limit cone.

        P --p1--> A
        |
        p2
        |
        v
        B

    """

    name: str
    left: Sort
    right: Sort
    object: Sort
    projection_left: Map
    projection_right: Map


def add_binary_product(
    sketch: Sketch,
    left: str,
    right: str,
    product_name: str
) -> Product:

    """
    Add a binary product A x B to the sketch.

    This creates:

        P -> A
        P -> B

    and declares the resulting cone to be a limit cone.
    """

    if left not in sketch.sorts:
        raise ValueError(
            f"Unknown sort '{left}'."
        )

    if right not in sketch.sorts:
        raise ValueError(
            f"Unknown sort '{right}'."
        )

    A = sketch.sorts[left]
    B = sketch.sorts[right]

    # Create the product sort
    P = sketch.add_sort(product_name)

    # Create projections
    p1 = sketch.add_map(
        name=f"pi_1_{product_name}",
        source=product_name,
        target=left
    )

    p2 = sketch.add_map(
        name=f"pi_2_{product_name}",
        source=product_name,
        target=right
    )

    # Declare the cone to be a limit cone
    sketch.add_cone(
        name=f"product_{product_name}",
        vertex=product_name,
        legs=(p1.name, p2.name),
        is_limit=True
    )

    return Product(
        name=product_name,
        left=A,
        right=B,
        object=P,
        projection_left=p1,
        projection_right=p2
    )


# ============================================================
# PRODUCT ELEMENTS
# ============================================================

@dataclass(frozen=True)
class Pair:
    """
    A formal element of a product.

        <a,b> : A x B
    """

    left: object
    right: object
    product: Product

    def __str__(self):
        return f"<{self.left}, {self.right}>"



def pair(
    product: Product,
    left_element,
    right_element
) -> Pair:

    """
    Construct the universal pairing

        <a,b> : A x B.
    """

    return Pair(
        left=left_element,
        right=right_element,
        product=product
    )


def project_left(p: Pair):
    """Apply the first projection."""
    return p.left


def project_right(p: Pair):
    """Apply the second projection."""
    return p.right


# ============================================================
# EXAMPLE
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Construct the sketch
    # --------------------------------------------------------

    S = Sketch()

    # Two basic sorts
    S.add_sort("A")
    S.add_sort("B")

    # --------------------------------------------------------
    # Add their binary product
    # --------------------------------------------------------

    AxB = add_binary_product(
        sketch=S,
        left="A",
        right="B",
        product_name="A_times_B"
    )

    # --------------------------------------------------------
    # Display the sketch
    # --------------------------------------------------------

    S.describe()

    # --------------------------------------------------------
    # Construct elements
    # --------------------------------------------------------

    a = "a"
    b = "b"

    x = pair(
        product=AxB,
        left_element=a,
        right_element=b
    )

    print("\nPRODUCT ELEMENT:")
    print(f"  x = {x}")

    # --------------------------------------------------------
    # Verify the projection equations
    # --------------------------------------------------------

    print("\nPROJECTIONS:")

    print(
        f"  {AxB.projection_left.name}(x) = "
        f"{project_left(x)}"
    )

    print(
        f"  {AxB.projection_right.name}(x) = "
        f"{project_right(x)}"
    )